# Outputs

Two Milestone 4 artifacts are tracked:

- `data_statistics.json` is the machine-readable validation report.
- `manual_inspection_100.md` is the deterministic 100-example train/development review packet.

Milestone 6 adds `dev_baselines.json`, containing complete development metrics for Random, BM25, and frozen BGE. Milestone 7 adds the small tracked `dev_teacher_comparison.json` after validating the complete development cache; full score caches remain outside Git.

Milestone 9 writes `checkpoints/hard_label_student/`. Each immutable epoch directory contains the saved model, optimizer/scheduler/scaler and RNG state, plus epoch metrics. `latest.json` and `best.json` point to resumable and selected checkpoints, `training_history.json` tracks all requested signals, and `best_reload_verification.json` proves the selected model was reloaded and reevaluated successfully. These run artifacts remain ignored.

The small JSON records from the completed original temperature-1 hard-label run are tracked under `hard_label_run/`. They preserve its configuration, full three-epoch history, latest/best pointers, and reload verification. Model weights and optimizer state remain in external artifact storage.

Milestone 10 writes the matched control to `checkpoints/hard_label_student_tau005/`, the treatment to `checkpoints/distilled_student/`, and their validated development comparison to `dev_student_comparison.json`. Commit the small comparison and run metadata only after both full runs finish; keep checkpoint weights outside ordinary Git history.

`final_selection.json` is the tracked pre-test freeze record. It selects hard-label epoch 3 and distilled epoch 2 from complete development runs and locks the public-test hash before evaluation. `final_test_results.json` is the validated six-model Milestone 11 result, and `efficiency_results.json` is the same-Tesla-T4 Milestone 12 benchmark. Checkpoint weights and raw teacher caches remain in persistent external artifact storage described by `artifacts/manifest.json`.

Milestone 13 first writes resumable per-model ranking caches and `error_review_packet.json` to persistent artifact storage. After exactly 80 failures are classified, the compact, tracked deliverables are `error_analysis.csv` and `docs/error_analysis.md`; raw score caches and checkpoints remain outside Git.

Regenerate the validation artifacts with `python src/data/validate_dataset.py --seed 42`. The final result tables and completed error analysis are tracked; large checkpoints, score caches, and run logs remain external.
