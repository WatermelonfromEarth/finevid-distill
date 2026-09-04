# Outputs

Two Milestone 4 artifacts are tracked:

- `data_statistics.json` is the machine-readable validation report.
- `manual_inspection_100.md` is the deterministic 100-example train/development review packet.

Milestone 6 adds `dev_baselines.json`, containing complete development metrics for Random, BM25, and frozen BGE. Milestone 7 adds the small tracked `dev_teacher_comparison.json` after validating the complete development cache; full score caches remain outside Git.

Milestone 9 writes `checkpoints/hard_label_student/`. Each immutable epoch directory contains the saved model, optimizer/scheduler/scaler and RNG state, plus epoch metrics. `latest.json` and `best.json` point to resumable and selected checkpoints, `training_history.json` tracks all requested signals, and `best_reload_verification.json` proves the selected model was reloaded and reevaluated successfully. These run artifacts remain ignored.

Regenerate both with `python src/data/validate_dataset.py --seed 42`. Run-specific metrics, checkpoints, logs, and final experiment tables remain ignored.
