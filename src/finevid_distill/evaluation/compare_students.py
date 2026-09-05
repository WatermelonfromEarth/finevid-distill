"""Compare completed student runs only after checking their matched controls."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from finevid_distill.evaluation.evaluate import format_markdown_table, write_json
from finevid_distill.evaluation.metrics import METRIC_NAMES
from finevid_distill.training.train_hard_labels import (
    EXPECTED_DEVELOPMENT_QUESTIONS,
    EXPECTED_DEV_DATA_SHA256,
    EXPECTED_TRAINING_QUESTIONS,
    EXPECTED_TRAIN_ROWS_SHA256,
)


SUPERVISION_FIELDS = {"treatment", "objective", "target", "teacher_temperature", "hard_label_weight"}


def _read(directory: Path, name: str) -> dict:
    return json.loads((directory / name).read_text(encoding="utf-8"))


def compare_student_runs(
    hard_dir: Path, distilled_dir: Path, *, allow_diagnostic: bool = False
) -> dict:
    configs, metrics, initials = [], [], []
    for directory, expected_treatment in ((hard_dir, "hard_label"), (distilled_dir, "distilled")):
        config = _read(directory, "run_config.json")
        best = _read(directory, "best.json")
        latest = _read(directory, "latest.json")
        verification = _read(directory, "best_reload_verification.json")
        initial = _read(directory, "initial_development.json")
        epochs = _read(directory, "training_history.json")["epochs"]
        if config.get("schema_version") != 2 or config.get("treatment") != expected_treatment:
            raise ValueError("Expected the two new, matched student treatments; legacy runs cannot be substituted.")
        diagnostic = config["limit_train"] is not None or config["limit_dev"] is not None
        if diagnostic and not allow_diagnostic:
            raise ValueError("Diagnostic runs cannot be reported as full development experiments.")
        if not diagnostic:
            expected_full_run = {
                "train_rows_sha256": EXPECTED_TRAIN_ROWS_SHA256,
                "dev_data_sha256": EXPECTED_DEV_DATA_SHA256,
                "training_question_count": EXPECTED_TRAINING_QUESTIONS,
                "development_question_count": EXPECTED_DEVELOPMENT_QUESTIONS,
            }
            if any(config.get(key) != value for key, value in expected_full_run.items()):
                raise ValueError("Full run does not use the fixed complete experiment artifacts.")
        if [row["epoch"] for row in epochs] != list(range(1, config["epochs"] + 1)):
            raise ValueError("Both runs must complete their configured epoch budget.")
        steps = math.ceil(config["training_question_count"] / config["questions_per_batch"])
        if any(row["optimizer_steps"] != steps for row in epochs):
            raise ValueError("A run did not complete its expected optimizer steps.")
        if latest["completed_epoch"] != config["epochs"] or latest["global_step"] != steps * config["epochs"]:
            raise ValueError("Latest checkpoint does not match the complete training history.")
        selected = max(epochs, key=lambda row: row["development_metrics"]["mrr"])
        if best["completed_epoch"] != selected["epoch"] or best["development_metrics"] != selected["development_metrics"]:
            raise ValueError("Best checkpoint was not selected by development MRR.")
        if (verification.get("reload_verified") is not True
                or verification["checkpoint"] != best["checkpoint"]
                or verification["development_metrics"] != best["development_metrics"]):
            raise ValueError("Best checkpoint reload verification is missing or inconsistent.")
        for key in ("train_rows_sha256", "dev_data_sha256"):
            if verification.get(key) != config[key]:
                raise ValueError(f"Reload verification does not match {key}.")
        if (verification["question_count"] != config["development_question_count"]
                or initial["question_count"] != config["development_question_count"]
                or initial["dev_data_sha256"] != config["dev_data_sha256"]):
            raise ValueError("Development evaluations use inconsistent data.")
        for values in (verification["development_metrics"], initial["development_metrics"]):
            if set(values) != set(METRIC_NAMES) or not all(math.isfinite(v) and 0 <= v <= 1 for v in values.values()):
                raise ValueError("Development metrics must be complete, finite and in [0, 1].")
        configs.append(config)
        metrics.append(verification["development_metrics"])
        initials.append(initial["development_metrics"])
    controls = [{key: value for key, value in config.items() if key not in SUPERVISION_FIELDS}
                for config in configs]
    if controls[0] != controls[1]:
        differences = sorted(key for key in controls[0].keys() | controls[1].keys()
                             if controls[0].get(key) != controls[1].get(key))
        raise ValueError(f"Student controls differ: {differences}")
    if any(not math.isclose(initials[0][name], initials[1][name], rel_tol=0, abs_tol=1e-12)
           for name in METRIC_NAMES):
        raise ValueError("Pretrained development metrics differ before student training.")
    return {
        "split": "dev", "seed": configs[0]["seed"],
        "question_count": configs[0]["development_question_count"],
        "diagnostic_run": configs[0]["limit_train"] is not None or configs[0]["limit_dev"] is not None,
        "fairness_verified": True,
        "student_temperature": configs[0]["student_temperature"],
        "teacher_temperature": configs[1]["teacher_temperature"],
        "hard_label_weight": configs[1]["hard_label_weight"],
        "models": {"Pretrained BGE (training evaluator)": initials[0],
                   "Hard-label BGE-small": metrics[0], "Distilled BGE-small": metrics[1]},
        "distilled_minus_hard": {name: metrics[1][name] - metrics[0][name] for name in METRIC_NAMES},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hard-dir", type=Path, required=True)
    parser.add_argument("--distilled-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-diagnostic", action="store_true")
    args = parser.parse_args(argv)
    report = compare_student_runs(args.hard_dir, args.distilled_dir, allow_diagnostic=args.allow_diagnostic)
    write_json(report, args.output)
    print(format_markdown_table(report["models"]))
    print("Distilled minus hard:", json.dumps(report["distilled_minus_hard"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
