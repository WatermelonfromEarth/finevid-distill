"""Small, testable helpers for inspecting the original FinQA JSON schema."""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Mapping


FINQA_COMMIT = "0f16e2867befa6840783e58be38c9efb9229d742"
FINQA_RAW_URL = (
    "https://raw.githubusercontent.com/czyssrs/FinQA/"
    f"{FINQA_COMMIT}/dataset/{{split}}.json"
)
INSPECTION_SPLITS = ("train", "dev")
_GOLD_KEY = re.compile(r"^(text|table)_(-?\d+)$")
_TOKENIZED_PUNCTUATION = re.compile(r"\s+([,.:])")


class SchemaMappingError(ValueError):
    """Raised when a gold evidence entry cannot be mapped to its raw source."""


def download_split(raw_dir: str | Path, split: str) -> Path:
    """Download one split from the pinned official FinQA repository if absent."""
    if split not in {*INSPECTION_SPLITS, "test"}:
        raise ValueError(f"Unsupported FinQA split: {split!r}")

    destination = Path(raw_dir) / f"{split}.json"
    if destination.exists():
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(FINQA_RAW_URL.format(split=split), destination)
    return destination


def load_split(
    raw_dir: str | Path,
    split: str,
    *,
    download_if_missing: bool = False,
) -> list[dict[str, Any]]:
    """Load an original FinQA JSON split without flattening its nested schema."""
    path = Path(raw_dir) / f"{split}.json"
    if download_if_missing:
        path = download_split(raw_dir, split)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run download_split or enable download_if_missing."
        )
    with path.open(encoding="utf-8") as source:
        records = json.load(source)
    if not isinstance(records, list):
        raise SchemaMappingError(f"Expected a list at the root of {path}.")
    return records


def iter_records(
    splits: Mapping[str, Iterable[dict[str, Any]]],
) -> Iterable[tuple[str, dict[str, Any]]]:
    """Yield ``(split, record)`` pairs in split and source-file order."""
    for split, records in splits.items():
        for record in records:
            yield split, record


def parse_gold_key(key: str) -> tuple[str, int]:
    """Parse ``text_N`` or ``table_N`` into its source kind and integer index."""
    match = _GOLD_KEY.fullmatch(key)
    if match is None:
        raise SchemaMappingError(f"Unrecognised gold_inds key: {key!r}")
    return match.group(1), int(match.group(2))


def serialize_table_row(table: list[list[str]], row_index: int) -> str:
    """Reproduce FinQA's annotated table-row template.

    FinQA prefixes the first header cell when it is non-empty, then verbalizes
    every remaining cell as ``the ROW of HEADER is CELL ;``.
    """
    header = table[0]
    row = table[row_index]
    pieces = [header[0]] if header[0] else []
    pieces.extend(
        f"the {row[0]} of {column_header} is {cell} ;"
        for column_header, cell in zip(header[1:], row[1:])
    )
    return " ".join(" ".join(pieces).split())


def normalize_annotation_spacing(value: str) -> str:
    """Normalize annotation-time spaces before comma, period, and colon."""
    return _TOKENIZED_PUNCTUATION.sub(r"\1", " ".join(value.split()))


def resolve_gold_evidence(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Resolve every ``qa.gold_inds`` entry to its exact raw source evidence.

    Text indices address ``pre_text + post_text`` and retain Python's negative
    index behaviour for the dataset's single legacy ``text_-1`` annotation.
    Table indices address raw rows directly, including row zero.
    """
    pre_text = record["pre_text"]
    post_text = record["post_text"]
    table = record["table"]
    combined_text = pre_text + post_text
    resolved: list[dict[str, Any]] = []

    for gold_key, annotated_value in record["qa"]["gold_inds"].items():
        source_kind, annotated_index = parse_gold_key(gold_key)
        if source_kind == "text":
            if not -len(combined_text) <= annotated_index < len(combined_text):
                raise SchemaMappingError(
                    f"{record['id']}:{gold_key} is outside the combined text."
                )
            combined_index = annotated_index % len(combined_text)
            raw_value = combined_text[annotated_index]
            if raw_value != annotated_value:
                raise SchemaMappingError(
                    f"{record['id']}:{gold_key} does not equal its raw sentence."
                )
            if combined_index < len(pre_text):
                source_field = "pre_text"
                source_index = combined_index
            else:
                source_field = "post_text"
                source_index = combined_index - len(pre_text)
        else:
            if not 0 <= annotated_index < len(table):
                raise SchemaMappingError(
                    f"{record['id']}:{gold_key} is outside the raw table."
                )
            combined_index = None
            source_field = "table"
            source_index = annotated_index
            raw_value = table[source_index]

        reconstructed_value = (
            raw_value
            if source_kind == "text"
            else serialize_table_row(table, source_index)
        )
        exact_value_match = reconstructed_value == annotated_value
        normalized_value_match = normalize_annotation_spacing(
            reconstructed_value
        ) == normalize_annotation_spacing(annotated_value)
        if not normalized_value_match:
            raise SchemaMappingError(
                f"{record['id']}:{gold_key} does not match its source evidence."
            )

        resolved.append(
            {
                "gold_key": gold_key,
                "source_kind": source_kind,
                "annotated_index": annotated_index,
                "source_field": source_field,
                "source_index": source_index,
                "combined_text_index": combined_index,
                "annotated_value": annotated_value,
                "raw_evidence": raw_value,
                "reconstructed_value": reconstructed_value,
                "exact_value_match": exact_value_match,
                "normalized_value_match": normalized_value_match,
            }
        )
    return resolved


def gold_format(record: Mapping[str, Any]) -> tuple[str, int]:
    """Return the evidence-source signature and supporting-fact count."""
    source_kinds = sorted(
        {parse_gold_key(key)[0] for key in record["qa"]["gold_inds"]}
    )
    return "+".join(source_kinds), len(record["qa"]["gold_inds"])


def candidate_counts(record: Mapping[str, Any]) -> dict[str, int]:
    """Count raw evidence candidates when every sentence and row is retained."""
    pre_count = len(record["pre_text"])
    post_count = len(record["post_text"])
    table_count = len(record["table"])
    return {
        "pre_text_candidates": pre_count,
        "post_text_candidates": post_count,
        "prose_candidates": pre_count + post_count,
        "table_row_candidates": table_count,
        "all_evidence_candidates": pre_count + post_count + table_count,
        "gold_supporting_facts": len(record["qa"]["gold_inds"]),
    }
