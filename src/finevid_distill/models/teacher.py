"""Qwen3 reranker wrapper that returns untransformed logit differences."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from finevid_distill.models.bge_ranker import resolve_device


QWEN_MODEL_ID = "Qwen/Qwen3-Reranker-0.6B"
QWEN_MODEL_REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"
QWEN_INSTRUCTION = (
    "Given a financial question, retrieve every supporting fact from the financial "
    "report that is required to answer the question"
)


class QwenTeacher:
    """Score question/candidate pairs with raw Qwen yes-minus-no logits."""

    label = "Qwen teacher"

    def __init__(
        self,
        model_id: str = QWEN_MODEL_ID,
        *,
        revision: str | None = QWEN_MODEL_REVISION,
        instruction: str = QWEN_INSTRUCTION,
        device: str = "auto",
        max_length: int = 512,
        local_files_only: bool = False,
        allow_cpu: bool = False,
    ) -> None:
        self.model_id = model_id
        self.revision = revision
        self.instruction = instruction
        self.device = resolve_device(device)
        if self.device == "cpu" and not allow_cpu:
            raise RuntimeError(
                "Qwen teacher inference requires an accelerator for this experiment. "
                "Use the Colab notebook, or pass allow_cpu=True only for an explicit "
                "small diagnostic run."
            )
        self.max_length = max_length
        self.local_files_only = local_files_only
        self._model: Any | None = None

    @property
    def model(self) -> Any:
        if self._model is None:
            import torch
            from sentence_transformers import CrossEncoder

            # The published checkpoint is BF16. This host exposes AVX2 but no native
            # BF16 CPU instructions, so float32 avoids extremely slow BF16 emulation.
            model_kwargs = {"dtype": torch.float32} if self.device == "cpu" else None
            self._model = CrossEncoder(
                self.model_id,
                revision=self.revision,
                device=self.device,
                prompts={"finqa": self.instruction},
                default_prompt_name="finqa",
                max_length=self.max_length,
                local_files_only=self.local_files_only,
                model_kwargs=model_kwargs,
            )
            self._model.model.eval()
        return self._model

    def score_pairs(
        self,
        pairs: Sequence[tuple[str, str]],
        *,
        batch_size: int = 8,
        show_progress: bool = True,
    ) -> list[float]:
        """Return raw logit differences; no sigmoid or temperature is applied."""
        if not pairs:
            return []
        import numpy as np
        import torch

        scores = self.model.predict(
            list(pairs),
            batch_size=batch_size,
            show_progress_bar=show_progress,
            activation_fn=torch.nn.Identity(),
            apply_softmax=False,
            convert_to_numpy=True,
        )
        values = [float(value) for value in np.asarray(scores).reshape(-1)]
        if len(values) != len(pairs):
            raise ValueError("Qwen returned the wrong number of scores.")
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Qwen returned a non-finite raw logit.")
        return values
