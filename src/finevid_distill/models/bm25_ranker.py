"""Within-report BM25 baseline."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from rank_bm25 import BM25Okapi


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[.,][0-9]+)*%?", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    """Tokenize words and financial number forms deterministically."""
    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]


class BM25Ranker:
    """Fit a separate BM25 index over every question's report candidates."""

    label = "BM25"

    def score_records(
        self, records: Sequence[Mapping[str, Any]]
    ) -> list[list[float]]:
        results: list[list[float]] = []
        for record in records:
            corpus = [tokenize(candidate["text"]) for candidate in record["candidates"]]
            if not corpus:
                raise ValueError(f"{record['question_id']} has no candidates.")
            scores = BM25Okapi(corpus).get_scores(tokenize(record["question"]))
            results.append([float(score) for score in scores])
        return results
