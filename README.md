# finevid-distill

`finevid-distill` is a controlled FinQA evidence-ranking experiment. It asks:

> On FinQA report-level candidate sets, does teacher-score distillation improve BGE-small beyond ordinary hard-label fine-tuning?

**Answer: no.** On the locked 1,147-question test split, Hard-label BGE reaches 0.9342 MRR and Distilled BGE reaches 0.8469. Distillation improves the frozen encoder and slightly exceeds the teacher, but it is substantially weaker than ordinary supervised fine-tuning.

## Project objective

The experiment fixes every important choice before test evaluation:

| Item | Fixed choice |
| --- | --- |
| Dataset | FinQA |
| Retrieval pool | Every prose entry and table row in the question's report |
| Teacher | `Qwen/Qwen3-Reranker-0.6B` at revision `e61197e…` |
| Student | `BAAI/bge-small-en-v1.5` at revision `5c38ec7…` |
| Seed | 42 |
| Training row | All gold facts plus seeded same-report negatives, approximately eight candidates |
| Selection | Development MRR |
| Test use | Once, after checkpoint selection was frozen |

The full machine-readable contract is [`configs/beginner.yaml`](configs/beginner.yaml). Hard-label and distilled training use the same initialization, examples, candidate order, optimizer settings, training budget, and evaluator. Only their supervision differs.

## Teacher–student architecture

Qwen is a cross-encoder reranker: it reads each question–candidate pair and produces a raw yes-minus-no logit. BGE-small is a bi-encoder: it separately encodes the instructed question and uninstructed candidate, normalizes both embeddings, and scores their cosine-equivalent dot product.

```text
FinQA question + report candidates
             │
             ├── Qwen cross-encoder ── raw teacher scores ── softmax(· / 0.3)
             │                                                │
             └── BGE bi-encoder ── normalized cosine scores ── softmax(· / 0.05)
                                                              │
Hard-label target: equal probability over every gold fact ────┤
                                                              ▼
Hard model:      listwise cross-entropy
Distilled model: KL(teacher || student) + 0.1 × hard-label loss
```

Teacher tensors are detached, padding is excluded before softmax, KL is computed across candidates within each question, and probability/loss calculations use FP32. The query instruction is applied only to questions.

## Dataset construction

The official FinQA files are pinned to commit `0f16e2867befa6840783e58be38c9efb9229d742`. For every question, preprocessing creates:

- one `pre-text-N` candidate per `pre_text` entry;
- one `post-text-N` candidate per `post_text` entry;
- one `table-row-N` candidate per raw table row; and
- positive candidate IDs resolved exactly from `qa.gold_inds`.

The checked-in ranking pools preserve the official 6,251/883/1,147 train/dev/test question splits. Model inputs exclude answers, programs, executable answers, and raw annotations. The validator reconstructs every source candidate, checks 100% gold mapping, IDs, formatting, duplicates, leakage, split overlap, and deterministic hashes. The 100-example manual mapping review is saved in [`outputs/manual_inspection_100.md`](outputs/manual_inspection_100.md).

Both student treatments consume the same external `train_rows.jsonl`: 6,251 rows and 49,938 candidate occurrences, with every gold fact retained and candidate/teacher-score order verified. Its SHA-256 is `df56334db862a9e45504db7a1b0846c394e3e7fc9c1414dd89c101efa05a847e`.

## Development baselines

These results use all 883 development questions and the shared metric implementation:

| Model | Recall@1 | Recall@5 | MRR | NDCG@10 | CompleteRecall@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Random | 0.0470 | 0.2092 | 0.2115 | 0.2151 | 0.1200 |
| BM25 | 0.3542 | 0.7105 | 0.6355 | 0.6490 | 0.5776 |
| Frozen BGE | 0.4907 | 0.8435 | 0.7900 | 0.7987 | 0.7339 |
| Qwen teacher | 0.5021 | 0.8504 | 0.8041 | 0.8035 | 0.7407 |

Qwen passed the predeclared teacher gate by outperforming Frozen BGE on development MRR. Results are stored in [`outputs/dev_baselines.json`](outputs/dev_baselines.json) and [`outputs/dev_teacher_comparison.json`](outputs/dev_teacher_comparison.json).

## Final results

Development selection chose hard-label epoch 3 and distilled epoch 2. [`outputs/final_selection.json`](outputs/final_selection.json) was frozen before public-test access.

| Model | Recall@1 | Recall@5 | MRR | NDCG@10 | CompleteRecall@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Random | 0.0459 | 0.2060 | 0.2030 | 0.2119 | 0.1255 |
| BM25 | 0.3516 | 0.6997 | 0.6194 | 0.6362 | 0.5789 |
| Frozen BGE | 0.5035 | 0.8315 | 0.7871 | 0.7893 | 0.7140 |
| **Hard-label BGE** | **0.6509** | **0.9362** | **0.9342** | **0.9162** | **0.8684** |
| Distilled BGE | 0.5690 | 0.8552 | 0.8469 | 0.8285 | 0.7350 |
| Qwen teacher | 0.5395 | 0.8363 | 0.8136 | 0.8020 | 0.7184 |

Distilled-minus-Hard MRR is **−0.0873**, so the predeclared decision rule answers **no**. Distillation still adds 0.0598 MRR over Frozen BGE. Its NDCG@10 divided by teacher NDCG@10 is 1.033, or 103.3% teacher quality retained. The exact result is [`outputs/final_test_results.json`](outputs/final_test_results.json).

## Efficiency comparison

Both models were benchmarked sequentially on the same Tesla T4. Timings are medians of five measured runs after two warm-ups. BGE's one-time 100-candidate embedding precomputation is reported separately.

| Model | NDCG@10 | Parameters | Model size | Peak GPU memory | Query latency | Rank 100 | Candidates/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen teacher | 0.8020 | 595.8M | 1,136 MiB | 2,068 MiB | 120.6 ms | 7,516.5 ms | 13.3 |
| Distilled BGE | 0.8285 | 33.4M | 127 MiB | 294 MiB | 9.5 ms | 10.0 ms | 10,041.8 |

Distilled BGE has 17.9× fewer parameters, uses about 7× less peak GPU memory, and ranks 100 pre-encoded candidates about 755× faster. Candidate precomputation took 211.5 ms. Full measurements are in [`outputs/efficiency_results.json`](outputs/efficiency_results.json).

## Example success and failure cases

**Hard-label success — multi-fact retrieval.** For “what percentage of 2005 industrial packaging sales are containerboard sales?”, Hard-label BGE ranks the report sales denominator first and containerboard sales second. Frozen and Distilled BGE place the denominator eighth; Qwen places it twelfth. Direct gold supervision learned to retrieve the generic total needed alongside the named numerator.

**Distillation failure — inherited teacher preference.** For the 2004 money-pool percentage question, Hard-label BGE ranks all three annotated facts in its top three. Qwen puts the numeric receivables row ninth and Distilled BGE puts it twelfth, while both emphasize related prose. Six of the 20 sampled distilled failures show this teacher–student miss with a hard-label success.

**Evaluation failure — annotation noise.** One pension-liability question includes an unrelated CDO sentence as gold evidence. Every model retrieves the numeric pension row first but fails `CompleteRecall@5` because the unrelated sentence is absent. Overall, 46 of 80 reviewed failures contain redundant, irrelevant, or internally inconsistent annotations.

The complete 80-case audit is [`outputs/error_analysis.csv`](outputs/error_analysis.csv); findings and failure counts are summarized in [`docs/error_analysis.md`](docs/error_analysis.md).

## Artifact storage

Source, tests, processed ranking pools, aggregate results, and error analysis are tracked in Git. Generated teacher caches, shared training rows, and checkpoint directories are stored outside ordinary Git history because they are large and include optimizer state.

```text
FinEvid-Distill/
├── processed_data/train_rows.jsonl
├── teacher_scores/
│   ├── teacher_train_scores.jsonl
│   ├── teacher_dev_scores.jsonl
│   └── teacher_test_scores.jsonl
└── checkpoints/
    ├── hard_label_student_tau005/   # selected epoch 3
    └── distilled_student/           # selected epoch 2
```

[`artifacts/manifest.json`](artifacts/manifest.json) records tracked hashes, external paths, cache hashes, and selected models. Run `python src/evaluation/audit_repository.py --artifact-root /path/to/FinEvid-Distill` to validate candidate ordering, training-row identity, complete run metadata, and selected checkpoint directories.

## Reproduction commands

Python 3.10 or newer is required.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python src/data/download_finqa.py
python src/data/build_dataset.py --seed 42
python src/data/validate_dataset.py --seed 42
pytest
python -m finevid_distill.environment --config configs/beginner.yaml
python src/evaluation/evaluate.py --models random,bm25,bge
python src/evaluation/audit_repository.py
```

Create the shared rows after teacher scoring:

```bash
python src/data/build_training_rows.py \
  --teacher-cache /path/to/FinEvid-Distill/teacher_scores/teacher_train_scores.jsonl \
  --output /path/to/FinEvid-Distill/processed_data/train_rows.jsonl
```

GPU work is organized into thin Colab notebooks that call the tested scripts:

1. [`notebooks/02_colab_teacher.ipynb`](notebooks/02_colab_teacher.ipynb) caches Qwen train/dev scores and applies the teacher gate.
2. [`notebooks/04_colab_distilled.ipynb`](notebooks/04_colab_distilled.ipynb) trains the matched hard-label and distilled students and saves resumable checkpoints.
3. [`notebooks/05_colab_final_evaluation.ipynb`](notebooks/05_colab_final_evaluation.ipynb) freezes selection, caches test teacher scores, runs the six-model test comparison, and benchmarks efficiency.
4. [`notebooks/06_colab_error_analysis.ipynb`](notebooks/06_colab_error_analysis.ipynb) regenerates rankings and samples the post-test failure-review packet.

With the external artifacts available, reproduce the final table in one command:

```bash
python src/evaluation/final_comparison.py \
  --selection outputs/final_selection.json \
  --teacher-cache /path/to/FinEvid-Distill/teacher_scores/teacher_test_scores.jsonl \
  --hard-dir /path/to/FinEvid-Distill/checkpoints/hard_label_student_tau005 \
  --distilled-dir /path/to/FinEvid-Distill/checkpoints/distilled_student \
  --device cuda \
  --output reproduced_final_test_results.json
```

## Limitations

- This is one seed, one dataset, one teacher, one student, and one training budget; it is not a general distillation benchmark.
- Training distills over approximately eight sampled candidates per question, while evaluation ranks the full report pool.
- At teacher temperature 0.3, 70.7% of training rows place over 99% probability on one candidate, limiting the information in the soft distribution.
- Qwen only narrowly beats Frozen BGE on development and is much weaker than Hard-label BGE on test, constraining what it can teach.
- Strict candidate-ID `CompleteRecall@5` penalizes semantically duplicate and irrelevant gold annotations; 46/80 reviewed failures were annotation-driven.
- Efficiency numbers come from one Tesla T4 and will vary by hardware and software version.
- No confidence intervals or multi-seed significance estimates are reported.

## Planned intermediate extensions

1. Audit and merge semantically equivalent gold candidates, then report both original and equivalence-aware complete recall.
2. Repeat the fixed comparison over multiple seeds and attach confidence intervals to treatment differences.
3. Replace uniform negatives with deterministic hard negatives while keeping identical rows across treatments.
4. Distill over larger or full-report candidate sets to reduce the train/evaluation pool mismatch.
5. Pre-register a small development-only study of teacher temperature and hard-label weight before any new test evaluation.
6. Improve table-row context and test a stronger teacher only as separately named experiments, leaving this beginner result unchanged.
