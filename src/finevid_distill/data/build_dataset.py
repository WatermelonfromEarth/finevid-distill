"""Build deterministic FinQA evidence-ranking JSONL files."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Iterable, Mapping

from finevid_distill.data.finqa import INSPECTION_SPLITS, load_split, resolve_gold_evidence


OFFICIAL_SPLITS = (*INSPECTION_SPLITS, "test")
EXPECTED_SEED = 42


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def report_id_from_question_id(question_id: str) -> str:
    """Remove FinQA's final question-number suffix from an example ID."""
    report_id, separator, question_number = question_id.rpartition("-")
    if not separator or not report_id or not question_number.isdigit():
        raise ValueError(f"Unexpected FinQA question ID: {question_id!r}")
    return report_id


def candidate_id(source_type: str, source_index: int) -> str:
    """Return a deterministic ID unique within one question's candidates."""
    prefixes = {
        "pre_text": "pre-text",
        "post_text": "post-text",
        "table": "table-row",
    }
    try:
        prefix = prefixes[source_type]
    except KeyError as error:
        raise ValueError(f"Unknown source type: {source_type!r}") from error
    return f"{prefix}-{source_index}"


def format_table_row(table: list[list[str]], row_index: int) -> str:
    """Format one raw table row as compact, deterministic ranking text."""
    if not table:
        return ""
    row = table[row_index]
    header = table[0]

    if row_index == 0:
        return " | ".join(str(cell).strip() for cell in row).strip()

    parts: list[str] = []
    if row:
        parts.append(str(row[0]).strip())
    for column_index, cell in enumerate(row[1:], start=1):
        cell_text = str(cell).strip()
        header_text = (
            str(header[column_index]).strip()
            if column_index < len(header)
            else f"column-{column_index}"
        )
        if header_text:
            parts.append(f"{header_text}: {cell_text}")
        else:
            parts.append(cell_text)
    return " | ".join(part for part in parts if part).strip()


def make_candidates(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Create one candidate for every prose entry and raw table row."""
    candidates: list[dict[str, Any]] = []
    for source_type in ("pre_text", "post_text"):
        for source_index, text in enumerate(record[source_type]):
            candidates.append(
                {
                    "candidate_id": candidate_id(source_type, source_index),
                    "text": text,
                    "source_type": source_type,
                    "source_index": source_index,
                }
            )
    for source_index in range(len(record["table"])):
        candidates.append(
            {
                "candidate_id": candidate_id("table", source_index),
                "text": format_table_row(record["table"], source_index),
                "source_type": "table",
                "source_index": source_index,
            }
        )
    return candidates


def positive_candidate_ids(record: Mapping[str, Any]) -> list[str]:
    """Map every raw gold annotation to its candidate ID in annotation order."""
    positives = []
    for evidence in resolve_gold_evidence(record):
        positives.append(
            candidate_id(evidence["source_field"], evidence["source_index"])
        )
    return positives


def build_question(record: Mapping[str, Any]) -> dict[str, Any]:
    """Convert one untouched FinQA object into one ranking example."""
    question_id = record["id"]
    candidates = make_candidates(record)
    positives = positive_candidate_ids(record)
    available_ids = {candidate["candidate_id"] for candidate in candidates}
    missing = [positive for positive in positives if positive not in available_ids]
    if not positives:
        raise ValueError(f"{question_id} has no positive candidates.")
    if missing:
        raise ValueError(f"{question_id} has missing positive IDs: {missing!r}")
    return {
        "question_id": question_id,
        "report_id": report_id_from_question_id(question_id),
        "question": record["qa"]["question"],
        "candidates": candidates,
        "positive_candidate_ids": positives,
    }


def write_jsonl(records: Iterable[Mapping[str, Any]], destination: Path) -> str:
    """Atomically write compact JSONL and return its SHA-256 digest."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    digest = hashlib.sha256()
    with temporary.open("w", encoding="utf-8", newline="\n") as output:
        for record in records:
            line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            output.write(line)
            digest.update(line.encode("utf-8"))
    temporary.replace(destination)
    return digest.hexdigest()


def build_split(
    raw_dir: str | Path,
    processed_dir: str | Path,
    split: str,
) -> dict[str, Any]:
    """Build one official split and return deterministic output metadata."""
    if split not in OFFICIAL_SPLITS:
        raise ValueError(f"Unsupported split: {split!r}")
    raw_records = load_split(raw_dir, split)
    destination = Path(processed_dir) / f"{split}.jsonl"
    digest = write_jsonl((build_question(record) for record in raw_records), destination)
    return {
        "split": split,
        "records": len(raw_records),
        "path": destination.as_posix(),
        "sha256": digest,
    }


def build_all_splits(
    raw_dir: str | Path,
    processed_dir: str | Path,
    *,
    seed: int = EXPECTED_SEED,
) -> dict[str, dict[str, Any]]:
    """Build train/dev/test in official source order with the locked seed."""
    if seed != EXPECTED_SEED:
        raise ValueError(f"The beginner experiment seed must be {EXPECTED_SEED}.")
    random.seed(seed)
    return {
        split: build_split(raw_dir, processed_dir, split)
        for split in OFFICIAL_SPLITS
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=root / "data" / "raw")
    parser.add_argument(
        "--processed-dir", type=Path, default=root / "data" / "processed"
    )
    parser.add_argument("--seed", type=int, default=EXPECTED_SEED)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    results = build_all_splits(args.raw_dir, args.processed_dir, seed=args.seed)
    for result in results.values():
        print(
            f"{result['split']}: {result['records']:,} records -> "
            f"{result['path']} (sha256={result['sha256']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
