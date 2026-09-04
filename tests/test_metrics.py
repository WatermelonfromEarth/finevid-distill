import math

import pytest

from finevid_distill.evaluation.metrics import (
    complete_recall_at_k,
    mean_metrics,
    ndcg_at_k,
    rank_by_score,
    ranking_metrics,
    recall_at_k,
    reciprocal_rank,
)


def test_one_positive_ranked_first() -> None:
    metrics = ranking_metrics(["p", "n1", "n2"], ["p"])

    assert metrics == {
        "recall_at_1": 1.0,
        "recall_at_5": 1.0,
        "mrr": 1.0,
        "ndcg_at_10": 1.0,
        "complete_recall_at_5": 1.0,
    }


def test_one_positive_ranked_last() -> None:
    ranked = ["n1", "n2", "n3", "n4", "n5", "p"]

    assert recall_at_k(ranked, ["p"], 1) == 0.0
    assert recall_at_k(ranked, ["p"], 5) == 0.0
    assert reciprocal_rank(ranked, ["p"]) == pytest.approx(1 / 6)
    assert ndcg_at_k(ranked, ["p"], 10) == pytest.approx(1 / math.log2(7))
    assert complete_recall_at_k(ranked, ["p"], 5) == 0.0


def test_multiple_positives_partial_recall_is_not_complete_recall() -> None:
    ranked = ["n1", "p1", "n2", "n3", "n4", "p2"]
    ideal_dcg = 1 + 1 / math.log2(3)
    actual_dcg = 1 / math.log2(3) + 1 / math.log2(7)

    assert recall_at_k(ranked, ["p1", "p2"], 1) == 0.0
    assert recall_at_k(ranked, ["p1", "p2"], 5) == 0.5
    assert reciprocal_rank(ranked, ["p1", "p2"]) == 0.5
    assert ndcg_at_k(ranked, ["p1", "p2"], 10) == pytest.approx(
        actual_dcg / ideal_dcg
    )
    assert complete_recall_at_k(ranked, ["p1", "p2"], 5) == 0.0


def test_multiple_positives_all_in_first_five() -> None:
    ranked = ["n1", "p1", "n2", "p2", "n3", "n4"]

    assert recall_at_k(ranked, ["p1", "p2"], 5) == 1.0
    assert complete_recall_at_k(ranked, ["p1", "p2"], 5) == 1.0


def test_no_positive_is_retrieved() -> None:
    ranked = ["n1", "n2", "n3"]

    assert recall_at_k(ranked, ["missing"], 5) == 0.0
    assert reciprocal_rank(ranked, ["missing"]) == 0.0
    assert ndcg_at_k(ranked, ["missing"], 10) == 0.0
    assert complete_recall_at_k(ranked, ["missing"], 5) == 0.0


def test_ndcg_at_ten_handles_fewer_than_ten_candidates() -> None:
    ranked = ["n1", "p", "n2"]

    assert ndcg_at_k(ranked, ["p"], 10) == pytest.approx(1 / math.log2(3))


def test_tied_scores_preserve_original_candidate_order() -> None:
    candidate_ids = ["first", "second", "third", "fourth"]
    ranked = rank_by_score(candidate_ids, [0.5, 0.5, 0.8, 0.5])

    assert ranked == ["third", "first", "second", "fourth"]
    assert reciprocal_rank(ranked, ["second"]) == pytest.approx(1 / 3)


def test_macro_average_matches_hand_calculation() -> None:
    first = ranking_metrics(["p", "n"], ["p"])
    second = ranking_metrics(["n", "p"], ["p"])
    averaged = mean_metrics([first, second])

    assert averaged["recall_at_1"] == 0.5
    assert averaged["recall_at_5"] == 1.0
    assert averaged["mrr"] == 0.75
    assert averaged["ndcg_at_10"] == pytest.approx((1 + 1 / math.log2(3)) / 2)
    assert averaged["complete_recall_at_5"] == 1.0


@pytest.mark.parametrize("k", [0, -1])
def test_cutoffs_must_be_positive(k: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        recall_at_k(["p"], ["p"], k)


def test_invalid_scores_and_empty_gold_are_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        rank_by_score(["a"], [float("nan")])
    with pytest.raises(ValueError, match="positive candidate"):
        ranking_metrics(["a"], [])
