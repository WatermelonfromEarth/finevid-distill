"""Freeze and validate the development-selected checkpoints before test access."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from finevid_distill.evaluation.compare_students import compare_student_runs
from finevid_distill.evaluation.metrics import METRIC_NAMES
from finevid_distill.evaluation.evaluate import write_json


SELECTION_SCHEMA_VERSION = 1
EXPECTED_TEST_DATA_SHA256 = "14b7b00bced86a9a37a040f0c2fc14ab1cdef7c43f895e21ff4da54cb668b975"
EXPECTED_TEST_QUESTIONS = 1147
EXPECTED_TRAINING_BUNDLE_SHA256 = "17a078245004016d7aa376692959e982ccd100beb5aced08cb746a4510949d80"
MODEL_KEYS = ("hard_label", "distilled")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_selection_document(selection: Mapping[str, Any]) -> None:
    """Validate the immutable policy and provenance stored at the freeze point."""
    required = {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "status": "frozen_before_public_test",
        "selection_split": "dev",
        "selection_metric": "mrr",
        "seed": 42,
        "development_question_count": 883,
        "test_data_sha256": EXPECTED_TEST_DATA_SHA256,
        "test_question_count": EXPECTED_TEST_QUESTIONS,
        "test_evaluated_at_freeze": False,
        "no_further_hyperparameter_search": True,
    }
    mismatches = {
        key: (selection.get(key), value)
        for key, value in required.items()
        if selection.get(key) != value
    }
    if mismatches:
        raise ValueError(f"Invalid final-selection policy: {mismatches}")
    if selection.get("development_winner") != "hard_label":
        raise ValueError("The recorded development winner must be hard_label.")
    if set(selection.get("models", {})) != set(MODEL_KEYS):
        raise ValueError("Final selection must contain exactly both student treatments.")
    if selection.get("source_bundle_sha256") != EXPECTED_TRAINING_BUNDLE_SHA256:
        raise ValueError("The training source-bundle SHA-256 changed after selection.")

    for key in MODEL_KEYS:
        record = selection["models"][key]
        checkpoint = Path(record.get("selected_checkpoint", ""))
        if checkpoint.is_absolute() or ".." in checkpoint.parts or checkpoint.name != "model":
            raise ValueError(f"Unsafe selected checkpoint for {key}.")
        if record.get("selected_epoch") not in (1, 2, 3):
            raise ValueError(f"Invalid selected epoch for {key}.")
        metrics = record.get("development_metrics", {})
        if set(metrics) != set(METRIC_NAMES) or not all(
            isinstance(value, (int, float)) and math.isfinite(value) and 0 <= value <= 1
            for value in metrics.values()
        ):
            raise ValueError(f"Invalid development metrics for {key}.")
    delta = selection.get("distilled_minus_hard_development_mrr")
    expected_delta = (
        selection["models"]["distilled"]["development_metrics"]["mrr"]
        - selection["models"]["hard_label"]["development_metrics"]["mrr"]
    )
    if not isinstance(delta, (int, float)) or not math.isclose(
        delta, expected_delta, rel_tol=0, abs_tol=1e-15
    ):
        raise ValueError("The recorded development MRR difference is inconsistent.")
    if delta >= 0:
        raise ValueError("The recorded development results do not select hard_label.")


def freeze_selection(
    hard_dir: Path,
    distilled_dir: Path,
    *,
    source_bundle_sha256: str,
) -> dict[str, Any]:
    """Create the selection record using development artifacts only."""
    report = compare_student_runs(hard_dir, distilled_dir)
    if report["split"] != "dev" or report["diagnostic_run"]:
        raise ValueError("Only complete development runs can freeze final selection.")
    directories = {"hard_label": hard_dir, "distilled": distilled_dir}
    labels = {"hard_label": "Hard-label BGE-small", "distilled": "Distilled BGE-small"}
    models: dict[str, Any] = {}
    for key in MODEL_KEYS:
        directory = directories[key]
        best = _read(directory / "best.json")
        config = _read(directory / "run_config.json")
        models[key] = {
            "run_directory_name": directory.name,
            "selected_checkpoint": f"{best['checkpoint']}/model",
            "selected_epoch": best["completed_epoch"],
            "development_metrics": report["models"][labels[key]],
            "training_code_sha256": config["training_code_sha256"],
            "train_rows_sha256": config["train_rows_sha256"],
            "dev_data_sha256": config["dev_data_sha256"],
        }
    payload = {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "status": "frozen_before_public_test",
        "selection_split": "dev",
        "selection_metric": "mrr",
        "selection_rule": "best completed epoch by development MRR",
        "seed": 42,
        "development_question_count": report["question_count"],
        "development_winner": "hard_label",
        "distilled_minus_hard_development_mrr": report["distilled_minus_hard"]["mrr"],
        "no_further_hyperparameter_search": True,
        "test_evaluated_at_freeze": False,
        "test_data_sha256": EXPECTED_TEST_DATA_SHA256,
        "test_question_count": EXPECTED_TEST_QUESTIONS,
        "source_bundle_sha256": source_bundle_sha256,
        "models": models,
    }
    validate_selection_document(payload)
    return payload


def validate_selection_against_runs(
    selection_path: Path,
    hard_dir: Path,
    distilled_dir: Path,
    *,
    require_model_directories: bool = True,
) -> dict[str, Path]:
    """Recreate the dev comparison and resolve the two locked model paths."""
    selection = _read(selection_path)
    validate_selection_document(selection)
    regenerated = freeze_selection(
        hard_dir,
        distilled_dir,
        source_bundle_sha256=selection["source_bundle_sha256"],
    )
    if regenerated != selection:
        raise ValueError("Final selection does not match the saved development runs.")
    resolved: dict[str, Path] = {}
    for key, directory in (("hard_label", hard_dir), ("distilled", distilled_dir)):
        model_path = directory / selection["models"][key]["selected_checkpoint"]
        if require_model_directories and not model_path.is_dir():
            raise FileNotFoundError(f"Selected {key} model is missing: {model_path}")
        resolved[key] = model_path
    return resolved


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hard-dir", type=Path, required=True)
    parser.add_argument("--distilled-dir", type=Path, required=True)
    parser.add_argument("--source-bundle-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite frozen selection: {args.output}")
    if len(args.source_bundle_sha256) != 64:
        raise ValueError("--source-bundle-sha256 must be a 64-character SHA-256.")
    payload = freeze_selection(
        args.hard_dir,
        args.distilled_dir,
        source_bundle_sha256=args.source_bundle_sha256,
    )
    write_json(payload, args.output)
    print(f"Frozen before test access: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
