# Outputs

Two Milestone 4 artifacts are tracked:

- `data_statistics.json` is the machine-readable validation report.
- `manual_inspection_100.md` is the deterministic 100-example train/development review packet.

Milestone 6 adds `dev_baselines.json`, containing complete development metrics for Random, BM25, and frozen BGE. The Colab teacher workflow stores `dev_teacher_comparison.json` in Google Drive after validating the development cache.

Regenerate both with `python src/data/validate_dataset.py --seed 42`. Run-specific metrics, checkpoints, logs, and final experiment tables remain ignored.
