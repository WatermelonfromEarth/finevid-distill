"""Build the one fixed FinQA training file shared by both student treatments."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from finevid_distill.data.build_dataset import write_jsonl
from finevid_distill.data.cache_teacher_scores import (
    load_cache,
    validate_teacher_cache,
)
from finevid_distill.evaluation.evaluate import load_jsonl


EXPECTED_SEED = 42
TARGET_CANDIDATES = 8
NEGATIVE_STRATEGY = "seeded_uniform_without_replacement_within_report"


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def question_rng(seed: int, question_id: str) -> random.Random:
    """Return a stable per-question RNG independent of input traversal order."""
    material = f"{seed}\0{question_id}".encode("utf-8")
    derived_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    return random.Random(derived_seed)


def _validate_source_pair(
    record: Mapping[str, Any], cache_record: Mapping[str, Any]
) -> tuple[list[str], list[float]]:
    question_id = record.get("question_id")
    if cache_record.get("question_id") != question_id:
        raise ValueError(f"Teacher cache question mismatch for {question_id}.")

    candidate_ids = [candidate["candidate_id"] for candidate in record["candidates"]]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError(f"Duplicate source candidate IDs for {question_id}.")
    if cache_record.get("candidate_ids") != candidate_ids:
        raise ValueError(f"Teacher candidate ordering mismatch for {question_id}.")

    scores = [float(score) for score in cache_record.get("teacher_scores", [])]
    if len(scores) != len(candidate_ids):
        raise ValueError(f"Teacher score count mismatch for {question_id}.")
    if not all(math.isfinite(score) for score in scores):
        raise ValueError(f"Non-finite teacher score for {question_id}.")
    if cache_record.get("score_type") != "raw_logit_difference":
        raise ValueError(f"Teacher scores are not raw logits for {question_id}.")
    if cache_record.get("temperature_applied") is not False:
        raise ValueError(f"Teacher cache was temperature transformed for {question_id}.")
    return candidate_ids, scores


def build_training_row(
    record: Mapping[str, Any],
    cache_record: Mapping[str, Any],
    *,
    seed: int = EXPECTED_SEED,
    target_candidates: int = TARGET_CANDIDATES,
) -> dict[str, Any]:
    """Select all positives plus seeded uniform within-report negatives."""
    if target_candidates <= 0:
        raise ValueError("target_candidates must be positive.")

    candidate_ids, scores = _validate_source_pair(record, cache_record)
    question_id = str(record["question_id"])
    positive_ids = list(record.get("positive_candidate_ids", []))
    if not positive_ids:
        raise ValueError(f"{question_id} has no positive candidates.")
    if len(positive_ids) != len(set(positive_ids)):
        raise ValueError(f"{question_id} contains duplicate positive IDs.")

    available = set(candidate_ids)
    missing = [positive_id for positive_id in positive_ids if positive_id not in available]
    if missing:
        raise ValueError(f"{question_id} has missing positive IDs: {missing!r}")

    positive_set = set(positive_ids)
    negative_ids = [candidate_id for candidate_id in candidate_ids if candidate_id not in positive_set]
    negative_count = min(
        max(target_candidates - len(positive_ids), 0),
        len(negative_ids),
    )
    rng = question_rng(seed, question_id)
    sampled_negatives = rng.sample(negative_ids, negative_count)
    selected_ids = [*positive_ids, *sampled_negatives]
    rng.shuffle(selected_ids)

    candidate_by_id = {
        candidate["candidate_id"]: candidate for candidate in record["candidates"]
    }
    score_by_id = dict(zip(candidate_ids, scores, strict=True))
    return {
        "question_id": question_id,
        "question": record["question"],
        "candidate_ids": selected_ids,
        "candidate_texts": [candidate_by_id[candidate_id]["text"] for candidate_id in selected_ids],
        "positive_mask": [int(candidate_id in positive_set) for candidate_id in selected_ids],
        "teacher_scores": [score_by_id[candidate_id] for candidate_id in selected_ids],
    }


def validate_training_row(
    row: Mapping[str, Any],
    record: Mapping[str, Any],
    cache_record: Mapping[str, Any],
    *,
    target_candidates: int = TARGET_CANDIDATES,
) -> int:
    """Validate one materialized row against both ordered source artifacts."""
    candidate_ids, scores = _validate_source_pair(record, cache_record)
    question_id = str(record["question_id"])
    if row.get("question_id") != question_id or row.get("question") != record.get("question"):
        raise ValueError(f"Training-row identity mismatch for {question_id}.")

    selected_ids = row.get("candidate_ids")
    texts = row.get("candidate_texts")
    mask = row.get("positive_mask")
    selected_scores = row.get("teacher_scores")
    if not all(isinstance(value, list) for value in (selected_ids, texts, mask, selected_scores)):
        raise ValueError(f"Training-row fields must be lists for {question_id}.")
    lengths = {len(selected_ids), len(texts), len(mask), len(selected_scores)}
    if len(lengths) != 1 or not selected_ids:
        raise ValueError(f"Training-row lengths do not match for {question_id}.")
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError(f"Duplicate selected candidate IDs for {question_id}.")

    positives = set(record["positive_candidate_ids"])
    if any(value not in (0, 1) for value in mask):
        raise ValueError(f"Non-binary positive mask for {question_id}.")
    mapped_positives = {
        candidate_id for candidate_id, value in zip(selected_ids, mask, strict=True) if value == 1
    }
    if mapped_positives != positives:
        raise ValueError(f"Not all and only gold facts were retained for {question_id}.")

    expected_size = min(len(candidate_ids), max(target_candidates, len(positives)))
    if len(selected_ids) != expected_size:
        raise ValueError(
            f"Unexpected training-row size for {question_id}: "
            f"{len(selected_ids)} != {expected_size}."
        )

    candidate_by_id = {
        candidate["candidate_id"]: candidate for candidate in record["candidates"]
    }
    score_by_id = dict(zip(candidate_ids, scores, strict=True))
    for candidate_id, text, score in zip(selected_ids, texts, selected_scores, strict=True):
        if candidate_id not in candidate_by_id:
            raise ValueError(f"Unknown selected candidate {candidate_id!r} for {question_id}.")
        if text != candidate_by_id[candidate_id]["text"]:
            raise ValueError(f"Candidate text ordering mismatch for {question_id}.")
        try:
            numeric_score = float(score)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Non-numeric selected teacher score for {question_id}.") from error
        if not math.isfinite(numeric_score) or numeric_score != score_by_id[candidate_id]:
            raise ValueError(f"Teacher score ordering mismatch for {question_id}.")
    return len(selected_ids)


def validate_training_rows(
    training_rows_path: Path,
    processed_records: Sequence[Mapping[str, Any]],
    cache_records: Sequence[Mapping[str, Any]],
    *,
    target_candidates: int = TARGET_CANDIDATES,
) -> dict[str, Any]:
    rows = load_jsonl(training_rows_path)
    if len(rows) != len(processed_records) or len(rows) != len(cache_records):
        raise ValueError("Training rows, processed records, and teacher cache counts differ.")
    candidate_counts = [
        validate_training_row(
            row,
            record,
            cache_record,
            target_candidates=target_candidates,
        )
        for row, record, cache_record in zip(
            rows, processed_records, cache_records, strict=True
        )
    ]
    return {
        "questions": len(rows),
        "candidates": sum(candidate_counts),
        "minimum_candidates": min(candidate_counts),
        "maximum_candidates": max(candidate_counts),
        "mean_candidates": sum(candidate_counts) / len(candidate_counts),
    }


def build_training_rows(
    processed_records: Sequence[Mapping[str, Any]],
    cache_records: Sequence[Mapping[str, Any]],
    destination: Path,
    *,
    seed: int = EXPECTED_SEED,
    target_candidates: int = TARGET_CANDIDATES,
) -> dict[str, Any]:
    if len(processed_records) != len(cache_records):
        raise ValueError("Processed records and teacher cache counts differ.")
    rows = [
        build_training_row(
            record,
            cache_record,
            seed=seed,
            target_candidates=target_candidates,
        )
        for record, cache_record in zip(processed_records, cache_records, strict=True)
    ]
    digest = write_jsonl(rows, destination)
    stats = validate_training_rows(
        destination,
        processed_records,
        cache_records,
        target_candidates=target_candidates,
    )
    stats.update(
        {
            "seed": seed,
            "target_candidates": target_candidates,
            "negative_strategy": NEGATIVE_STRATEGY,
            "sha256": digest,
        }
    )
    return stats


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--processed-train",
        type=Path,
        default=root / "data" / "processed" / "train.jsonl",
    )
    parser.add_argument(
        "--teacher-cache",
        type=Path,
        default=root / "data" / "processed" / "teacher_train_scores.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "data" / "processed" / "train_rows.jsonl",
    )
    parser.add_argument("--seed", type=int, default=EXPECTED_SEED)
    parser.add_argument("--target-candidates", type=int, default=TARGET_CANDIDATES)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.seed != EXPECTED_SEED:
        raise ValueError(f"The beginner experiment seed must be {EXPECTED_SEED}.")
    if args.target_candidates != TARGET_CANDIDATES:
        raise ValueError(
            f"The beginner experiment target must be {TARGET_CANDIDATES} candidates."
        )

    records = load_jsonl(args.processed_train)
    validate_teacher_cache(args.teacher_cache, records)
    cache_records = load_cache(args.teacher_cache)
    stats = build_training_rows(
        records,
        cache_records,
        args.output,
        seed=args.seed,
        target_candidates=args.target_candidates,
    )
    print(json.dumps(stats, indent=2, sort_keys=True))
    print(f"Saved fixed shared training rows: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
