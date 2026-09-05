import math
from pathlib import Path

import pytest
import torch

from finevid_distill.models.bge_ranker import BGE_QUERY_INSTRUCTION
from finevid_distill.training.train_hard_labels import (
    epoch_batches,
    equal_positive_target,
    linear_warmup_decay,
    listwise_cross_entropy,
    load_trainer_state,
    save_epoch_checkpoint,
    set_reproducible_seed,
    train_one_epoch,
    training_batch_loss,
    validate_loaded_training_rows,
)


class TinySentenceEncoder(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.embedding = torch.nn.Embedding(67, 6)
        self.tokenized_batches: list[list[str]] = []

    def tokenize(self, texts: list[str]) -> dict[str, torch.Tensor]:
        self.tokenized_batches.append(texts)
        ids = [
            [sum(text.encode("utf-8")) % 67, len(text.encode("utf-8")) % 67]
            for text in texts
        ]
        return {"input_ids": torch.tensor(ids, dtype=torch.long)}

    def forward(self, features: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        embeddings = self.embedding(features["input_ids"]).mean(dim=1)
        return {"sentence_embedding": embeddings}

    def save_pretrained(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), path / "tiny_model.pt")

    @classmethod
    def from_pretrained(cls, path: Path) -> "TinySentenceEncoder":
        model = cls()
        model.load_state_dict(
            torch.load(path / "tiny_model.pt", map_location="cpu", weights_only=True)
        )
        return model


def training_rows() -> list[dict]:
    return [
        {
            "question_id": "report-1-1",
            "question": "What changed?",
            "candidate_ids": ["c0", "c1", "c2"],
            "candidate_texts": ["revenue rose", "cost fell", "nothing"],
            "positive_mask": [1, 1, 0],
            "teacher_scores": [2.0, 1.0, -2.0],
        },
        {
            "question_id": "report-2-1",
            "question": "What was the margin?",
            "candidate_ids": ["c0", "c1"],
            "candidate_texts": ["margin was ten percent", "cash increased"],
            "positive_mask": [1, 0],
            "teacher_scores": [3.0, -1.0],
        },
    ]


def test_equal_positive_target_splits_mass_across_all_gold() -> None:
    target = equal_positive_target([1, 0, 1, 0])

    assert target.tolist() == [0.5, 0.0, 0.5, 0.0]
    assert target.sum().item() == 1.0


def test_listwise_cross_entropy_matches_hand_calculation() -> None:
    scores = torch.tensor([2.0, 0.0, 1.0])
    expected = -0.5 * math.log(math.exp(2.0) / sum(math.exp(x) for x in (2, 0, 1)))
    expected -= 0.5 * math.log(math.exp(1.0) / sum(math.exp(x) for x in (2, 0, 1)))

    actual = listwise_cross_entropy([scores], [[1, 0, 1]])

    assert actual.item() == pytest.approx(expected)


@pytest.mark.parametrize("mask", ([0, 0], [1, 2], [], [[1, 0]]))
def test_invalid_hard_targets_are_rejected(mask) -> None:
    with pytest.raises(ValueError):
        equal_positive_target(mask)


def test_batch_loss_instructs_questions_but_not_candidates() -> None:
    model = TinySentenceEncoder()

    loss = training_batch_loss(model, training_rows(), device=torch.device("cpu"))

    assert torch.isfinite(loss)
    assert all(text.startswith(BGE_QUERY_INSTRUCTION) for text in model.tokenized_batches[0])
    assert all(
        not text.startswith(BGE_QUERY_INSTRUCTION)
        for text in model.tokenized_batches[1]
    )


def test_hard_label_loss_does_not_read_teacher_scores() -> None:
    model = TinySentenceEncoder()
    rows = training_rows()
    original = training_batch_loss(model, rows, device=torch.device("cpu"))
    for row in rows:
        row["teacher_scores"] = [999.0] * len(row["teacher_scores"])

    changed = training_batch_loss(model, rows, device=torch.device("cpu"))

    assert torch.equal(original, changed)


def test_seeded_epoch_batches_are_reproducible() -> None:
    rows = training_rows() * 3

    first = epoch_batches(rows, questions_per_batch=2, seed=42, epoch=1)
    second = epoch_batches(rows, questions_per_batch=2, seed=42, epoch=1)

    assert [id(row) for batch in first for row in batch] == [
        id(row) for batch in second for row in batch
    ]


def _trained_once(initial_state: dict[str, torch.Tensor]) -> tuple[dict, dict]:
    model = TinySentenceEncoder()
    model.load_state_dict(initial_state)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
    metrics = train_one_epoch(
        model,
        training_rows(),
        optimizer,
        scheduler,
        device=torch.device("cpu"),
        questions_per_batch=1,
        seed=42,
        epoch=1,
        max_gradient_norm=1.0,
    )
    return model.state_dict(), metrics


def test_one_epoch_is_reproducible() -> None:
    set_reproducible_seed(42)
    initial = TinySentenceEncoder().state_dict()

    first_state, first_metrics = _trained_once(initial)
    second_state, second_metrics = _trained_once(initial)

    assert first_metrics == second_metrics
    assert all(torch.equal(first_state[key], second_state[key]) for key in first_state)


def test_fp16_loss_scaler_backs_off_and_retries_the_same_batch() -> None:
    class OverflowOnceScaler:
        def __init__(self) -> None:
            self.scale_value = 8.0
            self.unscale_calls = 0
            self.optimizer_steps = 0
            self.found_nonfinite = False

        def scale(self, loss):
            return loss

        def unscale_(self, optimizer) -> None:
            self.found_nonfinite = self.unscale_calls == 0
            self.unscale_calls += 1
            if self.found_nonfinite:
                parameter = optimizer.param_groups[0]["params"][0]
                parameter.grad.view(-1)[0] = float("inf")

        def step(self, optimizer) -> None:
            if not self.found_nonfinite:
                optimizer.step()
                self.optimizer_steps += 1

        def update(self) -> None:
            if self.found_nonfinite:
                self.scale_value /= 2

        def get_scale(self) -> float:
            return self.scale_value

    model = TinySentenceEncoder()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
    scaler = OverflowOnceScaler()

    metrics = train_one_epoch(
        model,
        training_rows(),
        optimizer,
        scheduler,
        device=torch.device("cpu"),
        questions_per_batch=2,
        seed=42,
        epoch=1,
        max_gradient_norm=1.0,
        scaler=scaler,
        use_fp16=False,
        show_progress=False,
    )

    assert metrics["optimizer_steps"] == 1
    assert metrics["loss_scale_overflow_retries"] == 1
    assert scaler.unscale_calls == 2
    assert scaler.optimizer_steps == 1


def test_checkpoint_saves_model_optimizer_scheduler_and_rng(tmp_path: Path) -> None:
    set_reproducible_seed(42)
    model = TinySentenceEncoder()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)

    checkpoint = save_epoch_checkpoint(
        tmp_path,
        model,
        optimizer,
        scheduler,
        completed_epoch=1,
        global_step=2,
        scaler=None,
        epoch_metrics={"development_mrr": 0.75},
    )
    reloaded_model = TinySentenceEncoder.from_pretrained(checkpoint / "model")
    reloaded_optimizer = torch.optim.AdamW(reloaded_model.parameters(), lr=1e-3)
    reloaded_scheduler = torch.optim.lr_scheduler.LambdaLR(
        reloaded_optimizer, lambda _: 1.0
    )
    state = load_trainer_state(
        checkpoint,
        reloaded_optimizer,
        reloaded_scheduler,
        scaler=None,
    )

    assert state["completed_epoch"] == 1
    assert state["global_step"] == 2
    assert state["rng"]["torch_cpu"] is not None
    assert all(
        torch.equal(model.state_dict()[key], reloaded_model.state_dict()[key])
        for key in model.state_dict()
    )


def test_learning_rate_schedule_has_warmup_and_decay() -> None:
    assert linear_warmup_decay(0, warmup_steps=2, total_steps=10) == 0.0
    assert linear_warmup_decay(1, warmup_steps=2, total_steps=10) == 0.5
    assert linear_warmup_decay(2, warmup_steps=2, total_steps=10) == 1.0
    assert linear_warmup_decay(10, warmup_steps=2, total_steps=10) == 0.0


def test_training_rows_require_a_positive() -> None:
    rows = training_rows()
    rows[0]["positive_mask"] = [0, 0, 0]

    with pytest.raises(ValueError, match="zero-positive"):
        validate_loaded_training_rows(rows)
