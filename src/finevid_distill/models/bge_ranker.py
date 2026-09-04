"""Frozen BGE-small dense retrieval baseline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np


BGE_MODEL_ID = "BAAI/bge-small-en-v1.5"
BGE_MODEL_REVISION = "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


def resolve_device(requested: str) -> str:
    if requested != "auto":
        return requested
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class BGERanker:
    """Encode instructed questions and plain candidates as normalized vectors."""

    label = "Frozen BGE"

    def __init__(
        self,
        model_id: str = BGE_MODEL_ID,
        *,
        revision: str | None = BGE_MODEL_REVISION,
        device: str = "auto",
        batch_size: int = 64,
        show_progress: bool = True,
        local_files_only: bool = False,
    ) -> None:
        self.model_id = model_id
        self.revision = revision
        self.device = resolve_device(device)
        self.batch_size = batch_size
        self.show_progress = show_progress
        self.local_files_only = local_files_only
        self._model: Any | None = None

    @property
    def model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self.model_id,
                revision=self.revision,
                device=self.device,
                local_files_only=self.local_files_only,
            )
            self._model.eval()
        return self._model

    def score_records(
        self, records: Sequence[Mapping[str, Any]]
    ) -> list[list[float]]:
        """Score records while encoding each report candidate only once."""
        if not records:
            return []

        candidate_keys: list[tuple[str, str]] = []
        candidate_text_by_key: dict[tuple[str, str], str] = {}
        seen_candidate_keys: set[tuple[str, str]] = set()
        for record in records:
            for candidate in record["candidates"]:
                key = (record["report_id"], candidate["candidate_id"])
                text = candidate["text"]
                previous = candidate_text_by_key.setdefault(key, text)
                if previous != text:
                    raise ValueError(f"Candidate provenance changed for {key!r}.")
                if key not in seen_candidate_keys:
                    candidate_keys.append(key)
                    seen_candidate_keys.add(key)

        candidate_embeddings = self.model.encode(
            [candidate_text_by_key[key] for key in candidate_keys],
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=self.show_progress,
        )
        question_embeddings = self.model.encode(
            [BGE_QUERY_INSTRUCTION + record["question"] for record in records],
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=self.show_progress,
        )
        candidate_index = {key: index for index, key in enumerate(candidate_keys)}

        results: list[list[float]] = []
        for question_embedding, record in zip(question_embeddings, records, strict=True):
            indices = [
                candidate_index[(record["report_id"], candidate["candidate_id"])]
                for candidate in record["candidates"]
            ]
            matrix = np.asarray(candidate_embeddings)[indices]
            scores = matrix @ np.asarray(question_embedding)
            results.append([float(score) for score in scores])
        return results
