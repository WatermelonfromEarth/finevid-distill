import json
from pathlib import Path

import pytest

from finevid_distill.data.build_training_rows import (
    build_training_row,
    build_training_rows,
    validate_training_rows,
)


def source_record(*, positive_ids: list[str] | None = None) -> dict:
    candidates = [
        {"candidate_id": f"candidate-{index}", "text": f"evidence {index}"}
        for index in range(12)
    ]
    return {
        "question_id": "report-1-1",
        "report_id": "report-1",
        "question": "What changed?",
        "candidates": candidates,
        "positive_candidate_ids": positive_ids or ["candidate-2", "candidate-7"],
    }


def teacher_cache(record: dict) -> dict:
    candidate_ids = [candidate["candidate_id"] for candidate in record["candidates"]]
    return {
        "question_id": record["question_id"],
        "candidate_ids": candidate_ids,
        "teacher_scores": [index - 5.5 for index in range(len(candidate_ids))],
        "score_type": "raw_logit_difference",
        "temperature_applied": False,
    }


def test_fixed_row_retains_all_gold_and_aligns_every_field() -> None:
    record = source_record()
    cache = teacher_cache(record)

    row = build_training_row(record, cache, seed=42, target_candidates=8)

    assert len(row["candidate_ids"]) == 8
    assert sum(row["positive_mask"]) == 2
    assert {
        candidate_id
        for candidate_id, positive in zip(
            row["candidate_ids"], row["positive_mask"], strict=True
        )
        if positive
    } == set(record["positive_candidate_ids"])
    candidate_by_id = {
        candidate["candidate_id"]: candidate for candidate in record["candidates"]
    }
    score_by_id = dict(zip(cache["candidate_ids"], cache["teacher_scores"], strict=True))
    for candidate_id, text, score in zip(
        row["candidate_ids"],
        row["candidate_texts"],
        row["teacher_scores"],
        strict=True,
    ):
        assert text == candidate_by_id[candidate_id]["text"]
        assert score == score_by_id[candidate_id]


def test_sampling_and_shuffle_are_deterministic_per_question() -> None:
    record = source_record()
    cache = teacher_cache(record)

    first = build_training_row(record, cache, seed=42)
    second = build_training_row(record, cache, seed=42)
    changed_seed = build_training_row(record, cache, seed=43)

    assert first == second
    assert first["candidate_ids"] != changed_seed["candidate_ids"]


def test_more_than_eight_gold_facts_are_all_retained() -> None:
    positives = [f"candidate-{index}" for index in range(10)]
    record = source_record(positive_ids=positives)

    row = build_training_row(record, teacher_cache(record), target_candidates=8)

    assert len(row["candidate_ids"]) == 10
    assert sum(row["positive_mask"]) == 10
    assert set(row["candidate_ids"]) == set(positives)


def test_build_is_byte_identical_and_validated(tmp_path: Path) -> None:
    record = source_record()
    cache = teacher_cache(record)
    first_path = tmp_path / "first.jsonl"
    second_path = tmp_path / "second.jsonl"

    first = build_training_rows([record], [cache], first_path, seed=42)
    second = build_training_rows([record], [cache], second_path, seed=42)

    assert first_path.read_bytes() == second_path.read_bytes()
    assert first["sha256"] == second["sha256"]
    assert first["questions"] == 1
    assert first["candidates"] == 8
    assert validate_training_rows(first_path, [record], [cache])["questions"] == 1


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda cache: cache.update(candidate_ids=list(reversed(cache["candidate_ids"]))), "ordering"),
        (lambda cache: cache.update(teacher_scores=[float("inf")] * 12), "Non-finite"),
        (lambda cache: cache.update(temperature_applied=True), "temperature"),
    ],
)
def test_source_cache_corruption_is_rejected(mutation, message: str) -> None:
    record = source_record()
    cache = teacher_cache(record)
    mutation(cache)

    with pytest.raises(ValueError, match=message):
        build_training_row(record, cache)


def test_validator_rejects_teacher_score_misalignment(tmp_path: Path) -> None:
    record = source_record()
    cache = teacher_cache(record)
    destination = tmp_path / "rows.jsonl"
    build_training_rows([record], [cache], destination)
    row = json.loads(destination.read_text(encoding="utf-8"))
    row["teacher_scores"] = list(reversed(row["teacher_scores"]))
    destination.write_text(json.dumps(row) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="score ordering"):
        validate_training_rows(destination, [record], [cache])


def test_zero_positive_question_is_rejected() -> None:
    record = source_record()
    record["positive_candidate_ids"] = []

    with pytest.raises(ValueError, match="no positive"):
        build_training_row(record, teacher_cache(record))
