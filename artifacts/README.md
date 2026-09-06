# Experiment artifacts

Small, reviewable results are tracked in `outputs/`. Large or generated artifacts use this external layout:

```text
FinEvid-Distill/
├── processed_data/train_rows.jsonl
├── teacher_scores/
│   ├── teacher_train_scores.jsonl
│   ├── teacher_dev_scores.jsonl
│   └── teacher_test_scores.jsonl
└── checkpoints/
    ├── hard_label_student_tau005/
    └── distilled_student/
```

The full checkpoint directories contain model weights, optimizer and scheduler state, gradient-scaler state, RNG state, training history, and best/reload-verification records. They are too large for ordinary Git history and remain in Google Drive or equivalent artifact storage. `manifest.json` records the fixed paths, available hashes, and selected epochs.

Validate the Git checkout alone:

```bash
python src/evaluation/audit_repository.py
```

Validate the checkout plus all external artifacts:

```bash
python src/evaluation/audit_repository.py --artifact-root /path/to/FinEvid-Distill
```

The second command validates all teacher rows against the processed candidate IDs and ordering, checks the shared training-row hash, reconstructs the frozen development selection from both run directories, and confirms that both selected model directories exist.
