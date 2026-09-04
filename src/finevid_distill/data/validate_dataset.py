"""Validate processed FinQA ranking data before any model sees it."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from finevid_distill.data.build_dataset import (
    EXPECTED_SEED,
    OFFICIAL_SPLITS,
    build_all_splits,
    build_question,
    project_root,
)
from finevid_distill.data.finqa import FINQA_COMMIT, load_split


TOP_LEVEL_FIELDS = {
    "question_id",
    "report_id",
    "question",
    "candidates",
    "positive_candidate_ids",
}
CANDIDATE_FIELDS = {"candidate_id", "text", "source_type", "source_index"}
FORBIDDEN_MODEL_FIELDS = {
    "answer",
    "exe_ans",
    "program",
    "program_re",
    "gold_inds",
    "steps",
}
FATAL_ISSUES = {
    "candidate_count_mismatch",
    "candidate_provenance_mismatch",
    "duplicate_candidate_ids",
    "duplicate_question_ids",
    "empty_candidates",
    "forbidden_model_fields",
    "inconsistent_table_formatting",
    "missing_processed_questions",
    "non_deterministic_regeneration",
    "official_order_mismatch",
    "program_literal_leakage",
    "answer_exact_field_leakage",
    "split_question_id_overlap",
    "split_report_id_overlap",
    "unexpected_processed_questions",
    "unmapped_gold_evidence",
    "zero_positive_questions",
}


class DatasetValidationError(RuntimeError):
    """Raised when one or more fatal dataset checks fail."""


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load one processed JSONL file with useful line-level errors."""
    records = []
    with Path(path).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise DatasetValidationError(
                    f"Invalid JSON in {path} at line {line_number}: {error}"
                ) from error
    return records


def _normalise_text(value: Any) -> str:
    return " ".join(str(value).casefold().split())


def _percentile(values: list[int], probability: float) -> float:
    """Return a linearly interpolated percentile without extra dependencies."""
    ordered = sorted(values)
    if not ordered:
        return math.nan
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _count_summary(values: list[int]) -> dict[str, float | int]:
    return {
        "count": len(values),
        "min": min(values),
        "p01": round(_percentile(values, 0.01), 3),
        "p25": round(_percentile(values, 0.25), 3),
        "median": round(_percentile(values, 0.50), 3),
        "p75": round(_percentile(values, 0.75), 3),
        "p99": round(_percentile(values, 0.99), 3),
        "max": max(values),
        "mean": round(sum(values) / len(values), 3),
    }


def _add_issue(
    issue_counts: Counter[str],
    issue_samples: dict[str, list[dict[str, Any]]],
    issue: str,
    detail: Mapping[str, Any],
) -> None:
    issue_counts[issue] += 1
    if len(issue_samples[issue]) < 20:
        issue_samples[issue].append(dict(detail))


def _forbidden_fields(record: Mapping[str, Any]) -> list[str]:
    found = set(record) & FORBIDDEN_MODEL_FIELDS
    for candidate in record.get("candidates", []):
        found.update(set(candidate) & FORBIDDEN_MODEL_FIELDS)
    return sorted(found)


def _leakage_diagnostics(
    raw: Mapping[str, Any], processed: Mapping[str, Any]
) -> tuple[bool, bool, bool, bool]:
    """Return program, answer, and known raw-annotation diagnostic signals.

    Exact source provenance is checked separately. Answer substrings inside source
    evidence are expected and are reported only as a diagnostic, not leakage.
    """
    question_input = _normalise_text(processed.get("question", ""))
    candidate_inputs = [
        candidate.get("text", "") for candidate in processed.get("candidates", [])
    ]
    normalised_candidates = [_normalise_text(value) for value in candidate_inputs]
    normalised_inputs = [question_input, *normalised_candidates]

    program = _normalise_text(raw["qa"].get("program", ""))
    program_literal = bool(program) and any(program in text for text in normalised_inputs)

    answers = {
        _normalise_text(raw["qa"].get(field, ""))
        for field in ("answer", "exe_ans")
    }
    answers.discard("")
    answer_exact = any(
        answer == text for answer in answers for text in normalised_candidates
    )
    answer_substring = any(
        answer in text for answer in answers for text in normalised_inputs if answer
    )
    raw_answer_equals_question = _normalise_text(raw["qa"].get("answer", "")) == (
        question_input
    )
    return program_literal, answer_exact, answer_substring, raw_answer_equals_question


def _write_json(payload: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manual_case_markdown(
    number: int,
    split: str,
    raw: Mapping[str, Any],
    processed: Mapping[str, Any],
    rng: random.Random,
) -> str:
    candidate_lookup = {
        candidate["candidate_id"]: candidate
        for candidate in processed["candidates"]
    }
    positives = [
        candidate_lookup[positive_id]
        for positive_id in processed["positive_candidate_ids"]
    ]
    positive_ids = set(processed["positive_candidate_ids"])
    negatives = [
        candidate
        for candidate in processed["candidates"]
        if candidate["candidate_id"] not in positive_ids
    ]
    sampled_negatives = rng.sample(negatives, 5)

    lines = [
        f"## {number:03d}. [{split}] `{processed['question_id']}`",
        "",
        f"**Question:** {processed['question']}",
        "",
        "**Mapped positives:**",
        "",
    ]
    lines.extend(
        f"- `{candidate['candidate_id']}` "
        f"({candidate['source_type']}[{candidate['source_index']}]): "
        f"{candidate['text']}"
        for candidate in positives
    )
    lines.extend(["", "**Five negative candidates:**", ""])
    lines.extend(
        f"- `{candidate['candidate_id']}` "
        f"({candidate['source_type']}[{candidate['source_index']}]): "
        f"{candidate['text']}"
        for candidate in sampled_negatives
    )
    lines.extend(
        [
            "",
            "**Original gold annotations:**",
            "",
            "```json",
            json.dumps(raw["qa"]["gold_inds"], indent=2, ensure_ascii=False),
            "```",
            "",
            "**Mapping check:** PASS — every annotation maps to the displayed positive ID.",
            "",
        ]
    )
    return "\n".join(lines)


def write_manual_inspection(
    raw_dir: str | Path,
    processed_dir: str | Path,
    destination: Path,
    eligible_ids: list[tuple[str, str]],
    *,
    seed: int,
    review_complete: bool,
) -> dict[str, Any]:
    """Write a deterministic 100-record review packet from train and dev only."""
    rng = random.Random(seed)
    sample_size = min(100, len(eligible_ids))
    selected = rng.sample(eligible_ids, sample_size)
    selected_positions = {key: index for index, key in enumerate(selected)}
    cases: list[tuple[int, str]] = []

    for split in ("train", "dev"):
        raw_records = load_split(raw_dir, split)
        processed_records = load_jsonl(Path(processed_dir) / f"{split}.jsonl")
        for raw, processed in zip(raw_records, processed_records):
            key = (split, processed["question_id"])
            if key not in selected_positions:
                continue
            position = selected_positions[key]
            cases.append(
                (
                    position,
                    _manual_case_markdown(
                        position + 1, split, raw, processed, rng
                    ),
                )
            )

    status = (
        f"COMPLETE — {sample_size}/{sample_size} examples reviewed"
        if review_complete
        else "PENDING"
    )
    header = "\n".join(
        [
            "# FinQA ranking-data manual inspection (seed 42)",
            "",
            f"**Review status:** {status}",
            "",
            "This deterministic packet samples 100 train/development examples. "
            "The test split is excluded from qualitative inspection. Each case "
            "shows the question, every mapped positive, five negatives, and the "
            "untouched `qa.gold_inds` mapping.",
            "",
        ]
    )
    body = "\n".join(case for _, case in sorted(cases))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(header + body, encoding="utf-8")
    return {
        "path": destination.as_posix(),
        "sample_size": len(cases),
        "seed": seed,
        "eligible_splits": ["train", "dev"],
        "status": "complete" if review_complete else "pending",
    }


def validate_dataset(
    raw_dir: str | Path,
    processed_dir: str | Path,
    *,
    statistics_path: str | Path,
    manual_inspection_path: str | Path,
    seed: int = EXPECTED_SEED,
    manual_review_complete: bool = False,
) -> dict[str, Any]:
    """Run all Milestone 4 checks and write deterministic audit artifacts."""
    if seed != EXPECTED_SEED:
        raise ValueError(f"The beginner experiment seed must be {EXPECTED_SEED}.")

    issue_counts: Counter[str] = Counter()
    issue_samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    split_statistics: dict[str, dict[str, Any]] = {}
    candidate_counts_by_split: dict[str, list[int]] = {}
    question_ids_by_split: dict[str, set[str]] = {}
    report_ids_by_split: dict[str, set[str]] = {}
    question_text_by_split: dict[str, set[str]] = {}
    eligible_manual_ids: list[tuple[str, str]] = []
    duplicate_text_questions = 0
    duplicate_text_instances = 0
    duplicate_text_samples: list[dict[str, Any]] = []
    gold_annotations = 0
    mapped_gold_annotations = 0
    program_literal_occurrences = 0
    answer_exact_occurrences = 0
    answer_substring_source_occurrences = 0
    raw_answer_equals_question_occurrences = 0

    for split in OFFICIAL_SPLITS:
        raw_records = load_split(raw_dir, split)
        processed_path = Path(processed_dir) / f"{split}.jsonl"
        processed_records = load_jsonl(processed_path)
        raw_ids = [record["id"] for record in raw_records]
        processed_ids = [record.get("question_id") for record in processed_records]

        if len(raw_records) != len(processed_records):
            _add_issue(
                issue_counts,
                issue_samples,
                "missing_processed_questions",
                {"split": split, "raw": len(raw_records), "processed": len(processed_records)},
            )
        if raw_ids != processed_ids:
            _add_issue(
                issue_counts,
                issue_samples,
                "official_order_mismatch",
                {"split": split},
            )

        raw_by_id = {record["id"]: record for record in raw_records}
        missing_ids = sorted(set(raw_ids) - set(processed_ids))
        unexpected_ids = sorted(set(processed_ids) - set(raw_ids))
        for question_id in missing_ids:
            _add_issue(
                issue_counts,
                issue_samples,
                "missing_processed_questions",
                {"split": split, "question_id": question_id},
            )
        for question_id in unexpected_ids:
            _add_issue(
                issue_counts,
                issue_samples,
                "unexpected_processed_questions",
                {"split": split, "question_id": question_id},
            )

        id_counts = Counter(processed_ids)
        for question_id, count in id_counts.items():
            if count > 1:
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "duplicate_question_ids",
                    {"split": split, "question_id": question_id, "count": count},
                )

        split_candidate_counts: list[int] = []
        for processed in processed_records:
            question_id = processed.get("question_id")
            raw = raw_by_id.get(question_id)
            if raw is None:
                continue
            expected = build_question(raw)
            candidates = processed.get("candidates", [])
            positives = processed.get("positive_candidate_ids", [])
            split_candidate_counts.append(len(candidates))

            extra_top_fields = set(processed) - TOP_LEVEL_FIELDS
            missing_top_fields = TOP_LEVEL_FIELDS - set(processed)
            forbidden = _forbidden_fields(processed)
            if forbidden or extra_top_fields & FORBIDDEN_MODEL_FIELDS:
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "forbidden_model_fields",
                    {"split": split, "question_id": question_id, "fields": forbidden},
                )
            if missing_top_fields:
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "candidate_provenance_mismatch",
                    {"split": split, "question_id": question_id, "missing_fields": sorted(missing_top_fields)},
                )

            if not candidates or any(not candidate.get("text", "").strip() for candidate in candidates):
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "empty_candidates",
                    {"split": split, "question_id": question_id},
                )
            if not positives:
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "zero_positive_questions",
                    {"split": split, "question_id": question_id},
                )

            candidate_ids = [candidate.get("candidate_id") for candidate in candidates]
            duplicate_candidate_ids = [
                candidate for candidate, count in Counter(candidate_ids).items() if count > 1
            ]
            if duplicate_candidate_ids:
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "duplicate_candidate_ids",
                    {"split": split, "question_id": question_id, "ids": duplicate_candidate_ids},
                )

            available_ids = set(candidate_ids)
            expected_positives = expected["positive_candidate_ids"]
            gold_annotations += len(raw["qa"]["gold_inds"])
            mapped_gold_annotations += sum(
                positive in available_ids and positive in positives
                for positive in expected_positives
            )
            mapping_valid = not (
                any(positive not in available_ids for positive in positives)
                or positives != expected_positives
            )
            if not mapping_valid:
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "unmapped_gold_evidence",
                    {
                        "split": split,
                        "question_id": question_id,
                        "expected": expected_positives,
                        "actual": positives,
                    },
                )

            if len(candidates) != len(expected["candidates"]):
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "candidate_count_mismatch",
                    {
                        "split": split,
                        "question_id": question_id,
                        "expected": len(expected["candidates"]),
                        "actual": len(candidates),
                    },
                )

            expected_by_id = {
                candidate["candidate_id"]: candidate
                for candidate in expected["candidates"]
            }
            for candidate in candidates:
                candidate_key = candidate.get("candidate_id")
                expected_candidate = expected_by_id.get(candidate_key)
                if set(candidate) != CANDIDATE_FIELDS or expected_candidate is None:
                    _add_issue(
                        issue_counts,
                        issue_samples,
                        "candidate_provenance_mismatch",
                        {"split": split, "question_id": question_id, "candidate_id": candidate_key},
                    )
                    continue
                if candidate != expected_candidate:
                    issue = (
                        "inconsistent_table_formatting"
                        if candidate.get("source_type") == "table"
                        and candidate.get("text") != expected_candidate.get("text")
                        else "candidate_provenance_mismatch"
                    )
                    _add_issue(
                        issue_counts,
                        issue_samples,
                        issue,
                        {"split": split, "question_id": question_id, "candidate_id": candidate_key},
                    )

            if (
                processed.get("question") != expected["question"]
                or processed.get("report_id") != expected["report_id"]
            ):
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "candidate_provenance_mismatch",
                    {"split": split, "question_id": question_id, "field": "question_or_report_id"},
                )

            text_counts = Counter(candidate.get("text", "") for candidate in candidates)
            duplicates = {text: count for text, count in text_counts.items() if count > 1}
            if duplicates:
                duplicate_text_questions += 1
                duplicate_text_instances += sum(count - 1 for count in duplicates.values())
                if len(duplicate_text_samples) < 20:
                    duplicate_text_samples.append(
                        {
                            "split": split,
                            "question_id": question_id,
                            "duplicates": dict(list(duplicates.items())[:5]),
                        }
                    )

            (
                program_literal,
                answer_exact,
                answer_substring,
                raw_answer_equals_question,
            ) = _leakage_diagnostics(raw, processed)
            program_literal_occurrences += int(program_literal)
            answer_exact_occurrences += int(answer_exact)
            answer_substring_source_occurrences += int(answer_substring)
            raw_answer_equals_question_occurrences += int(raw_answer_equals_question)
            if program_literal:
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "program_literal_leakage",
                    {"split": split, "question_id": question_id},
                )
            if answer_exact:
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "answer_exact_field_leakage",
                    {"split": split, "question_id": question_id},
                )

            negative_count = len(candidates) - len(set(positives))
            if split in {"train", "dev"} and negative_count >= 5 and mapping_valid:
                eligible_manual_ids.append((split, question_id))

        question_ids_by_split[split] = set(processed_ids)
        report_ids_by_split[split] = {
            record.get("report_id") for record in processed_records
        }
        question_text_by_split[split] = {
            _normalise_text(record.get("question", "")) for record in processed_records
        }
        candidate_counts_by_split[split] = split_candidate_counts
        split_statistics[split] = {
            "raw_questions": len(raw_records),
            "processed_questions": len(processed_records),
            "unique_question_ids": len(set(processed_ids)),
            "unique_reports": len(report_ids_by_split[split]),
            "total_candidates": sum(split_candidate_counts),
            "candidate_counts": _count_summary(split_candidate_counts),
        }

    overlaps: dict[str, dict[str, Any]] = {}
    for left, right in (("train", "dev"), ("train", "test"), ("dev", "test")):
        pair = f"{left}__{right}"
        question_id_overlap = sorted(question_ids_by_split[left] & question_ids_by_split[right])
        report_id_overlap = sorted(report_ids_by_split[left] & report_ids_by_split[right])
        question_text_overlap = sorted(
            question_text_by_split[left] & question_text_by_split[right]
        )
        overlaps[pair] = {
            "question_id_count": len(question_id_overlap),
            "report_id_count": len(report_id_overlap),
            "normalised_question_text_count": len(question_text_overlap),
            "normalised_question_text_samples": question_text_overlap[:20],
        }
        if question_id_overlap:
            _add_issue(
                issue_counts,
                issue_samples,
                "split_question_id_overlap",
                {"pair": pair, "sample": question_id_overlap[:20]},
            )
        if report_id_overlap:
            _add_issue(
                issue_counts,
                issue_samples,
                "split_report_id_overlap",
                {"pair": pair, "sample": report_id_overlap[:20]},
            )

    anomaly_rows = []
    for split, values in candidate_counts_by_split.items():
        q1 = _percentile(values, 0.25)
        q3 = _percentile(values, 0.75)
        upper_fence = q3 + 3 * (q3 - q1)
        processed_records = load_jsonl(Path(processed_dir) / f"{split}.jsonl")
        for record, count in zip(processed_records, values):
            if count > upper_fence:
                anomaly_rows.append(
                    {
                        "split": split,
                        "question_id": record["question_id"],
                        "candidate_count": count,
                        "upper_outer_fence": round(upper_fence, 3),
                    }
                )

    reproducibility: dict[str, dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="finevid-regeneration-") as temporary_dir:
        regenerated = build_all_splits(raw_dir, temporary_dir, seed=seed)
        for split in OFFICIAL_SPLITS:
            current_digest = _sha256_file(Path(processed_dir) / f"{split}.jsonl")
            regenerated_digest = regenerated[split]["sha256"]
            matches = current_digest == regenerated_digest
            reproducibility[split] = {
                "current_sha256": current_digest,
                "regenerated_sha256": regenerated_digest,
                "identical": matches,
            }
            if not matches:
                _add_issue(
                    issue_counts,
                    issue_samples,
                    "non_deterministic_regeneration",
                    {"split": split},
                )

    manual_result = write_manual_inspection(
        raw_dir,
        processed_dir,
        Path(manual_inspection_path),
        eligible_manual_ids,
        seed=seed,
        review_complete=manual_review_complete,
    )

    fatal_counts = {
        issue: issue_counts.get(issue, 0) for issue in sorted(FATAL_ISSUES)
    }
    valid = not any(fatal_counts.values()) and mapped_gold_annotations == gold_annotations
    statistics: dict[str, Any] = {
        "schema_version": 1,
        "source": {
            "dataset": "FinQA",
            "official_commit": FINQA_COMMIT,
            "seed": seed,
        },
        "valid": valid,
        "splits": split_statistics,
        "gold_mapping": {
            "annotations": gold_annotations,
            "mapped": mapped_gold_annotations,
            "percentage": round(100 * mapped_gold_annotations / gold_annotations, 6),
        },
        "fatal_issue_counts": fatal_counts,
        "issue_samples": {key: value for key, value in sorted(issue_samples.items())},
        "duplicate_candidate_text": {
            "classification": "reported_source_property_not_removed",
            "questions_with_duplicates": duplicate_text_questions,
            "repeated_instances_beyond_first": duplicate_text_instances,
            "samples": duplicate_text_samples,
        },
        "candidate_count_anomalies": {
            "rule": "above split Q3 + 3*IQR",
            "count": len(anomaly_rows),
            "samples": anomaly_rows[:100],
        },
        "reproducibility": reproducibility,
        "leakage": {
            "detected": bool(
                issue_counts["forbidden_model_fields"]
                or issue_counts["candidate_provenance_mismatch"]
                or program_literal_occurrences
                or answer_exact_occurrences
            ),
            "forbidden_field_occurrences": issue_counts["forbidden_model_fields"],
            "program_literal_occurrences": program_literal_occurrences,
            "answer_exact_field_occurrences": answer_exact_occurrences,
            "natural_answer_substring_source_occurrences": answer_substring_source_occurrences,
            "raw_answer_equals_question_occurrences": raw_answer_equals_question_occurrences,
            "note": (
                "Answer substrings naturally present in source evidence are diagnostic only; "
                "the raw answer/question duplication is a source annotation anomaly; exact "
                "source provenance proves no answer metadata was injected."
            ),
        },
        "split_overlap": overlaps,
        "manual_inspection": manual_result,
    }
    _write_json(statistics, Path(statistics_path))
    if not valid:
        failures = {key: value for key, value in fatal_counts.items() if value}
        raise DatasetValidationError(f"Dataset validation failed: {failures}")
    return statistics


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=root / "data" / "raw")
    parser.add_argument(
        "--processed-dir", type=Path, default=root / "data" / "processed"
    )
    parser.add_argument(
        "--statistics-path",
        type=Path,
        default=root / "outputs" / "data_statistics.json",
    )
    parser.add_argument(
        "--manual-inspection-path",
        type=Path,
        default=root / "outputs" / "manual_inspection_100.md",
    )
    parser.add_argument("--seed", type=int, default=EXPECTED_SEED)
    parser.add_argument(
        "--manual-review-complete",
        action="store_true",
        help="Mark the generated review packet complete after all 100 cases are reviewed.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    statistics = validate_dataset(
        args.raw_dir,
        args.processed_dir,
        statistics_path=args.statistics_path,
        manual_inspection_path=args.manual_inspection_path,
        seed=args.seed,
        manual_review_complete=args.manual_review_complete,
    )
    print(
        f"Validation passed: {statistics['gold_mapping']['mapped']:,} / "
        f"{statistics['gold_mapping']['annotations']:,} gold annotations mapped."
    )
    print(f"Statistics: {args.statistics_path}")
    print(f"Manual inspection packet: {args.manual_inspection_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
