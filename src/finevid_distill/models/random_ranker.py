"""Seeded random ranking sanity check."""

from __future__ import annotations

import hashlib
import random
from collections.abc import Mapping, Sequence
from typing import Any


class RandomRanker:
    """Assign reproducible pseudo-random scores independently per question."""

    label = "Random"

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def score_records(
        self, records: Sequence[Mapping[str, Any]]
    ) -> list[list[float]]:
        results: list[list[float]] = []
        for record in records:
            seed_bytes = f"{self.seed}\0{record['question_id']}".encode("utf-8")
            local_seed = int.from_bytes(hashlib.sha256(seed_bytes).digest()[:8], "big")
            generator = random.Random(local_seed)
            results.append([generator.random() for _ in record["candidates"]])
        return results
