import ast
import json
from pathlib import Path

import pytest

from finevid_distill.evaluation.error_analysis import (
    ERROR_MODEL_LABELS,
    FAILURE_CATEGORIES,
    MAX_BGE_DEVICE_DRIFT_QUESTIONS,
    build_review_packet,
    load_score_cache,
    ranking_detail,
    select_failure_instances,
    validate_metric_reproduction,
    write_score_cache,
)
from finevid_distill.evaluation.metrics import mean_metrics


ROOT = Path(__file__).resolve().parents[1]


def record(question_id: str, positives: list[str]) -> dict:
    return {
        "question_id": question_id,
        "report_id": question_id.rpartition("-")[0],
        "question": f"Question {question_id}",
        "candidates": [
            {
                "candidate_id": candidate_id,
                "text": f"Evidence {candidate_id}",
                "source_type": "table" if candidate_id.startswith("p") else "pre_text",
                "source_index": index,
            }
            for index, candidate_id in enumerate(("n1", "n2", "p1", "p2"))
        ],
        "positive_candidate_ids": positives,
    }


def raw_record(processed: dict) -> dict:
    return {
        "id": processed["question_id"],
        "qa": {
            "question": processed["question"],
            "gold_inds": {"table_1": "gold"},
            "program": "subtract(1, 2)",
            "exe_ans": "-1",
        },
    }


def test_score_cache_round_trip_and_rejects_candidate_reordering(tmp_path) -> None:
    records = [record("report-1", ["p1"]), record("report-2", ["p2"])]
    scores = [[4.0, 3.0, 2.0, 1.0], [1.0, 2.0, 3.0, 4.0]]
    path = tmp_path / "scores.jsonl"

    write_score_cache(
        path,
        label="Frozen BGE",
        records=records,
        score_rows=scores,
        test_data_sha256="a" * 64,
        selection_sha256="b" * 64,
    )

    assert load_score_cache(
        path,
        label="Frozen BGE",
        records=records,
        test_data_sha256="a" * 64,
        selection_sha256="b" * 64,
    ) == scores

    lines = path.read_text().splitlines()
    changed = json.loads(lines[1])
    changed["candidate_ids"] = list(reversed(changed["candidate_ids"]))
    lines[1] = json.dumps(changed)
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(ValueError, match="ordering changed"):
        load_score_cache(
            path,
            label="Frozen BGE",
            records=records,
            test_data_sha256="a" * 64,
            selection_sha256="b" * 64,
        )


def test_ranking_detail_marks_incomplete_multi_fact_retrieval() -> None:
    item = record("report-1", ["p1", "p2"])
    detail = ranking_detail(item, [4.0, 3.0, 2.0, 1.0])

    assert detail["failed_complete_recall_at_5"] is False
    assert detail["first_gold_rank"] == 3
    assert detail["gold_ranks"] == {"p1": 3, "p2": 4}
    assert all("score" in candidate for candidate in detail["top_10"])


def test_packet_selects_equal_genuine_failures_and_reproduces_metrics() -> None:
    records = [record(f"report-{index}", ["p1"]) for index in range(1, 7)]
    # A positive score at p1 (index 2) puts the gold first; a negative score puts it last.
    success = [0.0, 0.0, 2.0, 0.0]
    failure = [4.0, 3.0, -1.0, 2.0]
    scores = {
        "Frozen BGE": [failure, failure, success, success, failure, success],
        "Hard-label BGE": [success, failure, success, failure, success, success],
        "Distilled BGE": [failure, success, success, failure, failure, success],
        "Qwen teacher": [failure, success, failure, success, success, success],
    }
    # With four candidates no CompleteRecall@5 failure is possible, so add five negatives.
    for item in records:
        for number in range(3, 8):
            item["candidates"].insert(
                number - 1,
                {
                    "candidate_id": f"n{number}",
                    "text": f"Evidence n{number}",
                    "source_type": "pre_text",
                    "source_index": number,
                },
            )
    success = [0.0] * 9
    success[7] = 2.0  # p1 after the inserted negatives
    failure = [float(9 - index) for index in range(9)]
    failure[7] = -1.0
    scores = {
        "Frozen BGE": [failure, failure, success, success, failure, success],
        "Hard-label BGE": [success, failure, success, failure, success, success],
        "Distilled BGE": [failure, success, success, failure, failure, success],
        "Qwen teacher": [failure, success, failure, success, success, success],
    }
    final_metrics = {
        label: mean_metrics(
            [ranking_detail(item, row)["metrics"] for item, row in zip(records, rows)]
        )
        for label, rows in scores.items()
    }

    packet = build_review_packet(
        records,
        [raw_record(item) for item in records],
        scores,
        final_metrics=final_metrics,
        test_data_sha256="a" * 64,
        selection_sha256="b" * 64,
        failures_per_model=2,
    )

    assert packet["review_instance_count"] == 8
    assert packet["categories"] == list(FAILURE_CATEGORIES)
    assert packet["full_test_failure_counts"] == {
        "Frozen BGE": 3,
        "Hard-label BGE": 2,
        "Distilled BGE": 3,
        "Qwen teacher": 2,
    }
    assert packet["review_ranking_failure_counts"] == packet["full_test_failure_counts"]
    assert all(
        delta == pytest.approx(0.0)
        for model_deltas in packet["metric_deltas_from_locked_final"].values()
        for delta in model_deltas.values()
    )
    assert [instance["failure_model"] for instance in packet["instances"]] == [
        label for label in ERROR_MODEL_LABELS for _ in range(2)
    ]
    assert all(
        instance["models"][instance["failure_model"]]["failed_complete_recall_at_5"]
        for instance in packet["instances"]
    )


def test_metric_reproduction_bounds_bge_device_drift_and_keeps_teacher_exact() -> None:
    question_count = 1_000
    expected = {"ndcg_at_10": 0.8}
    allowed = MAX_BGE_DEVICE_DRIFT_QUESTIONS / question_count

    deltas = validate_metric_reproduction(
        "Frozen BGE",
        {"ndcg_at_10": expected["ndcg_at_10"] + allowed * 0.999},
        expected,
        question_count,
    )
    assert deltas["ndcg_at_10"] == pytest.approx(allowed * 0.999)

    with pytest.raises(ValueError, match="device-drift bound"):
        validate_metric_reproduction(
            "Frozen BGE",
            {"ndcg_at_10": expected["ndcg_at_10"] + allowed + 1e-6},
            expected,
            question_count,
        )

    with pytest.raises(ValueError, match="device-drift bound"):
        validate_metric_reproduction(
            "Qwen teacher",
            {"ndcg_at_10": expected["ndcg_at_10"] + 1e-9},
            expected,
            question_count,
        )


def test_failure_sampler_rejects_nonpositive_or_oversized_requests() -> None:
    cases = [{"models": {label: {"failed_complete_recall_at_5": True}
                         for label in ERROR_MODEL_LABELS}}]
    with pytest.raises(ValueError, match="positive"):
        select_failure_instances(cases, failures_per_model=0)
    with pytest.raises(ValueError, match="Not enough"):
        select_failure_instances(cases, failures_per_model=2)


def test_error_analysis_notebook_uses_cached_teacher_and_no_training() -> None:
    notebook = json.loads((ROOT / "notebooks/06_colab_error_analysis.ipynb").read_text())
    source = "\n".join("".join(cell["source"]) for cell in notebook["cells"])

    assert "teacher_test_scores.jsonl" in source
    assert "prepare_error_analysis.py" in source
    assert "error_review_packet.json" in source
    assert "--failures-per-model', '20'" in source
    assert "train_hard_labels.py" not in source
    assert "train_distilled.py" not in source
    assert notebook["metadata"]["accelerator"] == "GPU"
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell["execution_count"] is None
            assert cell["outputs"] == []
            python_source = "\n".join(
                line
                for line in "".join(cell["source"]).splitlines()
                if not line.startswith("%")
            )
            ast.parse(python_source)
