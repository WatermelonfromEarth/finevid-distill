import ast
import json
from pathlib import Path

import pytest
import torch

from finevid_distill.data import cache_teacher_scores
from finevid_distill.evaluation.benchmark_efficiency import (
    build_benchmark_sample,
    format_quality_efficiency_table,
    model_statistics,
)
from finevid_distill.evaluation.final_comparison import (
    FINAL_MODEL_LABELS,
    build_final_payload,
    evaluate_final_rankers,
)
from finevid_distill.evaluation.final_selection import (
    EXPECTED_TEST_DATA_SHA256,
    EXPECTED_TEST_QUESTIONS,
    EXPECTED_TRAINING_BUNDLE_SHA256,
    validate_selection_document,
)


ROOT = Path(__file__).resolve().parents[1]


def metric_row(value: float) -> dict[str, float]:
    return {
        "recall_at_1": value,
        "recall_at_5": value,
        "mrr": value,
        "ndcg_at_10": value,
        "complete_recall_at_5": value,
    }


class FixedRanker:
    def __init__(self, label: str) -> None:
        self.label = label

    def score_records(self, records):
        return [[float(len(record["candidates"]) - index) for index, _ in enumerate(record["candidates"])]
                for record in records]


def test_frozen_selection_is_complete_and_precedes_test() -> None:
    selection = json.loads((ROOT / "outputs/final_selection.json").read_text())

    validate_selection_document(selection)

    assert selection["test_evaluated_at_freeze"] is False
    assert selection["test_data_sha256"] == EXPECTED_TEST_DATA_SHA256
    assert selection["test_question_count"] == EXPECTED_TEST_QUESTIONS
    assert selection["source_bundle_sha256"] == EXPECTED_TRAINING_BUNDLE_SHA256
    assert selection["models"]["hard_label"]["selected_epoch"] == 3
    assert selection["models"]["distilled"]["selected_epoch"] == 2


def test_final_rankers_use_one_shared_metric_path_and_locked_order() -> None:
    records = [{
        "question_id": "q1",
        "question": "question",
        "candidates": [{"candidate_id": "positive", "text": "yes"},
                       {"candidate_id": "negative", "text": "no"}],
        "positive_candidate_ids": ["positive"],
    }]
    rankers = [FixedRanker(label) for label in FINAL_MODEL_LABELS]

    results = evaluate_final_rankers(records, rankers)

    assert tuple(results) == FINAL_MODEL_LABELS
    assert all(values == metric_row(1.0) for values in results.values())


def test_final_payload_calculates_teacher_quality_retained() -> None:
    results = {label: metric_row(0.8) for label in FINAL_MODEL_LABELS}
    results["Distilled BGE"] = metric_row(0.6)
    results["Hard-label BGE"] = metric_row(0.7)

    payload = build_final_payload(
        results, question_count=EXPECTED_TEST_QUESTIONS, selection_sha256="a" * 64
    )

    assert payload["teacher_quality_retained"] == pytest.approx(0.75)
    assert payload["distilled_minus_hard_mrr"] == pytest.approx(-0.1)
    assert payload["distillation_improves_over_hard_label"] is False


def test_public_test_teacher_cache_requires_frozen_selection(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="final-selection"):
        cache_teacher_scores.main([
            "--splits", "test",
            "--processed-dir", str(tmp_path),
            "--output-dir", str(tmp_path),
            "--device", "cpu",
            "--allow-cpu",
        ])


def test_efficiency_helpers_measure_model_and_format_table() -> None:
    model = torch.nn.Linear(3, 2)
    stats = model_statistics(model)
    records = [{
        "question_id": "q1",
        "question": "question",
        "candidates": [
            {"candidate_id": "a", "text": "alpha"},
            {"candidate_id": "b", "text": "beta"},
            {"candidate_id": "c", "text": "gamma"},
        ],
    }]

    question_id, question, candidates, sample_hash = build_benchmark_sample(
        records, candidate_count=3
    )
    row = {
        **stats,
        "ndcg_at_10": 0.8,
        "peak_memory_bytes": 1024,
        "candidate_encoding_time_seconds": None,
        "query_latency_seconds": 0.001,
        "rank_100_time_seconds": 0.01,
        "candidates_per_second": 10_000.0,
    }

    assert stats["parameter_count"] == 8
    assert stats["model_size_bytes"] == 8 * 4
    assert (question_id, question, candidates) == ("q1", "question", ["alpha", "beta", "gamma"])
    assert len(sample_hash) == 64
    table = format_quality_efficiency_table({"Qwen teacher": row})
    assert "| Model | NDCG@10 | Parameters |" in table
    assert "| Qwen teacher | 0.800000 | 8 |" in table


def test_final_colab_notebook_keeps_selection_before_test_actions() -> None:
    notebook = json.loads((ROOT / "notebooks/05_colab_final_evaluation.ipynb").read_text())
    source = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
    required = (
        "frozen final selection", "final_selection.json", "teacher_test_scores.jsonl",
        "final_comparison.py", "benchmark_efficiency.py", "efficiency_results.json",
        "hard_label_student_tau005", "distilled_student",
    )
    assert all(text in source for text in required)
    assert source.index("final_selection.json") < source.index("teacher_test_scores.jsonl")
    assert notebook["metadata"]["accelerator"] == "GPU"
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell["execution_count"] is None
            assert cell["outputs"] == []
            python_source = "\n".join(
                line for line in "".join(cell["source"]).splitlines()
                if not line.startswith("%")
            )
            ast.parse(python_source)
