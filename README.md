# finevid-distill

`finevid-distill` is a deliberately small retrieval-distillation experiment. It answers one question:

> On FinQA report-level candidate sets, does teacher-score distillation improve BGE-small beyond ordinary hard-label fine-tuning?

**Answer: no.** On the locked 1,147-question test split, distilled BGE reaches MRR 0.846864, while the matched hard-label BGE reaches 0.934211 (Distilled minus Hard = -0.087347). Distillation improves substantially over frozen BGE, but ordinary hard-label fine-tuning is the stronger student treatment under this fixed experiment.

The repository fixes the experiment contract, materializes one shared training set for both student treatments, and keeps modelling and evaluation logic reproducible. Later work must not silently change the contract below.

## Experiment contract

| Item | Fixed choice |
|---|---|
| Dataset | FinQA |
| Candidate-pool scope | All evidence entries in the question's FinQA report |
| Candidate unit | One `pre_text` entry, `post_text` entry, or table row |
| Teacher | `Qwen/Qwen3-Reranker-0.6B` |
| Student | `BAAI/bge-small-en-v1.5` |
| Random seed | `42` |
| Training candidate set | Approximately 8 evidence candidates per question: all labelled positives plus seeded uniform negatives sampled without replacement from the same report |
| Development split | Used for implementation checks, hyperparameter choices, and selection of the final configuration |
| Test split | Kept untouched until the final configuration has been selected; used once for the final comparison |

The machine-readable source of truth is [`configs/beginner.yaml`](configs/beginner.yaml). Tests fail if its core contract drifts from these choices.

## Required experiment table

Every final result table must contain all six rows. The two trained student rows use the same BGE-small architecture, candidate sets, seed, training budget, and evaluation code; only their supervision differs.

| System | Training or scoring signal | Role |
|---|---|---|
| Random | Seeded random ranking | Sanity check |
| BM25 | Lexical BM25 score; no neural training | Lexical baseline |
| Frozen BGE-small | Off-the-shelf BGE-small similarity; no fine-tuning | Pretrained student baseline |
| Hard-label BGE-small | Equal-mass distribution over all FinQA gold labels | Ordinary fine-tuning baseline |
| Distilled BGE-small | Soft target distribution made from the frozen Qwen teacher scores | Treatment under test |
| Qwen teacher | Frozen Qwen reranker score | Teacher reference comparison |

The primary comparison is **Distilled BGE-small versus Hard-label BGE-small**. BM25, frozen BGE-small, and the Qwen teacher provide context; they do not replace the primary comparison.

## Metrics and decision rule

Evidence candidates are sorted from highest to lowest score. A question can have more than one labelled positive; rank is therefore based on its highest-ranked positive candidate.

| Metric | Definition | Use |
|---|---|---|
| MRR | Mean reciprocal rank of the first labelled positive candidate | Primary metric |
| Recall@1 | Per-question fraction of all gold facts in the top 1, macro-averaged | Secondary metric |
| Recall@5 | Per-question fraction of all gold facts in the top 5, macro-averaged | Secondary metric |
| NDCG@10 | Binary-relevance DCG at 10 divided by the ideal DCG for all gold facts | Secondary metric |
| CompleteRecall@5 | Fraction of questions for which every gold fact is in the top 5 | Secondary metric |

Use development MRR to make configuration decisions. After selecting one final configuration, evaluate all six systems on the test set and report every metric plus the absolute Distilled-minus-Hard delta. The beginner experiment answers “yes” only when the final distilled student's test MRR is greater than the final hard-label student's test MRR; the size of the delta and all secondary metrics must still be shown.

## Scope restrictions

- Do not substitute another dataset, teacher, student, seed, or retrieval unit in this beginner experiment.
- Do not tune on, inspect per-example errors from, or repeatedly evaluate the test split before configuration selection is complete.
- Do not omit any of the six required systems from the final report.
- Do not give the distilled student extra data, candidate sets, optimizer steps, or evaluation treatment that the hard-label student does not receive.
- Teacher-score distillation means soft supervision derived from the fixed Qwen teacher's scores over the same candidate set. It is not pseudo-label filtering or extra teacher-generated text.
- Keep report text construction and candidate-set construction identical across systems. Cache candidates and teacher scores so each comparison sees the same examples.
- Record any unavoidable implementation deviation in the README and config before running the test set. A changed model or dataset is a different experiment, not a beginner-run variation.

## Project layout

```text
finevid-distill/
├── configs/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── outputs/
├── src/finevid_distill/
│   ├── data/
│   ├── evaluation/
│   ├── models/
│   └── training/
├── tests/
├── README.md
├── requirements.txt
└── pyproject.toml
```

The three deterministic ranking datasets and their validation artifacts are checked in. Raw FinQA downloads, model checkpoints, and other run-specific outputs remain ignored.

## Environment setup

Python 3.10 or newer is required. From the repository root on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the checks:

```powershell
python -m pytest
python -m finevid_distill.environment --config configs/beginner.yaml
```

The second command prints the requested device, the device actually selected from the available hardware, and the installed versions of the core packages.

Execute the FinQA inspection notebook from the repository root with:

```powershell
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_inspect_finqa.ipynb
```

## Ranking dataset

Build the evidence-ranking pools from the pinned official FinQA splits:

```powershell
python src/data/build_dataset.py --seed 42
```

Each question retains every evidence unit in its report. Candidate IDs are deterministic within the report: `pre-text-N` for `pre_text[N]`, `post-text-N` for `post_text[N]`, and `table-row-N` for `table[N]`. Table rows use `column: value` pairs after the row label; the header row is joined verbatim with ` | `. The full pools are materialized here even though the later training milestone will select approximately eight candidates per question.

Each JSONL record has the following model-input fields only: `question_id`, `report_id`, `question`, `candidates`, and `positive_candidate_ids`. Answers, executable answers, programs, and raw gold annotations are excluded. The original annotations are loaded separately by validation and are never model inputs.

## Dataset validation

Run the strict validation and regenerate its review packet:

```powershell
python src/data/validate_dataset.py --seed 42
```

The validator reconstructs every expected candidate from the raw source, checks all gold mappings, split membership and ordering, IDs, empty values, table formatting, leakage, count anomalies, duplicates, and cross-split overlap. It also rebuilds the complete dataset in a temporary directory and compares file hashes to prove deterministic regeneration.

The retained duplicate-text and candidate-count findings in `outputs/data_statistics.json` are diagnostics, not dropped examples: the construction contract requires every source entry. Exact question/report ID overlap is fatal; repeated generic question wording across different reports is recorded separately. Natural answer strings can legitimately occur in source evidence, so the leakage gate is based on prohibited fields, program literals, exact answer-as-candidate values, and exact source provenance.

The fixed 100-example review packet is `outputs/manual_inspection_100.md`. It is sampled deterministically from train and development only, leaving test examples uninspected. After actually reviewing all 100 mappings, record that fact explicitly with:

```powershell
python src/data/validate_dataset.py --seed 42 --manual-review-complete
```

## Shared ranking metrics

All rankers call `src/finevid_distill/evaluation/metrics.py`. Scores are sorted descending, and exact ties preserve original candidate order. MRR uses the first gold fact; Recall@k gives partial credit when only some required facts are retrieved; CompleteRecall@5 is one only when every required fact is present.

Run the hand-calculated metric tests with:

```powershell
python -m pytest tests/test_metrics.py
```

## Development baselines

One command evaluates all non-trained systems on development only:

```powershell
python src/evaluation/evaluate.py --models random,bm25,bge
```

Frozen BGE prefixes questions with the model's official `Represent this sentence for searching relevant passages: ` instruction, leaves candidates unprefixed, normalizes both embedding sets, and ranks by their cosine-equivalent dot product. Model revisions are pinned in `configs/beginner.yaml`.

| Model | Recall@1 | Recall@5 | MRR | NDCG@10 | CompleteRecall@5 |
|---|---:|---:|---:|---:|---:|
| Random | 0.047019 | 0.209237 | 0.211481 | 0.215148 | 0.120045 |
| BM25 | 0.354237 | 0.710526 | 0.635527 | 0.649003 | 0.577576 |
| Frozen BGE | 0.490718 | 0.843458 | 0.789972 | 0.798706 | 0.733862 |

These are the complete 883-question development results stored in `outputs/dev_baselines.json`. No test ranking was run.

## Qwen teacher cache and GPU gate

Qwen scoring requires a CUDA-capable runtime for this experiment. The local teacher command fails fast on CPU because the present machine lacks native BF16 and measured throughput is impractical. Open `notebooks/02_colab_teacher.ipynb` in a GPU Colab runtime. It clones the private GitHub repository into `/content/finevid-distill` for fast execution and writes persistent artifacts under `/content/drive/MyDrive/FinEvid-Distill`.

Before the first run, add a read-only fine-grained GitHub token named `GITHUB_TOKEN` through Colab's key icon. The notebook removes the authenticated URL from the clone immediately after checkout so the token is not retained as the Git remote. Colab uses `requirements-colab.txt`, which deliberately does not reinstall or replace Colab's CUDA-enabled PyTorch.

The notebook:

1. reproduces the non-trained development baselines;
2. writes and strictly validates `teacher_dev_scores.jsonl`;
3. compares Qwen with frozen BGE through the shared metrics;
4. stops if Qwen development MRR is not greater than frozen BGE MRR; and
5. writes `teacher_train_scores.jsonl` only after that gate passes.

Each cache line preserves processed candidate order and stores finite raw yes-minus-no logit differences with `temperature_applied: false`. Partial files resume at the next complete question after a Colab disconnect; an interrupted final write is discarded while all earlier validated rows are retained. If the teacher gate fails, do not train: inspect the financial retrieval instruction, table serialization, and truncation first.

The complete caches were produced and independently validated against the checked-in processed splits. On all 883 development questions, Qwen passed the required quality gate:

| Model | Recall@1 | Recall@5 | MRR | NDCG@10 | CompleteRecall@5 |
|---|---:|---:|---:|---:|---:|
| Frozen BGE | 0.490718 | 0.843458 | 0.789972 | 0.798706 | 0.733862 |
| Qwen teacher | 0.502096 | 0.850445 | 0.804112 | 0.803492 | 0.740657 |

The full comparison is tracked in `outputs/dev_teacher_comparison.json`; the large score caches remain in persistent artifact storage and are intentionally excluded from Git.

## Fixed shared training rows

Build the single file consumed by both hard-label and distilled training:

```powershell
python src/data/build_training_rows.py `
  --teacher-cache path/to/teacher_train_scores.jsonl `
  --output data/processed/train_rows.jsonl
```

For every training question, the builder retains all gold candidates, uniformly samples negatives without replacement from the same report until the row is approximately eight candidates, and applies a per-question seed-42 shuffle. It joins candidate text and raw teacher scores by candidate ID, then validates every output field against both source files. Hard-label training ignores the stored teacher scores; the later distilled treatment must read the same rows and ordering.

The complete seed-42 artifact contains 6,251 rows and 49,938 candidate occurrences (minimum 6, maximum 9, mean 7.988802). Its SHA-256 is `df56334db862a9e45504db7a1b0846c394e3e7fc9c1414dd89c101efa05a847e`. The generated JSONL contains teacher outputs and is therefore ignored by Git along with the full caches.

## Hard-label BGE-small training

`src/training/train_hard_labels.py` trains BGE-small with normalized query and candidate embeddings. Questions retain the official BGE query instruction; candidates remain uninstructed. Within each fixed row, the target distribution assigns equal probability to every gold candidate and zero to every negative. The matched experiment uses listwise cross-entropy over cosine scores divided by student temperature **0.05**.

The current GPU entry point is `notebooks/04_colab_distilled.ipynb`, which runs both matched treatments. The earlier `03_colab_hard_label.ipynb` documents the original temperature-1 run. For the new control, run:

```powershell
python src/training/train_hard_labels.py `
  --train-rows data/processed/train_rows.jsonl `
  --dev-data data/processed/dev.jsonl `
  --device cuda
```

The new default output is `outputs/checkpoints/hard_label_student_tau005/`, preserving `hard_label_student/`. Each completed epoch records loss components, development metrics, learning rate, mean pre-clipping gradient norm, optimizer steps, FP16 loss-scale overflow retries, and elapsed time. Its checkpoint contains the Sentence Transformers model, optimizer, scheduler, gradient-scaler and Python/NumPy/PyTorch RNG states. A scaled FP16 overflow backs the loss scale off and retries the same batch without advancing the optimizer or scheduler; a genuinely non-finite unscaled gradient still aborts before any update. Completed epoch directories are published atomically; on `--resume`, their records reconstruct the latest/best pointers and history if a disconnect interrupted those writes. Incomplete directories are preserved under an `.abandoned-*` name and never loaded. At completion the best model is loaded from disk and reevaluated; training fails if the reloaded development metrics change.

Resume requires identical configuration, data hashes, and implementation hash. The sole exception is a trainer-code update before the first checkpoint: the uncheckpointed attempt is restarted from the fixed seed and its previous metadata is preserved under `abandoned_runs/`. A legacy temperature-1 run cannot be resumed through the new trainer; retain its original artifacts and use a separate output directory for the matched experiment.

Trained checkpoints can also be evaluated directly through the same command and metric implementation as every baseline:

```powershell
python src/evaluation/evaluate.py `
  --models checkpoint `
  --checkpoint outputs/checkpoints/hard_label_student_tau005/epochs/epoch-001/model `
  --checkpoint-label "Hard-label BGE-small" `
  --output outputs/hard_label_dev.json
```

Only development evaluation is available during training. The test split remains untouched.

## Original hard-label run (temperature 1)

The downloaded Colab records, now tracked under `outputs/hard_label_run/`, confirm all three epochs completed on 6,251 training and 883 development questions, with 782 optimizer steps per epoch (2,346 total). Both dataset hashes match the checked-in development pool and shared training rows. Epoch 1 was selected by development MRR and its reloaded metrics match exactly. These are historical results, not the matched-temperature control for Milestone 10.

| Epoch | Training loss | Development MRR | Recall@5 |
|---|---:|---:|---:|
| 1 (selected) | 1.532174 | 0.762280 | 0.806505 |
| 2 | 1.409886 | 0.739014 | 0.803438 |
| 3 | 1.381780 | 0.748393 | 0.813300 |

Frozen BGE development MRR is 0.789972. The original fine-tuning run therefore reduced MRR by 0.027693. This motivates checking initial-model evaluation and using an identically scaled hard-label control; it does not establish the cause of the regression.

## Milestone 10: distilled student and matched control

Both treatments start independently from the pinned pretrained BGE revision, consume the same shared rows, and use the same student temperature, seed, learning rate, schedule, batching, maximum sequence length, and training budget. The temperature-1 result remains an earlier diagnostic comparison. Changing student temperature for only the distilled model would confound the supervision comparison.

For each question's valid candidates:

```text
p_teacher = softmax(detached_raw_teacher_scores / 0.3)
log_p_student = log_softmax(normalized_cosine_scores / 0.05)
gold_target = positive_mask / sum(positive_mask)
L_KL = sum(p_teacher * (log(p_teacher) - log_p_student))
L_hard = -sum(gold_target * log_p_student)
L_distilled = mean_questions(L_KL + 0.1 * L_hard)
L_control = mean_questions(L_hard)
```

No additional temperature-squared multiplier is applied. Probability and loss calculations use FP32. Valid candidates are selected before softmax; padded positions cannot affect normalization or gradients. The teacher is detached. Genuinely non-finite valid scores, losses, or unscaled gradients stop training before the optimizer update; recoverable FP16 loss-scale overflow instead lowers the scale and retries without dropping the batch. KL is summed along each row's candidate dimension and averaged equally across questions. The shared trainer retains question-only BGE instructions and normalized embeddings.

This transfers the teacher distribution over each approximately eight-candidate training row, not the full report pool. The full report pool remains the evaluation scope. At teacher temperature 0.3, 70.7% of the 6,251 cached training rows assign over 99% probability to one candidate. The trainer logs teacher entropy and top probability alongside unweighted KL, hard CE, and weighted total loss. Keep these starting settings fixed until the pipeline is complete.

Run the distilled treatment:

```powershell
python src/training/train_distilled.py `
  --train-rows data/processed/train_rows.jsonl `
  --dev-data data/processed/dev.jsonl `
  --device cuda
```

Its default directory is `outputs/checkpoints/distilled_student/`. Before training, each run writes `initial_development.json` using the same evaluator as checkpoint selection. Each run writes a hashed `run_config.json`, epoch metrics and checkpoints, `training_history.json`, `latest.json`, `best.json`, and `best_reload_verification.json`. CPU diagnostics require explicit `--allow-cpu --mixed-precision none --limit-train N --limit-dev N`; their verification records are marked `diagnostic_run: true`.

After both full runs finish:

```powershell
python src/evaluation/compare_students.py `
  --hard-dir outputs/checkpoints/hard_label_student_tau005 `
  --distilled-dir outputs/checkpoints/distilled_student `
  --output outputs/dev_student_comparison.json
```

The comparison checks matching controls and initial metrics, complete epoch/step budgets, best-by-MRR selection, and consistent reload verification. It reports every development metric and the Distilled-minus-Hard differences. Diagnostic runs are rejected unless explicitly allowed; they are never labelled as full experiments. This is a development comparison, not final test evidence or a significance claim.

The complete seed-42 GPU runs selected hard-label epoch 3 (development MRR 0.926379) and distilled epoch 2 (development MRR 0.840338). Both checkpoints reloaded exactly. `outputs/final_selection.json` records these decisions, input and implementation hashes, the public-test file hash, and the prohibition on further hyperparameter search. It was frozen before public-test scoring.

## Milestone 11: locked final comparison

Public-test teacher scoring is disabled unless the frozen selection validates against both complete student run directories. Once frozen, cache the test teacher logits resumably:

```powershell
python src/data/cache_teacher_scores.py `
  --splits test `
  --processed-dir data/processed `
  --output-dir path/to/teacher_scores `
  --final-selection outputs/final_selection.json `
  --hard-dir path/to/checkpoints/hard_label_student_tau005 `
  --distilled-dir path/to/checkpoints/distilled_student `
  --device cuda
```

One command then reproduces the six-model test table from the saved selected checkpoints and raw teacher cache:

```powershell
python src/evaluation/final_comparison.py `
  --selection outputs/final_selection.json `
  --test-data data/processed/test.jsonl `
  --teacher-cache path/to/teacher_scores/teacher_test_scores.jsonl `
  --hard-dir path/to/checkpoints/hard_label_student_tau005 `
  --distilled-dir path/to/checkpoints/distilled_student `
  --device cuda `
  --output outputs/final_test_results.json
```

The command validates the fixed 1,147-question test SHA-256, checkpoint provenance, development selection, teacher candidate ordering, and all six result rows. It reports `Distilled BGE NDCG@10 / Qwen teacher NDCG@10` as teacher quality retained and answers the primary MRR comparison directly.

### Final test result

| Model | Recall@1 | Recall@5 | MRR | NDCG@10 | CompleteRecall@5 |
|---|---:|---:|---:|---:|---:|
| Random | 0.045851 | 0.205950 | 0.202991 | 0.211930 | 0.125545 |
| BM25 | 0.351591 | 0.699666 | 0.619426 | 0.636191 | 0.578901 |
| Frozen BGE | 0.503545 | 0.831495 | 0.787082 | 0.789331 | 0.714037 |
| Hard-label BGE | **0.650908** | **0.936225** | **0.934211** | **0.916221** | **0.868352** |
| Distilled BGE | 0.568999 | 0.855246 | 0.846864 | 0.828457 | 0.734961 |
| Qwen teacher | 0.539509 | 0.836254 | 0.813630 | 0.802022 | 0.718396 |

Distilled minus Hard MRR is -0.087347, so the predeclared decision rule answers **no**. Distillation does improve over frozen BGE by 0.059782 MRR. Teacher quality retained is 1.032961 (103.30%): the distilled student's NDCG@10 exceeds the teacher's, even though it remains well below the hard-label student's NDCG@10.

## Milestone 12: same-hardware efficiency benchmark

After final quality evaluation, benchmark Qwen and the selected distilled checkpoint in one process on one CUDA device:

```powershell
python src/evaluation/benchmark_efficiency.py `
  --selection outputs/final_selection.json `
  --test-data data/processed/test.jsonl `
  --quality-results outputs/final_test_results.json `
  --hard-dir path/to/checkpoints/hard_label_student_tau005 `
  --distilled-dir path/to/checkpoints/distilled_student `
  --device cuda `
  --output outputs/efficiency_results.json
```

The deterministic benchmark sample contains 100 unique processed FinQA candidates. It reports parameter count, parameter-and-buffer bytes, peak allocated CUDA memory, median candidate precomputation time, query latency, online rank-100 latency, and candidates per second. BGE candidate embeddings are normalized and precomputed; that cost is reported separately. Qwen cannot precompute query-independent candidate embeddings, so its rank-100 timing cross-encodes all pairs. The resulting table combines test NDCG@10 with efficiency.

### Quality–efficiency result

All timings are medians from five measured runs after warm-up on the same Tesla T4.

| Model | Test NDCG@10 | Parameters | Model MiB | Peak GPU MiB | Candidate precompute | Query latency | Rank 100 | Candidates/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen teacher | 0.802022 | 595,776,512 | 1,136.35 | 2,067.97 | n/a | 120.628 ms | 7,516.459 ms | 13.30 |
| Distilled BGE | 0.828457 | 33,360,000 | 127.27 | 293.83 | 211.501 ms | 9.473 ms | 9.958 ms | 10,041.79 |

With candidate embeddings precomputed, distilled BGE ranks 100 candidates about 755 times faster, uses about 7 times less peak GPU memory, and has about 17.9 times fewer parameters. Its one-time 100-candidate precomputation cost is reported separately and is not included in the online rank-100 latency.

### Running in Colab without publishing local changes

Build a portable source bundle from the repository root:

```powershell
python scripts/package_colab.py --output outputs/finevid_milestone10_source.zip
```

Open `notebooks/04_colab_distilled.ipynb` in Colab, select a GPU runtime, and run its cells in order. Upload that bundle when prompted. The notebook verifies its manifest, installs the bundled source, tests it, rebuilds shared rows from the existing Drive teacher cache, trains both treatments, validates the comparison, and downloads a small review ZIP. The bundle contains source and train/development inputs; it omits credentials, raw data, teacher caches, model checkpoints, and the test ranking file. Existing teacher caches must remain under `MyDrive/FinEvid-Distill/teacher_scores/`.

For the final comparison and benchmark, create the separately gated bundle only after `outputs/final_selection.json` is frozen:

```powershell
python scripts/package_colab.py `
  --include-final-test `
  --output outputs/finevid_final_source.zip
```

Open `notebooks/05_colab_final_evaluation.ipynb`, upload that final bundle, and run its cells in order. Qwen test scoring is resumable. The final evaluator releases Qwen before loading BGE, and the benchmark loads the two models sequentially.

## Milestone status

- [x] Milestone 0: experiment question, comparisons, metrics, and restrictions are fixed.
- [x] Milestone 1: installable project structure, dependency specification, environment report, and smoke tests are present.
- [x] Milestone 2: the executable FinQA inspection notebook documents the raw schema and evidence mappings without loading test examples.
- [x] Milestone 3: the official FinQA splits are converted to deterministic, fully mapped ranking pools.
- [x] Milestone 4: strict validation passes and all 100 train/development audit examples have been manually reviewed.
- [x] Milestone 5: shared metrics agree with hand-calculated single- and multi-positive cases, including stable score ties.
- [x] Milestone 6: Random, BM25, and frozen BGE baselines are evaluated on all 883 development questions.
- [x] Milestone 7: complete training/development teacher caches validate, and Qwen development MRR 0.804112 exceeds frozen BGE MRR 0.789972.
- [x] Milestone 8: one deterministic 6,251-row artifact retains every gold fact and exactly aligns candidate, label, text, and teacher-score order.
- [x] Milestone 9: the original temperature-1 hard-label GPU run completed all three epochs; its best checkpoint was reloaded and verified.
- [x] Milestone 10: both matched GPU treatments completed all epochs; hard-label epoch 3 and distilled epoch 2 were reloaded, compared, and frozen.
- [x] Milestone 11: the locked six-model comparison completed on all 1,147 test questions and answers the research question.
- [x] Milestone 12: Qwen and distilled BGE were benchmarked sequentially on the same Tesla T4 and the quality–efficiency table is saved.
