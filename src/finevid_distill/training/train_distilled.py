"""Train a BGE student with teacher-to-student KL and a 0.1 hard-label anchor."""

from finevid_distill.training.train_hard_labels import main as run_student_training


def main(argv: list[str] | None = None) -> int:
    return run_student_training(argv, treatment="distilled")


if __name__ == "__main__":
    raise SystemExit(main())
