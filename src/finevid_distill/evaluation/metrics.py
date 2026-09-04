"""Shared, deterministic ranking metrics for every experiment system."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


METRIC_NAMES = (
    "recall_at_1",
    "recall_at_5",
    "mrr",
    "ndcg_at_10",
    "complete_recall_at_5",
)


def _gold_set(positive_candidate_ids: Iterable[str]) -> set[str]:
    positives = set(positive_candidate_ids)
    if not positives:
        raise ValueError("At least one positive candidate ID is required.")
    return positives


def _validate_ranked_ids(ranked_candidate_ids: Sequence[str]) -> None:
    if len(ranked_candidate_ids) != len(set(ranked_candidate_ids)):
        raise ValueError("Ranked candidate IDs must be unique.")


def rank_by_score(
    candidate_ids: Sequence[str], scores: Sequence[float]
) -> list[str]:
    """Rank scores descending, resolving ties by original candidate order."""
    if len(candidate_ids) != len(scores):
        raise ValueError("Candidate and score counts must match.")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("Candidate IDs must be unique.")
    numeric_scores = [float(score) for score in scores]
    if not all(math.isfinite(score) for score in numeric_scores):
        raise ValueError("All ranking scores must be finite.")
    order = sorted(range(len(candidate_ids)), key=lambda index: -numeric_scores[index])
    return [candidate_ids[index] for index in order]


def recall_at_k(
    ranked_candidate_ids: Sequence[str],
    positive_candidate_ids: Iterable[str],
    k: int,
) -> float:
    """Return the fraction of required facts found in the first ``k`` results."""
    if k <= 0:
        raise ValueError("k must be positive.")
    _validate_ranked_ids(ranked_candidate_ids)
    positives = _gold_set(positive_candidate_ids)
    retrieved = set(ranked_candidate_ids[:k])
    return len(positives & retrieved) / len(positives)


def reciprocal_rank(
    ranked_candidate_ids: Sequence[str], positive_candidate_ids: Iterable[str]
) -> float:
    """Return reciprocal rank of the first retrieved positive, or zero."""
    _validate_ranked_ids(ranked_candidate_ids)
    positives = _gold_set(positive_candidate_ids)
    for rank, candidate_id in enumerate(ranked_candidate_ids, start=1):
        if candidate_id in positives:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(
    ranked_candidate_ids: Sequence[str],
    positive_candidate_ids: Iterable[str],
    k: int,
) -> float:
    """Return binary-relevance normalized discounted cumulative gain at ``k``."""
    if k <= 0:
        raise ValueError("k must be positive.")
    _validate_ranked_ids(ranked_candidate_ids)
    positives = _gold_set(positive_candidate_ids)
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, candidate_id in enumerate(ranked_candidate_ids[:k], start=1)
        if candidate_id in positives
    )
    ideal_hits = min(len(positives), k)
    ideal_dcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / ideal_dcg


def complete_recall_at_k(
    ranked_candidate_ids: Sequence[str],
    positive_candidate_ids: Iterable[str],
    k: int,
) -> float:
    """Return one only when every required fact occurs in the first ``k`` results."""
    if k <= 0:
        raise ValueError("k must be positive.")
    _validate_ranked_ids(ranked_candidate_ids)
    positives = _gold_set(positive_candidate_ids)
    return float(positives.issubset(set(ranked_candidate_ids[:k])))


def ranking_metrics(
    ranked_candidate_ids: Sequence[str], positive_candidate_ids: Iterable[str]
) -> dict[str, float]:
    """Compute the complete per-question Milestone 5 metric set."""
    positives = tuple(positive_candidate_ids)
    return {
        "recall_at_1": recall_at_k(ranked_candidate_ids, positives, 1),
        "recall_at_5": recall_at_k(ranked_candidate_ids, positives, 5),
        "mrr": reciprocal_rank(ranked_candidate_ids, positives),
        "ndcg_at_10": ndcg_at_k(ranked_candidate_ids, positives, 10),
        "complete_recall_at_5": complete_recall_at_k(
            ranked_candidate_ids, positives, 5
        ),
    }


def mean_metrics(per_question: Iterable[dict[str, float]]) -> dict[str, float]:
    """Macro-average per-question metric dictionaries."""
    rows = list(per_question)
    if not rows:
        raise ValueError("At least one per-question result is required.")
    for row in rows:
        if set(row) != set(METRIC_NAMES):
            raise ValueError(f"Metric row must contain exactly {METRIC_NAMES!r}.")
        if not all(math.isfinite(float(value)) for value in row.values()):
            raise ValueError("Metric values must be finite.")
    return {
        name: sum(float(row[name]) for row in rows) / len(rows)
        for name in METRIC_NAMES
    }
