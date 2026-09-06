"""Run the locked six-model comparison on the public FinQA test split."""

from __future__ import annotations

import argparse
import gc
import json
import math
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from finevid_distill.evaluation.evaluate import (
    CachedTeacherRanker,
    Ranker,
    evaluate_ranker,
    format_markdown_table,
    load_jsonl,
    write_json,
)
from finevid_distill.evaluation.final_selection import (
    EXPECTED_TEST_DATA_SHA256,
    EXPECTED_TEST_QUESTIONS,
    sha256_file,
    validate_selection_against_runs,
)
from finevid_distill.evaluation.metrics import METRIC_NAMES
from finevid_distill.models.bge_ranker import BGE_MODEL_ID, BGE_MODEL_REVISION, BGERanker
from finevid_distill.models.bm25_ranker import BM25Ranker
from finevid_distill.models.random_ranker import RandomRanker


FINAL_MODEL_LABELS = (
    "Random",
    "BM25",
    "Frozen BGE",
    "Hard-label BGE",
    "Distilled BGE",
    "Qwen teacher",
)


def evaluate_final_rankers(
    records: Sequence[Mapping[str, Any]],
    rankers: Sequence[Ranker],
) -> dict[str, dict[str, float]]:
    if tuple(ranker.label for ranker in rankers) != FINAL_MODEL_LABELS:
        raise ValueError("Final rankers must use the locked model order and labels.")
    results: dict[str, dict[str, float]] = {}
    for ranker in rankers:
        results[ranker.label] = evaluate_ranker(records, ranker)
    return results


def build_final_payload(
    results: Mapping[str, Mapping[str, float]],
    *,
    question_count: int,
    selection_sha256: str,
) -> dict[str, Any]:
    if tuple(results) != FINAL_MODEL_LABELS:
        raise ValueError("Final results are incomplete or out of order.")
    teacher_ndcg = float(results["Qwen teacher"]["ndcg_at_10"])
    if not math.isfinite(teacher_ndcg) or teacher_ndcg <= 0:
        raise ValueError("Teacher NDCG@10 must be finite and positive.")
    retained = float(results["Distilled BGE"]["ndcg_at_10"]) / teacher_ndcg
    if not math.isfinite(retained):
        raise ValueError("Teacher quality retained is not finite.")
    return {
        "split": "test",
        "question_count": question_count,
        "test_data_sha256": EXPECTED_TEST_DATA_SHA256,
        "seed": 42,
        "selection_sha256": selection_sha256,
        "selection_frozen_before_test": True,
        "primary_metric": "mrr",
        "tie_policy": "stable_original_candidate_order",
        "recall_definition": "fraction_of_all_gold_candidates_retrieved",
        "models": dict(results),
        "teacher_quality_retained": retained,
        "teacher_quality_retained_definition": (
            "Distilled BGE NDCG@10 divided by Qwen teacher NDCG@10"
        ),
        "distilled_minus_hard_mrr": (
            float(results["Distilled BGE"]["mrr"])
            - float(results["Hard-label BGE"]["mrr"])
        ),
        "distillation_improves_over_hard_label": (
            float(results["Distilled BGE"]["mrr"])
            > float(results["Hard-label BGE"]["mrr"])
        ),
    }


def validate_final_payload(payload: Mapping[str, Any]) -> None:
    required = {
        "split": "test",
        "question_count": EXPECTED_TEST_QUESTIONS,
        "test_data_sha256": EXPECTED_TEST_DATA_SHA256,
        "seed": 42,
        "selection_frozen_before_test": True,
        "primary_metric": "mrr",
        "tie_policy": "stable_original_candidate_order",
        "recall_definition": "fraction_of_all_gold_candidates_retrieved",
    }
    if any(payload.get(key) != value for key, value in required.items()):
        raise ValueError("Final result provenance or evaluation policy is invalid.")
    models = payload.get("models", {})
    if set(models) != set(FINAL_MODEL_LABELS):
        raise ValueError("Final result does not contain exactly the six locked models.")
    for label in FINAL_MODEL_LABELS:
        metrics = models[label]
        if set(metrics) != set(METRIC_NAMES) or not all(
            isinstance(value, (int, float)) and math.isfinite(value) and 0 <= value <= 1
            for value in metrics.values()
        ):
            raise ValueError(f"Invalid final metrics for {label}.")
    selection_sha = payload.get("selection_sha256")
    if not isinstance(selection_sha, str) or len(selection_sha) != 64:
        raise ValueError("Final result selection SHA-256 is invalid.")
    expected = build_final_payload(
        {label: models[label] for label in FINAL_MODEL_LABELS},
        question_count=EXPECTED_TEST_QUESTIONS,
        selection_sha256=selection_sha,
    )
    if dict(payload) != expected:
        raise ValueError("Final calculated fields are inconsistent with the model metrics.")


def _release_accelerator_memory() -> None:
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=root / "outputs/final_selection.json")
    parser.add_argument("--test-data", type=Path, default=root / "data/processed/test.jsonl")
    parser.add_argument("--teacher-cache", type=Path, required=True)
    parser.add_argument(
        "--hard-dir", type=Path, default=root / "outputs/checkpoints/hard_label_student_tau005"
    )
    parser.add_argument(
        "--distilled-dir", type=Path, default=root / "outputs/checkpoints/distilled_student"
    )
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output", type=Path, default=root / "outputs/final_test_results.json")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.batch_size <= 0:
        raise ValueError("--batch-size must be positive.")
    if args.test_data.name != "test.jsonl":
        raise ValueError("Final comparison accepts only the processed test.jsonl split.")
    if sha256_file(args.test_data) != EXPECTED_TEST_DATA_SHA256:
        raise ValueError("Processed public test data does not match the frozen SHA-256.")
    records = load_jsonl(args.test_data)
    if len(records) != EXPECTED_TEST_QUESTIONS:
        raise ValueError("Processed public test question count changed.")
    selected = validate_selection_against_runs(
        args.selection, args.hard_dir, args.distilled_dir
    )

    factories: list[tuple[str, Callable[[], Ranker]]] = [
        ("Random", lambda: RandomRanker(42)),
        ("BM25", BM25Ranker),
        (
            "Frozen BGE",
            lambda: BGERanker(
                BGE_MODEL_ID,
                revision=BGE_MODEL_REVISION,
                device=args.device,
                batch_size=args.batch_size,
                label="Frozen BGE",
            ),
        ),
        (
            "Hard-label BGE",
            lambda: BGERanker(
                str(selected["hard_label"]),
                revision=None,
                device=args.device,
                batch_size=args.batch_size,
                local_files_only=True,
                label="Hard-label BGE",
            ),
        ),
        (
            "Distilled BGE",
            lambda: BGERanker(
                str(selected["distilled"]),
                revision=None,
                device=args.device,
                batch_size=args.batch_size,
                local_files_only=True,
                label="Distilled BGE",
            ),
        ),
        ("Qwen teacher", lambda: CachedTeacherRanker(args.teacher_cache)),
    ]
    results: dict[str, dict[str, float]] = {}
    for label, factory in factories:
        print(f"Evaluating {label} on {len(records):,} locked test questions...", flush=True)
        ranker = factory()
        if ranker.label != label:
            raise ValueError(f"Unexpected label for final ranker: {ranker.label}")
        results[label] = evaluate_ranker(records, ranker)
        del ranker
        _release_accelerator_memory()

    payload = build_final_payload(
        results,
        question_count=len(records),
        selection_sha256=sha256_file(args.selection),
    )
    validate_final_payload(payload)
    write_json(payload, args.output)
    print()
    print(format_markdown_table(results))
    print(f"\nTeacher quality retained: {payload['teacher_quality_retained']:.6f}")
    print(f"Distilled minus hard-label MRR: {payload['distilled_minus_hard_mrr']:.6f}")
    print(f"Saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
