"""Prepare a deterministic, human-reviewable sample of final-model failures."""

from __future__ import annotations

import argparse
import json
import math
import random
import re
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from finevid_distill.data.finqa import load_split
from finevid_distill.evaluation.evaluate import (
    CachedTeacherRanker,
    Ranker,
    load_jsonl,
    write_json,
)
from finevid_distill.evaluation.final_comparison import (
    _release_accelerator_memory,
    validate_final_payload,
)
from finevid_distill.evaluation.final_selection import (
    EXPECTED_TEST_DATA_SHA256,
    EXPECTED_TEST_QUESTIONS,
    sha256_file,
    validate_selection_against_runs,
)
from finevid_distill.evaluation.metrics import mean_metrics, rank_by_score, ranking_metrics
from finevid_distill.models.bge_ranker import BGE_MODEL_ID, BGE_MODEL_REVISION, BGERanker


ERROR_MODEL_LABELS = (
    "Frozen BGE",
    "Hard-label BGE",
    "Distilled BGE",
    "Qwen teacher",
)
FAILURE_CATEGORIES = (
    "wrong financial metric",
    "wrong year",
    "missed table evidence",
    "missed prose evidence",
    "incomplete multi-fact retrieval",
    "ambiguous annotation",
    "teacher error",
    "truncation problem",
    "excessive lexical matching",
)
FAILURE_DEFINITION = "not every gold candidate appears in the first five results"
SCORE_CACHE_SCHEMA_VERSION = 1
PACKET_SCHEMA_VERSION = 1
DEFAULT_FAILURES_PER_MODEL = 20


def _slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def _validate_score_rows(
    records: Sequence[Mapping[str, Any]], score_rows: Sequence[Sequence[float]]
) -> list[list[float]]:
    if len(score_rows) != len(records):
        raise ValueError("Score and record counts differ.")
    validated: list[list[float]] = []
    for record, values in zip(records, score_rows, strict=True):
        row = [float(value) for value in values]
        if len(row) != len(record["candidates"]) or not all(map(math.isfinite, row)):
            raise ValueError(f"Invalid scores for {record['question_id']}.")
        validated.append(row)
    return validated


def write_score_cache(
    path: Path,
    *,
    label: str,
    records: Sequence[Mapping[str, Any]],
    score_rows: Sequence[Sequence[float]],
    test_data_sha256: str,
    selection_sha256: str,
) -> None:
    """Atomically persist one model's candidate scores for resumable review prep."""
    rows = _validate_score_rows(records, score_rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    metadata = {
        "record_type": "metadata",
        "schema_version": SCORE_CACHE_SCHEMA_VERSION,
        "label": label,
        "question_count": len(records),
        "test_data_sha256": test_data_sha256,
        "selection_sha256": selection_sha256,
        "tie_policy": "stable_original_candidate_order",
    }
    with temporary.open("w", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(metadata, sort_keys=True, separators=(",", ":")) + "\n")
        for record, scores in zip(records, rows, strict=True):
            output.write(
                json.dumps(
                    {
                        "record_type": "scores",
                        "question_id": record["question_id"],
                        "candidate_ids": [
                            candidate["candidate_id"] for candidate in record["candidates"]
                        ],
                        "scores": scores,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )
    temporary.replace(path)


def load_score_cache(
    path: Path,
    *,
    label: str,
    records: Sequence[Mapping[str, Any]],
    test_data_sha256: str,
    selection_sha256: str,
) -> list[list[float]]:
    with path.open(encoding="utf-8") as source:
        lines = [json.loads(line) for line in source if line.strip()]
    if not lines:
        raise ValueError(f"Empty score cache: {path}")
    expected_metadata = {
        "record_type": "metadata",
        "schema_version": SCORE_CACHE_SCHEMA_VERSION,
        "label": label,
        "question_count": len(records),
        "test_data_sha256": test_data_sha256,
        "selection_sha256": selection_sha256,
        "tie_policy": "stable_original_candidate_order",
    }
    if lines[0] != expected_metadata or len(lines) != len(records) + 1:
        raise ValueError(f"Score-cache provenance changed for {label}.")
    score_rows: list[list[float]] = []
    for record, cached in zip(records, lines[1:], strict=True):
        expected_ids = [candidate["candidate_id"] for candidate in record["candidates"]]
        if (
            cached.get("record_type") != "scores"
            or cached.get("question_id") != record["question_id"]
            or cached.get("candidate_ids") != expected_ids
        ):
            raise ValueError(f"Score-cache ordering changed for {record['question_id']}.")
        score_rows.append(cached.get("scores", []))
    return _validate_score_rows(records, score_rows)


def score_or_load(
    ranker_factory: Callable[[], Ranker],
    *,
    label: str,
    records: Sequence[Mapping[str, Any]],
    cache_path: Path,
    test_data_sha256: str,
    selection_sha256: str,
) -> list[list[float]]:
    if cache_path.exists():
        print(f"Reusing validated {label} score cache: {cache_path}", flush=True)
        return load_score_cache(
            cache_path,
            label=label,
            records=records,
            test_data_sha256=test_data_sha256,
            selection_sha256=selection_sha256,
        )
    print(f"Scoring {label} for failure analysis...", flush=True)
    ranker = ranker_factory()
    if ranker.label != label:
        raise ValueError(f"Unexpected ranker label: {ranker.label}")
    rows = ranker.score_records(records)
    write_score_cache(
        cache_path,
        label=label,
        records=records,
        score_rows=rows,
        test_data_sha256=test_data_sha256,
        selection_sha256=selection_sha256,
    )
    del ranker
    _release_accelerator_memory()
    return _validate_score_rows(records, rows)


def ranking_detail(
    record: Mapping[str, Any], scores: Sequence[float]
) -> dict[str, Any]:
    values = _validate_score_rows([record], [scores])[0]
    candidate_ids = [candidate["candidate_id"] for candidate in record["candidates"]]
    candidates = {candidate["candidate_id"]: candidate for candidate in record["candidates"]}
    score_by_id = dict(zip(candidate_ids, values, strict=True))
    ranked_ids = rank_by_score(candidate_ids, values)
    positives = list(record["positive_candidate_ids"])
    positive_set = set(positives)
    top_five = ranked_ids[:5]
    retrieved = [candidate_id for candidate_id in positives if candidate_id in top_five]
    missing = [candidate_id for candidate_id in positives if candidate_id not in top_five]
    gold_ranks = {
        candidate_id: ranked_ids.index(candidate_id) + 1 for candidate_id in positives
    }

    def ranked_candidate(candidate_id: str) -> dict[str, Any]:
        candidate = candidates[candidate_id]
        return {
            "candidate_id": candidate_id,
            "score": score_by_id[candidate_id],
            "source_type": candidate["source_type"],
            "source_index": candidate["source_index"],
            "text": candidate["text"],
            "word_count": len(str(candidate["text"]).split()),
            "is_gold": candidate_id in positive_set,
        }

    return {
        "failed_complete_recall_at_5": bool(missing),
        "first_gold_rank": min(gold_ranks.values()),
        "gold_ranks": gold_ranks,
        "retrieved_gold_ids_at_5": retrieved,
        "missing_gold_ids_at_5": missing,
        "top_10": [ranked_candidate(candidate_id) for candidate_id in ranked_ids[:10]],
        "metrics": ranking_metrics(ranked_ids, positives),
    }


def _shuffled(values: Sequence[int], *, seed: int, label: str) -> list[int]:
    result = list(values)
    random.Random(f"{seed}:{label}").shuffle(result)
    return result


def select_failure_instances(
    cases: Sequence[Mapping[str, Any]],
    *,
    failures_per_model: int = DEFAULT_FAILURES_PER_MODEL,
    seed: int = 42,
) -> list[tuple[str, int]]:
    """Select an equal, deterministic number of genuine top-five failures per model."""
    if failures_per_model <= 0:
        raise ValueError("failures_per_model must be positive.")
    selected: list[tuple[str, int]] = []
    for label in ERROR_MODEL_LABELS:
        failures = [
            index
            for index, case in enumerate(cases)
            if case["models"][label]["failed_complete_recall_at_5"]
        ]
        if len(failures) < failures_per_model:
            raise ValueError(f"Not enough {label} failures for the requested sample.")
        if label == "Hard-label BGE":
            contrast = [
                index
                for index in failures
                if not cases[index]["models"]["Distilled BGE"]["failed_complete_recall_at_5"]
            ]
        elif label == "Distilled BGE":
            contrast = [
                index
                for index in failures
                if not cases[index]["models"]["Hard-label BGE"]["failed_complete_recall_at_5"]
            ]
        else:
            contrast = [
                index
                for index in failures
                if not cases[index]["models"]["Hard-label BGE"]["failed_complete_recall_at_5"]
            ]
        contrast = _shuffled(contrast, seed=seed, label=f"{label}:contrast")
        contrast_set = set(contrast)
        remainder = _shuffled(
            [index for index in failures if index not in contrast_set],
            seed=seed,
            label=f"{label}:remainder",
        )
        contrast_target = min(failures_per_model // 2, len(contrast))
        chosen = contrast[:contrast_target] + remainder[: failures_per_model - contrast_target]
        if len(chosen) < failures_per_model:
            chosen.extend(contrast[contrast_target : failures_per_model - len(chosen) + contrast_target])
        if len(chosen) != failures_per_model or len(chosen) != len(set(chosen)):
            raise RuntimeError(f"Could not construct a unique {label} failure sample.")
        selected.extend((label, index) for index in chosen)
    return selected


def build_review_packet(
    records: Sequence[Mapping[str, Any]],
    raw_records: Sequence[Mapping[str, Any]],
    score_rows_by_model: Mapping[str, Sequence[Sequence[float]]],
    *,
    final_metrics: Mapping[str, Mapping[str, float]],
    test_data_sha256: str,
    selection_sha256: str,
    failures_per_model: int = DEFAULT_FAILURES_PER_MODEL,
    seed: int = 42,
) -> dict[str, Any]:
    if tuple(score_rows_by_model) != ERROR_MODEL_LABELS:
        raise ValueError("Error-analysis models are incomplete or out of order.")
    raw_by_id = {record["id"]: record for record in raw_records}
    if len(raw_by_id) != len(raw_records):
        raise ValueError("Duplicate raw FinQA question IDs.")
    cases: list[dict[str, Any]] = []
    per_model_details: dict[str, list[dict[str, Any]]] = {}
    for label in ERROR_MODEL_LABELS:
        rows = _validate_score_rows(records, score_rows_by_model[label])
        per_model_details[label] = [
            ranking_detail(record, scores)
            for record, scores in zip(records, rows, strict=True)
        ]
        calculated = mean_metrics([detail["metrics"] for detail in per_model_details[label]])
        expected = final_metrics[label]
        for metric, value in calculated.items():
            if not math.isclose(value, float(expected[metric]), rel_tol=0, abs_tol=1e-12):
                raise ValueError(f"{label} {metric} does not reproduce the final result.")

    for index, record in enumerate(records):
        raw = raw_by_id.get(record["question_id"])
        if raw is None or raw["qa"]["question"] != record["question"]:
            raise ValueError(f"Raw/processed question mismatch: {record['question_id']}")
        candidate_by_id = {
            candidate["candidate_id"]: candidate for candidate in record["candidates"]
        }
        positives = [candidate_by_id[candidate_id] for candidate_id in record["positive_candidate_ids"]]
        cases.append(
            {
                "question_id": record["question_id"],
                "report_id": record["report_id"],
                "question": record["question"],
                "question_word_count": len(str(record["question"]).split()),
                "candidate_count": len(record["candidates"]),
                "gold_count": len(positives),
                "gold_candidates": positives,
                "original_gold_annotations": raw["qa"]["gold_inds"],
                "program": raw["qa"]["program"],
                "exe_ans": raw["qa"]["exe_ans"],
                "models": {
                    label: per_model_details[label][index] for label in ERROR_MODEL_LABELS
                },
            }
        )

    selected = select_failure_instances(
        cases, failures_per_model=failures_per_model, seed=seed
    )
    review_instances: list[dict[str, Any]] = []
    for order, (label, case_index) in enumerate(selected, start=1):
        case = cases[case_index]
        review_instances.append(
            {
                "review_order": order,
                "instance_id": f"{_slug(label)}::{case['question_id']}",
                "failure_model": label,
                "suggested_categories": list(FAILURE_CATEGORIES),
                **case,
            }
        )

    failure_counts = {
        label: sum(
            detail["failed_complete_recall_at_5"] for detail in per_model_details[label]
        )
        for label in ERROR_MODEL_LABELS
    }
    return {
        "schema_version": PACKET_SCHEMA_VERSION,
        "split": "test",
        "question_count": len(records),
        "test_data_sha256": test_data_sha256,
        "selection_sha256": selection_sha256,
        "seed": seed,
        "failure_definition": FAILURE_DEFINITION,
        "categories": list(FAILURE_CATEGORIES),
        "failures_per_model_reviewed": failures_per_model,
        "review_instance_count": len(review_instances),
        "sampling_method": (
            "equal per-model sample; half prioritized for a hard-vs-distilled contrast "
            "when available, remainder seeded random among that model's failures"
        ),
        "full_test_failure_counts": failure_counts,
        "full_test_complete_recall_at_5": {
            label: final_metrics[label]["complete_recall_at_5"] for label in ERROR_MODEL_LABELS
        },
        "final_metrics": {label: dict(final_metrics[label]) for label in ERROR_MODEL_LABELS},
        "review_instructions": (
            "Assign exactly one primary category and a concrete note to every instance. "
            "Use top-10, gold ranks, peer-model rankings, original annotations, program, "
            "and answer together; do not infer failure category from source type alone."
        ),
        "instances": review_instances,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=root / "outputs/final_selection.json")
    parser.add_argument("--final-results", type=Path, default=root / "outputs/final_test_results.json")
    parser.add_argument("--test-data", type=Path, default=root / "data/processed/test.jsonl")
    parser.add_argument("--raw-test-data", type=Path, default=root / "data/raw/test.json")
    parser.add_argument("--teacher-cache", type=Path, required=True)
    parser.add_argument("--hard-dir", type=Path, required=True)
    parser.add_argument("--distilled-dir", type=Path, required=True)
    parser.add_argument("--score-cache-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--failures-per-model", type=int, default=DEFAULT_FAILURES_PER_MODEL)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.batch_size <= 0 or args.failures_per_model <= 0:
        raise ValueError("Batch size and failures per model must be positive.")
    test_hash = sha256_file(args.test_data)
    if test_hash != EXPECTED_TEST_DATA_SHA256:
        raise ValueError("Processed public test data does not match the frozen SHA-256.")
    records = load_jsonl(args.test_data)
    if len(records) != EXPECTED_TEST_QUESTIONS:
        raise ValueError("Processed public test question count changed.")
    raw_records = load_split(args.raw_test_data.parent, "test")
    final_payload = json.loads(args.final_results.read_text(encoding="utf-8"))
    validate_final_payload(final_payload)
    selection_hash = sha256_file(args.selection)
    if selection_hash != final_payload["selection_sha256"]:
        raise ValueError("Final results do not match the frozen selection file.")
    selected = validate_selection_against_runs(
        args.selection, args.hard_dir, args.distilled_dir
    )
    factories: dict[str, Callable[[], Ranker]] = {
        "Frozen BGE": lambda: BGERanker(
            BGE_MODEL_ID,
            revision=BGE_MODEL_REVISION,
            device=args.device,
            batch_size=args.batch_size,
            label="Frozen BGE",
        ),
        "Hard-label BGE": lambda: BGERanker(
            str(selected["hard_label"]),
            revision=None,
            device=args.device,
            batch_size=args.batch_size,
            local_files_only=True,
            label="Hard-label BGE",
        ),
        "Distilled BGE": lambda: BGERanker(
            str(selected["distilled"]),
            revision=None,
            device=args.device,
            batch_size=args.batch_size,
            local_files_only=True,
            label="Distilled BGE",
        ),
        "Qwen teacher": lambda: CachedTeacherRanker(args.teacher_cache),
    }
    scores: dict[str, list[list[float]]] = {}
    for label in ERROR_MODEL_LABELS:
        scores[label] = score_or_load(
            factories[label],
            label=label,
            records=records,
            cache_path=args.score_cache_dir / f"{_slug(label)}.jsonl",
            test_data_sha256=test_hash,
            selection_sha256=selection_hash,
        )
    packet = build_review_packet(
        records,
        raw_records,
        scores,
        final_metrics=final_payload["models"],
        test_data_sha256=test_hash,
        selection_sha256=selection_hash,
        failures_per_model=args.failures_per_model,
    )
    write_json(packet, args.output)
    print("Full-test CompleteRecall@5 failure counts:")
    for label, count in packet["full_test_failure_counts"].items():
        print(f"  {label}: {count}/{len(records)}")
    print(f"Prepared {packet['review_instance_count']} human-review instances: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
