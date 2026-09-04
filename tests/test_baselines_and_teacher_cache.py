import json
from pathlib import Path

import pytest

from finevid_distill.data.cache_teacher_scores import (
    cache_split,
    validate_teacher_cache,
)
from finevid_distill.evaluation.evaluate import evaluate_ranker, format_markdown_table
from finevid_distill.models.bm25_ranker import BM25Ranker
from finevid_distill.models.random_ranker import RandomRanker


def example_records() -> list[dict]:
    return [
        {
            "question_id": "report-1-1",
            "report_id": "report-1",
            "question": "revenue increase",
            "candidates": [
                {"candidate_id": "pre-text-0", "text": "unrelated expenses"},
                {"candidate_id": "table-row-1", "text": "revenue increase 20 percent"},
            ],
            "positive_candidate_ids": ["table-row-1"],
        },
        {
            "question_id": "report-2-1",
            "report_id": "report-2",
            "question": "cash flow",
            "candidates": [
                {"candidate_id": "pre-text-0", "text": "cash flow improved"},
                {"candidate_id": "post-text-0", "text": "tax rate"},
            ],
            "positive_candidate_ids": ["pre-text-0"],
        },
    ]


class FakeTeacher:
    def score_pairs(self, pairs, *, batch_size, show_progress):
        del batch_size, show_progress
        return [float(index) - 2.5 for index, _ in enumerate(pairs)]


def test_random_ranker_is_seeded_and_order_independent_by_question() -> None:
    records = example_records()
    ranker = RandomRanker(42)

    scores = ranker.score_records(records)
    reordered_scores = ranker.score_records(list(reversed(records)))

    assert scores == list(reversed(reordered_scores))
    assert scores == RandomRanker(42).score_records(records)
    assert scores != RandomRanker(43).score_records(records)


def test_bm25_and_evaluator_use_shared_metrics() -> None:
    results = evaluate_ranker(example_records(), BM25Ranker())

    # With two documents BM25's matching-term IDF is zero, so stable input-order
    # tie-breaking places one of the two positives second.
    assert results["recall_at_1"] == 0.5
    assert results["recall_at_5"] == 1.0
    assert results["mrr"] == 0.75
    assert results["ndcg_at_10"] == pytest.approx((1.0 + 1 / 1.584962500721156) / 2)
    assert results["complete_recall_at_5"] == 1.0
    table = format_markdown_table({"BM25": results})
    assert "| Model | Recall@1 | Recall@5 | MRR | NDCG@10 | CompleteRecall@5 |" in table


def test_teacher_cache_round_trip_and_validation(tmp_path: Path) -> None:
    records = example_records()
    destination = tmp_path / "teacher_dev_scores.jsonl"

    stats = cache_split(
        records,
        destination,
        FakeTeacher(),
        batch_size=2,
        pair_chunk_size=2,
    )

    assert stats == {"questions": 2, "candidates": 4}
    rows = [json.loads(line) for line in destination.read_text().splitlines()]
    assert rows[0]["candidate_ids"] == ["pre-text-0", "table-row-1"]
    assert rows[0]["score_type"] == "raw_logit_difference"
    assert rows[0]["temperature_applied"] is False
    assert validate_teacher_cache(destination, records) == stats


def test_resume_discards_only_a_truncated_final_row(tmp_path: Path) -> None:
    records = example_records()
    partial = tmp_path / "teacher_dev_scores.jsonl.partial"
    complete_first_row = {
        "question_id": records[0]["question_id"],
        "candidate_ids": ["pre-text-0", "table-row-1"],
        "teacher_scores": [0.0, 1.0],
        "score_type": "raw_logit_difference",
        "temperature_applied": False,
    }
    partial.write_bytes(
        (json.dumps(complete_first_row) + "\n" + '{"question_id":"broken').encode()
    )

    stats = validate_teacher_cache(partial, records, allow_prefix=True)

    assert stats == {"questions": 1, "candidates": 2}
    assert partial.read_text(encoding="utf-8") == json.dumps(complete_first_row) + "\n"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("candidate_ids", ["table-row-1", "pre-text-0"], "ordering"),
        ("teacher_scores", [1.0], "count"),
        ("teacher_scores", [1.0, float("inf")], "finite"),
        ("score_type", "probability", "raw logit"),
        ("temperature_applied", True, "Temperature"),
    ],
)
def test_teacher_cache_rejects_corruption(
    tmp_path: Path, field: str, value, message: str
) -> None:
    records = example_records()[:1]
    destination = tmp_path / "cache.jsonl"
    row = {
        "question_id": records[0]["question_id"],
        "candidate_ids": ["pre-text-0", "table-row-1"],
        "teacher_scores": [0.0, 1.0],
        "score_type": "raw_logit_difference",
        "temperature_applied": False,
    }
    row[field] = value
    destination.write_text(json.dumps(row) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        validate_teacher_cache(destination, records)
