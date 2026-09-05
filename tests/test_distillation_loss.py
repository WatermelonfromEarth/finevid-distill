import math

import pytest
import torch

from finevid_distill.training.losses import ranking_loss_components
from finevid_distill.training.train_hard_labels import (
    training_batch_losses, training_score_rows,
)
from test_hard_label_training import TinySentenceEncoder, training_rows


def test_kl_direction_weight_and_reduction_match_hand_calculation():
    scores = 0.05 * torch.tensor([0.4, 0.6]).log()
    teacher = 0.3 * torch.tensor([0.75, 0.25]).log()
    result = ranking_loss_components([scores], [[1, 0]], teacher_score_rows=[teacher])
    expected_kl = 0.75 * math.log(0.75 / 0.4) + 0.25 * math.log(0.25 / 0.6)
    assert result["kl_loss"].item() == pytest.approx(expected_kl)
    assert result["hard_loss"].item() == pytest.approx(-math.log(0.4))
    assert result["total_loss"].item() == pytest.approx(expected_kl - 0.1 * math.log(0.4))


def test_questions_have_equal_weight_despite_different_candidate_counts():
    scores = [torch.zeros(2), torch.zeros(5)]
    teachers = [torch.tensor([2., -1.]), torch.arange(5.)]
    gold = [[1, 0], [1, 0, 1, 0, 0]]
    batch = ranking_loss_components(scores, gold, teacher_score_rows=teachers)
    separate = [ranking_loss_components([s], [g], teacher_score_rows=[t])
                for s, g, t in zip(scores, gold, teachers)]
    for name in batch:
        assert batch[name].item() == pytest.approx(
            sum(row[name].item() for row in separate) / 2
        )


@pytest.mark.parametrize("padding", [1e6, float("nan"), float("-inf")])
def test_padding_is_excluded_before_softmax_and_has_zero_gradient(padding):
    scores = torch.tensor([0.2, -0.1, padding], requires_grad=True)
    teacher = torch.tensor([1., -1., padding], requires_grad=True)
    result = ranking_loss_components(
        [scores], [[1, 0, 0]], teacher_score_rows=[teacher],
        candidate_masks=[[True, True, False]],
    )
    unpadded = ranking_loss_components(
        [scores[:2]], [[1, 0]], teacher_score_rows=[teacher[:2]]
    )
    assert result["total_loss"].item() == pytest.approx(unpadded["total_loss"].item())
    result["total_loss"].backward()
    assert teacher.grad is None
    assert torch.isfinite(scores.grad).all()
    assert scores.grad[-1].item() == 0


def test_teacher_is_detached_and_student_gets_nonzero_gradients():
    student = torch.tensor([0.1, 0.2], requires_grad=True)
    teacher = torch.tensor([3., -3.], requires_grad=True)
    result = ranking_loss_components([student], [[1, 0]], teacher_score_rows=[teacher])
    result["total_loss"].backward()
    assert teacher.grad is None
    assert student.grad.abs().sum() > 0
    assert torch.isfinite(student.grad).all()
    assert not result["teacher_entropy"].requires_grad


def test_identical_distributions_have_zero_kl():
    scores = torch.tensor([0.1, -0.2, 0.3])
    result = ranking_loss_components(
        [scores], [[1, 0, 1]], teacher_score_rows=[scores * 6]
    )
    assert result["kl_loss"].item() == pytest.approx(0, abs=1e-6)


def test_extreme_scores_use_finite_fp32_loss_and_gradients():
    scores = torch.tensor([1., -1., 0.], dtype=torch.float16, requires_grad=True)
    result = ranking_loss_components(
        [scores], [[0, 1, 1]], teacher_score_rows=[[10000., -10000., 0.]]
    )
    assert all(value.dtype == torch.float32 for value in result.values())
    assert all(torch.isfinite(value) for value in result.values())
    result["total_loss"].backward()
    assert torch.isfinite(scores.grad).all()


@pytest.mark.parametrize("name", ["student_temperature", "teacher_temperature"])
@pytest.mark.parametrize("value", [0., -1., float("nan"), float("inf")])
def test_invalid_temperatures_rejected(name, value):
    with pytest.raises(ValueError, match="temperature"):
        ranking_loss_components([torch.zeros(2)], [[1, 0]], **{name: value})


@pytest.mark.parametrize("teacher", [False, True])
def test_nonfinite_unmasked_scores_rejected(teacher):
    scores = torch.tensor([0., float("nan")])
    with pytest.raises(FloatingPointError):
        ranking_loss_components(
            [torch.zeros(2) if teacher else scores], [[1, 0]],
            teacher_score_rows=[scores if teacher else torch.zeros(2)],
        )


@pytest.mark.parametrize("mask,gold", [([0, 0], [1, 0]), ([1, 0], [0, 1]),
                                       ([1, 1], [0, 0]), ([1, 2], [1, 0])])
def test_invalid_candidate_or_gold_masks_rejected(mask, gold):
    with pytest.raises(ValueError):
        ranking_loss_components([torch.zeros(2)], [gold], candidate_masks=[mask])


def test_hard_term_matches_temperature_matched_baseline():
    scores = [torch.tensor([0.1, -0.1, 0.4])]
    gold = [[1, 0, 1]]
    hard = ranking_loss_components(scores, gold)
    distilled = ranking_loss_components(scores, gold, teacher_score_rows=[[2., 0., 1.]])
    assert torch.equal(hard["total_loss"], distilled["hard_loss"])


def test_distilled_path_applies_query_instruction_and_normalizes_embeddings():
    model = TinySentenceEncoder()
    rows = training_rows()
    scores = training_score_rows(model, rows, device=torch.device("cpu"))
    assert all(torch.all(row.abs() <= 1.000001) for row in scores)
    assert all(text.startswith("Represent this sentence") for text in model.tokenized_batches[0])
    assert model.tokenized_batches[1] == [text for row in rows for text in row["candidate_texts"]]
    result = training_batch_losses(model, rows, device=torch.device("cpu"), treatment="distilled")
    result["total_loss"].backward()
    assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
