"""Cache and validate raw Qwen teacher logits in processed-candidate order."""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol

from finevid_distill.evaluation.evaluate import load_jsonl
from finevid_distill.models.teacher import (
    QWEN_MODEL_ID,
    QWEN_MODEL_REVISION,
    QwenTeacher,
)


SCORE_TYPE = "raw_logit_difference"
OFFICIAL_CACHE_SPLITS = ("train", "dev")


class PairScorer(Protocol):
    def score_pairs(
        self,
        pairs: Sequence[tuple[str, str]],
        *,
        batch_size: int,
        show_progress: bool,
    ) -> list[float]: ...


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def cache_record(
    processed_record: Mapping[str, Any], scores: Sequence[float]
) -> dict[str, Any]:
    candidate_ids = [candidate["candidate_id"] for candidate in processed_record["candidates"]]
    numeric_scores = [float(score) for score in scores]
    if len(candidate_ids) != len(numeric_scores):
        raise ValueError(
            f"Candidate/score count mismatch for {processed_record['question_id']}."
        )
    if not all(math.isfinite(score) for score in numeric_scores):
        raise ValueError(f"Non-finite score for {processed_record['question_id']}.")
    return {
        "question_id": processed_record["question_id"],
        "candidate_ids": candidate_ids,
        "teacher_scores": numeric_scores,
        "score_type": SCORE_TYPE,
        "temperature_applied": False,
    }


def load_cache(
    path: Path, *, recover_truncated_final_line: bool = False
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw_lines = path.read_bytes().splitlines(keepends=True)
    for line_index, raw_line in enumerate(raw_lines):
        if not raw_line.strip():
            continue
        try:
            line = raw_line.decode("utf-8")
            rows.append(json.loads(line))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            is_final_line = line_index == len(raw_lines) - 1
            if recover_truncated_final_line and is_final_line:
                repaired = path.with_suffix(path.suffix + ".repair")
                repaired.write_bytes(b"".join(raw_lines[:-1]))
                repaired.replace(path)
                print(f"Discarded an incomplete final cache row from {path}.")
                break
            raise ValueError(f"Invalid JSON on {path}:{line_index + 1}.") from error
    return rows


def validate_teacher_cache(
    cache_path: Path,
    processed_records: Sequence[Mapping[str, Any]],
    *,
    allow_prefix: bool = False,
) -> dict[str, int]:
    """Validate IDs, order, counts, finiteness, and raw-score metadata."""
    cache_rows = load_cache(
        cache_path, recover_truncated_final_line=allow_prefix
    )
    if allow_prefix:
        if len(cache_rows) > len(processed_records):
            raise ValueError("Partial teacher cache is longer than the dataset.")
    elif len(cache_rows) != len(processed_records):
        raise ValueError(
            f"Teacher cache has {len(cache_rows)} rows; expected {len(processed_records)}."
        )

    candidate_count = 0
    for index, cache_row in enumerate(cache_rows):
        record = processed_records[index]
        question_id = record["question_id"]
        expected_ids = [candidate["candidate_id"] for candidate in record["candidates"]]
        if cache_row.get("question_id") != question_id:
            raise ValueError(f"Question ordering mismatch at row {index + 1}.")
        if cache_row.get("candidate_ids") != expected_ids:
            raise ValueError(f"Candidate ordering mismatch for {question_id}.")
        scores = cache_row.get("teacher_scores")
        if not isinstance(scores, list) or len(scores) != len(expected_ids):
            raise ValueError(f"Candidate/score count mismatch for {question_id}.")
        try:
            numeric_scores = [float(score) for score in scores]
        except (TypeError, ValueError) as error:
            raise ValueError(f"Non-numeric teacher score for {question_id}.") from error
        if not all(math.isfinite(score) for score in numeric_scores):
            raise ValueError(f"Non-finite teacher score for {question_id}.")
        if cache_row.get("score_type") != SCORE_TYPE:
            raise ValueError(f"Scores are not raw logit differences for {question_id}.")
        if cache_row.get("temperature_applied") is not False:
            raise ValueError(f"Temperature was applied for {question_id}.")
        candidate_count += len(expected_ids)

    return {"questions": len(cache_rows), "candidates": candidate_count}


def _append_rows(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        output.flush()


def cache_split(
    processed_records: Sequence[Mapping[str, Any]],
    destination: Path,
    scorer: PairScorer,
    *,
    batch_size: int,
    pair_chunk_size: int,
    resume: bool = True,
) -> dict[str, int]:
    """Cache a split in resumable whole-question chunks, then strictly validate it."""
    if destination.exists():
        try:
            return validate_teacher_cache(destination, processed_records)
        except ValueError as error:
            raise ValueError(
                f"Existing cache is invalid: {destination}. Remove it before rebuilding."
            ) from error

    partial = destination.with_suffix(destination.suffix + ".partial")
    start_index = 0
    if partial.exists():
        if not resume:
            raise ValueError(f"Partial cache exists and resume is disabled: {partial}")
        progress = validate_teacher_cache(partial, processed_records, allow_prefix=True)
        start_index = progress["questions"]
        print(f"Resuming {destination.name} at question {start_index:,}.")

    record_index = start_index
    while record_index < len(processed_records):
        chunk_records: list[Mapping[str, Any]] = []
        pair_count = 0
        while record_index + len(chunk_records) < len(processed_records):
            record = processed_records[record_index + len(chunk_records)]
            next_count = len(record["candidates"])
            if chunk_records and pair_count + next_count > pair_chunk_size:
                break
            chunk_records.append(record)
            pair_count += next_count
            if pair_count >= pair_chunk_size:
                break

        pairs = [
            (record["question"], candidate["text"])
            for record in chunk_records
            for candidate in record["candidates"]
        ]
        raw_scores = scorer.score_pairs(
            pairs, batch_size=batch_size, show_progress=True
        )
        rows: list[dict[str, Any]] = []
        offset = 0
        for record in chunk_records:
            count = len(record["candidates"])
            rows.append(cache_record(record, raw_scores[offset : offset + count]))
            offset += count
        if offset != len(raw_scores):
            raise ValueError("Teacher score chunk could not be partitioned by question.")
        _append_rows(partial, rows)
        record_index += len(chunk_records)
        print(
            f"Cached {record_index:,}/{len(processed_records):,} questions "
            f"for {destination.name}."
        )

    stats = validate_teacher_cache(partial, processed_records)
    partial.replace(destination)
    return stats


def parse_splits(value: str) -> list[str]:
    splits = [part.strip() for part in value.split(",") if part.strip()]
    if (
        not splits
        or len(splits) != len(set(splits))
        or any(split not in OFFICIAL_CACHE_SPLITS for split in splits)
    ):
        raise argparse.ArgumentTypeError(
            f"Splits must be a unique comma-separated subset of {OFFICIAL_CACHE_SPLITS!r}."
        )
    return splits


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=parse_splits, default=parse_splits("train,dev"))
    parser.add_argument("--processed-dir", type=Path, default=root / "data" / "processed")
    parser.add_argument("--output-dir", type=Path, default=root / "data" / "processed")
    parser.add_argument("--model", default=QWEN_MODEL_ID)
    parser.add_argument("--revision", default=QWEN_MODEL_REVISION)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--pair-chunk-size", type=int, default=512)
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument(
        "--allow-cpu",
        action="store_true",
        help="Allow impractically slow CPU inference for small diagnostics only.",
    )
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--limit", type=int)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.max_length <= 0 or args.batch_size <= 0 or args.pair_chunk_size <= 0:
        raise ValueError("Length and batch arguments must be positive.")
    teacher = QwenTeacher(
        args.model,
        revision=args.revision,
        device=args.device,
        max_length=args.max_length,
        local_files_only=args.local_files_only,
        allow_cpu=args.allow_cpu,
    )
    for split in args.splits:
        processed_path = args.processed_dir / f"{split}.jsonl"
        records = load_jsonl(processed_path, args.limit)
        suffix = f".limit-{args.limit}" if args.limit is not None else ""
        destination = args.output_dir / f"teacher_{split}_scores{suffix}.jsonl"
        stats = cache_split(
            records,
            destination,
            teacher,
            batch_size=args.batch_size,
            pair_chunk_size=args.pair_chunk_size,
            resume=not args.no_resume,
        )
        print(
            f"Validated {destination}: {stats['questions']:,} questions, "
            f"{stats['candidates']:,} finite raw logits."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
