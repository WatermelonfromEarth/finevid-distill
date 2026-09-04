# finevid-distill

`finevid-distill` is a deliberately small retrieval-distillation experiment. It answers one question:

> On FinQA report-level candidate sets, does teacher-score distillation improve BGE-small beyond ordinary hard-label fine-tuning?

This repository starts with an experiment contract and a reproducible Python environment. Later milestones may implement data preparation, scoring, training, and evaluation, but they must not silently change the contract below.

## Experiment contract

| Item | Fixed choice |
|---|---|
| Dataset | FinQA |
| Candidate-pool scope | All evidence entries in the question's FinQA report |
| Candidate unit | One `pre_text` entry, `post_text` entry, or table row |
| Teacher | `Qwen/Qwen3-Reranker-0.6B` |
| Student | `BAAI/bge-small-en-v1.5` |
| Random seed | `42` |
| Training candidate set | Approximately 8 evidence candidates per question: all labelled positives plus within-report BM25 hard negatives |
| Development split | Used for implementation checks, hyperparameter choices, and selection of the final configuration |
| Test split | Kept untouched until the final configuration has been selected; used once for the final comparison |

The machine-readable source of truth is [`configs/beginner.yaml`](configs/beginner.yaml). Tests fail if its core contract drifts from these choices.

## Required experiment table

Every final result table must contain all five rows. The two trained student rows use the same BGE-small architecture, candidate sets, seed, training budget, and evaluation code; only their supervision differs.

| System | Training or scoring signal | Role |
|---|---|---|
| BM25 | Lexical BM25 score; no neural training | Lexical baseline and hard-negative source |
| Frozen BGE-small | Off-the-shelf BGE-small similarity; no fine-tuning | Pretrained student baseline |
| Hard-label BGE-small | One-hot FinQA relevance labels | Ordinary fine-tuning baseline |
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

Use development MRR to make configuration decisions. After selecting one final configuration, evaluate all five systems on the test set and report every metric plus the absolute Distilled-minus-Hard delta. The beginner experiment answers “yes” only when the final distilled student's test MRR is greater than the final hard-label student's test MRR; the size of the delta and all secondary metrics must still be shown.

## Scope restrictions

- Do not substitute another dataset, teacher, student, seed, or retrieval unit in this beginner experiment.
- Do not tune on, inspect per-example errors from, or repeatedly evaluate the test split before configuration selection is complete.
- Do not omit any of the five required systems from the final report.
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

## Milestone status

- [x] Milestone 0: experiment question, comparisons, metrics, and restrictions are fixed.
- [x] Milestone 1: installable project structure, dependency specification, environment report, and smoke tests are present.
- [x] Milestone 2: the executable FinQA inspection notebook documents the raw schema and evidence mappings without loading test examples.
- [x] Milestone 3: the official FinQA splits are converted to deterministic, fully mapped ranking pools.
- [x] Milestone 4: strict validation passes and all 100 train/development audit examples have been manually reviewed.
- [x] Milestone 5: shared metrics agree with hand-calculated single- and multi-positive cases, including stable score ties.
- [x] Milestone 6: Random, BM25, and frozen BGE baselines are evaluated on all 883 development questions.
- [ ] Milestone 7: teacher scoring and cache validation are implemented; run the Colab GPU notebook to produce both full caches and decide the development gate.
- [ ] Training and experiment execution are intentionally deferred to later milestones.
