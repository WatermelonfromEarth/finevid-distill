"""Audit tracked results and optionally validate the external model artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from finevid_distill.data.cache_teacher_scores import validate_teacher_cache
from finevid_distill.evaluation.evaluate import load_jsonl
from finevid_distill.evaluation.final_comparison import validate_final_payload
from finevid_distill.evaluation.final_selection import validate_selection_against_runs


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def audit_repository(root: Path, artifact_root: Path | None = None) -> dict[str, Any]:
    manifest = _load_json(root / "artifacts/manifest.json")
    checked: list[str] = []
    for item in manifest["tracked_files"]:
        path = root / item["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = sha256_file(path)
        if actual != item["sha256"]:
            raise ValueError(f"Tracked artifact hash changed: {item['path']}")
        checked.append(item["path"])

    final_results = _load_json(root / "outputs/final_test_results.json")
    validate_final_payload(final_results)
    efficiency = _load_json(root / "outputs/efficiency_results.json")
    if efficiency["teacher_quality_retained"] != final_results["teacher_quality_retained"]:
        raise ValueError("Efficiency and final-result quality ratios differ.")
    for label in ("Distilled BGE", "Qwen teacher"):
        if efficiency["models"][label]["ndcg_at_10"] != final_results["models"][label]["ndcg_at_10"]:
            raise ValueError(f"Efficiency quality metric changed for {label}.")

    with (root / "outputs/error_analysis.csv").open(encoding="utf-8", newline="") as source:
        review_rows = list(csv.DictReader(source))
    if len(review_rows) != 80 or any(not row["review_note"].strip() for row in review_rows):
        raise ValueError("Error analysis is incomplete.")

    external: dict[str, Any] = {"status": "not_checked"}
    if artifact_root is not None:
        artifact_root = artifact_root.resolve()
        train_rows = artifact_root / "processed_data/train_rows.jsonl"
        expected_rows_hash = manifest["external_artifacts"]["training_rows"]["sha256"]
        if sha256_file(train_rows) != expected_rows_hash:
            raise ValueError("External training-row hash changed.")

        cache_results: dict[str, dict[str, int]] = {}
        for split in ("train", "dev", "test"):
            processed = load_jsonl(root / f"data/processed/{split}.jsonl")
            cache_path = artifact_root / f"teacher_scores/teacher_{split}_scores.jsonl"
            cache_results[split] = validate_teacher_cache(cache_path, processed)
            expected_hash = manifest["external_artifacts"]["teacher_scores"][split].get(
                "sha256"
            )
            if expected_hash and sha256_file(cache_path) != expected_hash:
                raise ValueError(f"External teacher {split} cache hash changed.")

        selected = validate_selection_against_runs(
            root / "outputs/final_selection.json",
            artifact_root / "checkpoints/hard_label_student_tau005",
            artifact_root / "checkpoints/distilled_student",
        )
        external = {
            "status": "validated",
            "artifact_root": str(artifact_root),
            "teacher_caches": cache_results,
            "selected_models": {key: str(path) for key, path in selected.items()},
        }

    return {
        "status": "passed",
        "tracked_files_checked": len(checked),
        "test_questions": final_results["question_count"],
        "research_answer": "no",
        "external_artifacts": external,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--artifact-root", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    print(json.dumps(audit_repository(args.root, args.artifact_root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
