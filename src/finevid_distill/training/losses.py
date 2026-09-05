"""Candidate-masked ranking objectives shared by both student treatments."""

from __future__ import annotations

import math
from collections.abc import Sequence

import torch
import torch.nn.functional as F


DEFAULT_STUDENT_TEMPERATURE = 0.05
DEFAULT_TEACHER_TEMPERATURE = 0.3
DEFAULT_HARD_LABEL_WEIGHT = 0.1


def _positive_temperature(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive.")


def ranking_loss_components(
    score_rows: Sequence[torch.Tensor],
    positive_masks: Sequence[Sequence[int] | torch.Tensor],
    *,
    teacher_score_rows: Sequence[Sequence[float] | torch.Tensor] | None = None,
    candidate_masks: Sequence[Sequence[bool] | torch.Tensor] | None = None,
    student_temperature: float = DEFAULT_STUDENT_TEMPERATURE,
    teacher_temperature: float = DEFAULT_TEACHER_TEMPERATURE,
    hard_label_weight: float = DEFAULT_HARD_LABEL_WEIGHT,
) -> dict[str, torch.Tensor]:
    """Sum over valid candidates, then average equally over questions.

    With teacher scores, optimize KL(teacher || student) + weight * hard CE.
    Otherwise optimize hard CE alone. Both terms use the same student logits.
    No additional temperature-squared multiplier is applied. Ragged rows need
    no padding; explicit masks also support padded callers without 0 * -inf.
    """
    _positive_temperature(student_temperature, "student_temperature")
    _positive_temperature(teacher_temperature, "teacher_temperature")
    if not math.isfinite(hard_label_weight) or hard_label_weight < 0:
        raise ValueError("hard_label_weight must be finite and non-negative.")
    if not score_rows or len(score_rows) != len(positive_masks):
        raise ValueError("Scores and positive masks must have matching non-empty rows.")
    for rows in (teacher_score_rows, candidate_masks):
        if rows is not None and len(rows) != len(score_rows):
            raise ValueError("All inputs must contain the same number of questions.")

    hard_losses, kl_losses, entropies, top_probabilities = [], [], [], []
    for index, raw_scores in enumerate(score_rows):
        if raw_scores.ndim != 1 or raw_scores.numel() == 0:
            raise ValueError("Every score row must be a non-empty candidate vector.")
        valid = torch.ones_like(raw_scores, dtype=torch.bool)
        if candidate_masks is not None:
            mask = torch.as_tensor(candidate_masks[index], device=raw_scores.device)
            if mask.shape != raw_scores.shape or not torch.all((mask == 0) | (mask == 1)):
                raise ValueError("Candidate mask must be binary and match score shape.")
            valid = mask.bool()
        if not valid.any():
            raise ValueError("Every question needs at least one valid candidate.")
        gold = torch.as_tensor(positive_masks[index], device=raw_scores.device)
        if gold.shape != raw_scores.shape or not torch.all((gold == 0) | (gold == 1)):
            raise ValueError("Gold mask must be binary and match score shape.")
        if gold[~valid].any():
            raise ValueError("Padding cannot be labelled as a positive candidate.")
        gold = gold[valid].float()
        if not gold.any():
            raise ValueError("Every question needs at least one valid positive.")
        scores = raw_scores[valid].float()
        if not torch.isfinite(scores).all():
            raise FloatingPointError("Non-finite student scores.")
        # Loss arithmetic stays in FP32 even inside the encoder's autocast block.
        student_log_probs = F.log_softmax(scores / student_temperature, dim=-1)
        hard_losses.append(-(gold / gold.sum() * student_log_probs).sum())

        if teacher_score_rows is not None:
            teacher = torch.as_tensor(teacher_score_rows[index]).detach().to(
                device=raw_scores.device, dtype=torch.float32
            )
            if teacher.shape != raw_scores.shape:
                raise ValueError("Teacher and student candidate shapes must match.")
            teacher = teacher[valid]
            if not torch.isfinite(teacher).all():
                raise FloatingPointError("Non-finite teacher scores.")
            teacher_log_probs = F.log_softmax(teacher / teacher_temperature, dim=-1)
            teacher_probs = teacher_log_probs.exp()
            kl_losses.append(
                (teacher_probs * (teacher_log_probs - student_log_probs)).sum()
            )
            entropies.append(-(teacher_probs * teacher_log_probs).sum())
            top_probabilities.append(teacher_probs.max())

    hard_loss = torch.stack(hard_losses).mean()
    result = {"hard_loss": hard_loss}
    if teacher_score_rows is None:
        result["total_loss"] = hard_loss
    else:
        result["kl_loss"] = torch.stack(kl_losses).mean()
        result["teacher_entropy"] = torch.stack(entropies).mean()
        result["teacher_top_probability"] = torch.stack(top_probabilities).mean()
        result["total_loss"] = result["kl_loss"] + hard_label_weight * hard_loss
    if any(not torch.isfinite(value).all() for value in result.values()):
        raise FloatingPointError("Non-finite ranking loss or teacher diagnostic.")
    return result
