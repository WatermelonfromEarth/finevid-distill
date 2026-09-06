import csv
from collections import Counter
from pathlib import Path

from finevid_distill.evaluation.error_analysis import ERROR_MODEL_LABELS, FAILURE_CATEGORIES


ROOT = Path(__file__).resolve().parents[1]


def test_completed_error_analysis_has_80_reviewed_failures() -> None:
    path = ROOT / "outputs/error_analysis.csv"
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))

    assert len(rows) == 80
    assert [int(row["review_order"]) for row in rows] == list(range(1, 81))
    assert len({row["instance_id"] for row in rows}) == 80
    assert Counter(row["failure_model"] for row in rows) == {
        label: 20 for label in ERROR_MODEL_LABELS
    }
    assert all(row["primary_category"] in FAILURE_CATEGORIES for row in rows)
    assert all(row["review_note"].strip() for row in rows)
    assert all(row["missing_gold_ids_at_5"].strip() for row in rows)


def test_error_analysis_category_counts_are_frozen() -> None:
    path = ROOT / "outputs/error_analysis.csv"
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))

    observed = Counter(
        (row["failure_model"], row["primary_category"]) for row in rows
    )
    expected = {
        ("Frozen BGE", "incomplete multi-fact retrieval"): 5,
        ("Frozen BGE", "ambiguous annotation"): 10,
        ("Frozen BGE", "wrong financial metric"): 3,
        ("Frozen BGE", "missed table evidence"): 1,
        ("Frozen BGE", "missed prose evidence"): 1,
        ("Hard-label BGE", "ambiguous annotation"): 12,
        ("Hard-label BGE", "wrong year"): 3,
        ("Hard-label BGE", "incomplete multi-fact retrieval"): 2,
        ("Hard-label BGE", "wrong financial metric"): 3,
        ("Distilled BGE", "wrong financial metric"): 1,
        ("Distilled BGE", "teacher error"): 6,
        ("Distilled BGE", "ambiguous annotation"): 11,
        ("Distilled BGE", "missed table evidence"): 2,
        ("Qwen teacher", "incomplete multi-fact retrieval"): 5,
        ("Qwen teacher", "missed table evidence"): 1,
        ("Qwen teacher", "ambiguous annotation"): 13,
        ("Qwen teacher", "excessive lexical matching"): 1,
    }
    assert observed == Counter(expected)


def test_error_analysis_report_states_distillation_findings() -> None:
    report = (ROOT / "docs/error_analysis.md").read_text(encoding="utf-8")
    assert "## Effects of distillation" in report
    assert "Six of the 20 sampled distilled failures" in report
    assert "does not improve BGE-small beyond ordinary hard-label fine-tuning" in report
