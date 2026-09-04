"""Evaluate all non-trained rankers through the shared metric implementation."""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol

from finevid_distill.evaluation.metrics import mean_metrics, rank_by_score, ranking_metrics
from finevid_distill.models.bge_ranker import (
    BGE_MODEL_ID,
    BGE_MODEL_REVISION,
    BGERanker,
)
from finevid_distill.models.bm25_ranker import BM25Ranker
from finevid_distill.models.random_ranker import RandomRanker


MODEL_ORDER = ("random", "bm25", "bge", "teacher")
DISPLAY_METRICS = (
    ("recall_at_1", "Recall@1"),
    ("recall_at_5", "Recall@5"),
    ("mrr", "MRR"),
    ("ndcg_at_10", "NDCG@10"),
    ("complete_recall_at_5", "CompleteRecall@5"),
)


class Ranker(Protocol):
    label: str

    def score_records(
        self, records: Sequence[Mapping[str, Any]]
    ) -> list[list[float]]: ...


class CachedTeacherRanker:
    label = "Qwen teacher"

    def __init__(self, cache_path: Path) -> None:
        self.cache_path = cache_path

    def score_records(
        self, records: Sequence[Mapping[str, Any]]
    ) -> list[list[float]]:
        cached: list[dict[str, Any]] = []
        with self.cache_path.open(encoding="utf-8") as cache_file:
            for line in cache_file:
                if line.strip():
                    cached.append(json.loads(line))
        if len(cached) != len(records):
            raise ValueError("Teacher cache and evaluation record counts differ.")
        scores: list[list[float]] = []
        for record, cache_record in zip(records, cached, strict=True):
            expected_ids = [item["candidate_id"] for item in record["candidates"]]
            if cache_record.get("question_id") != record["question_id"]:
                raise ValueError("Teacher cache question ordering changed.")
            if cache_record.get("candidate_ids") != expected_ids:
                raise ValueError(
                    f"Teacher candidate ordering changed for {record['question_id']}."
                )
            row = [float(score) for score in cache_record.get("teacher_scores", [])]
            if len(row) != len(expected_ids) or not all(map(math.isfinite, row)):
                raise ValueError(f"Invalid teacher scores for {record['question_id']}.")
            if cache_record.get("score_type") != "raw_logit_difference":
                raise ValueError("Teacher cache does not contain raw logit differences.")
            if cache_record.get("temperature_applied") is not False:
                raise ValueError("Teacher cache was temperature transformed.")
            scores.append(row)
        return scores


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as input_file:
        for line in input_file:
            if line.strip():
                records.append(json.loads(line))
            if limit is not None and len(records) >= limit:
                break
    if not records:
        raise ValueError(f"No records found in {path}.")
    return records


def evaluate_ranker(
    records: Sequence[Mapping[str, Any]], ranker: Ranker
) -> dict[str, float]:
    score_rows = ranker.score_records(records)
    if len(score_rows) != len(records):
        raise ValueError(f"{ranker.label} returned the wrong number of score rows.")

    per_question: list[dict[str, float]] = []
    for record, scores in zip(records, score_rows, strict=True):
        candidate_ids = [candidate["candidate_id"] for candidate in record["candidates"]]
        ranked_ids = rank_by_score(candidate_ids, scores)
        per_question.append(ranking_metrics(ranked_ids, record["positive_candidate_ids"]))
    return mean_metrics(per_question)


def format_markdown_table(results: Mapping[str, Mapping[str, float]]) -> str:
    headers = ["Model", *(display for _, display in DISPLAY_METRICS)]
    divider = ["---", *("---:" for _ in DISPLAY_METRICS)]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(divider) + " |"]
    for label, metrics in results.items():
        values = [label, *(f"{metrics[key]:.6f}" for key, _ in DISPLAY_METRICS)]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_json(payload: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def parse_model_names(value: str) -> list[str]:
    names = [name.strip().lower() for name in value.split(",") if name.strip()]
    unknown = [name for name in names if name not in MODEL_ORDER]
    if unknown or not names or len(names) != len(set(names)):
        raise argparse.ArgumentTypeError(
            f"Models must be a unique comma-separated subset of {MODEL_ORDER!r}."
        )
    return names


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev",), default="dev")
    parser.add_argument("--models", type=parse_model_names, default=parse_model_names("random,bm25,bge"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--bge-model", default=BGE_MODEL_ID)
    parser.add_argument("--bge-revision", default=BGE_MODEL_REVISION)
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument(
        "--teacher-cache",
        type=Path,
        default=root / "data" / "processed" / "teacher_dev_scores.jsonl",
    )
    parser.add_argument(
        "--output", type=Path, default=root / "outputs" / "dev_baselines.json"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.seed != 42:
        raise ValueError("The beginner experiment seed must be 42.")
    root = project_root()
    data_path = root / "data" / "processed" / f"{args.split}.jsonl"
    records = load_jsonl(data_path, args.limit)

    rankers: dict[str, Ranker] = {
        "random": RandomRanker(args.seed),
        "bm25": BM25Ranker(),
    }
    if "bge" in args.models:
        rankers["bge"] = BGERanker(
            args.bge_model,
            revision=args.bge_revision,
            device=args.device,
            batch_size=args.batch_size,
            local_files_only=args.local_files_only,
        )
    if "teacher" in args.models:
        rankers["teacher"] = CachedTeacherRanker(args.teacher_cache)

    results: dict[str, dict[str, float]] = {}
    for name in args.models:
        ranker = rankers[name]
        print(f"Evaluating {ranker.label} on {len(records):,} development questions...")
        results[ranker.label] = evaluate_ranker(records, ranker)

    payload = {
        "split": args.split,
        "question_count": len(records),
        "seed": args.seed,
        "tie_policy": "stable_original_candidate_order",
        "recall_definition": "fraction_of_all_gold_candidates_retrieved",
        "models": results,
    }
    write_json(payload, args.output)
    print()
    print(format_markdown_table(results))
    print(f"\nSaved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
