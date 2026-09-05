import json
from pathlib import Path

import pytest
import torch
import torch.nn.functional as F

from finevid_distill.training import train_hard_labels as trainer
from finevid_distill.training.train_distilled import main as distilled_main
from finevid_distill.evaluation.compare_students import compare_student_runs
from test_hard_label_training import TinySentenceEncoder, training_rows


class ReloadableTinyEncoder(TinySentenceEncoder):
    def forward(self, features):
        output = super().forward(features)
        output["sentence_embedding"] = F.dropout(
            output["sentence_embedding"], p=0.2, training=self.training
        )
        return output

    def encode(self, texts, **kwargs):
        self.eval()
        with torch.no_grad():
            return F.normalize(self(self.tokenize(texts))["sentence_embedding"], dim=1).numpy()


@pytest.fixture
def run_inputs(tmp_path, monkeypatch):
    rows = training_rows()
    train_path = tmp_path / "train_rows.jsonl"
    dev_path = tmp_path / "dev.jsonl"
    train_path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    dev_records = [
        {"question_id": row["question_id"], "report_id": row["question_id"],
         "question": row["question"],
         "candidates": [{"candidate_id": cid, "text": text}
                        for cid, text in zip(row["candidate_ids"], row["candidate_texts"])],
         "positive_candidate_ids": [cid for cid, gold in zip(row["candidate_ids"], row["positive_mask"]) if gold]}
        for row in rows
    ]
    dev_path.write_text("\n".join(json.dumps(row) for row in dev_records), encoding="utf-8")

    def load_model(source, **kwargs):
        if Path(source).is_dir():
            return ReloadableTinyEncoder.from_pretrained(Path(source))
        return ReloadableTinyEncoder()

    monkeypatch.setattr(trainer, "load_student_model", load_model)
    return ["--train-rows", str(train_path), "--dev-data", str(dev_path),
            "--device", "cpu", "--allow-cpu", "--mixed-precision", "none",
            "--limit-train", "2", "--limit-dev", "2", "--epochs", "2",
            "--questions-per-batch", "1", "--no-progress"]


def read_json(directory, name):
    return json.loads((directory / name).read_text())


@pytest.mark.parametrize("treatment", ["hard_label", "distilled"])
def test_resume_matches_uninterrupted_training_and_recovers_stale_pointers(
    run_inputs, tmp_path, monkeypatch, treatment
):
    full = tmp_path / "full"
    resumed = tmp_path / "resumed"
    trainer.main(run_inputs + ["--output-dir", str(full)], treatment=treatment)
    original_epoch = trainer.train_one_epoch

    def disconnect_on_second_epoch(*args, **kwargs):
        if kwargs["epoch"] == 2:
            raise RuntimeError("simulated Colab disconnect")
        return original_epoch(*args, **kwargs)

    monkeypatch.setattr(trainer, "train_one_epoch", disconnect_on_second_epoch)
    with pytest.raises(RuntimeError, match="disconnect"):
        trainer.main(run_inputs + ["--output-dir", str(resumed)], treatment=treatment)
    # Epoch publication succeeded, but its derived summary files were lost.
    for name in ("latest.json", "best.json", "training_history.json"):
        (resumed / name).unlink()
    monkeypatch.setattr(trainer, "train_one_epoch", original_epoch)
    trainer.main(run_inputs + ["--output-dir", str(resumed), "--resume"], treatment=treatment)

    assert read_json(full, "best_reload_verification.json") == read_json(resumed, "best_reload_verification.json")
    assert read_json(full, "initial_development.json") == read_json(resumed, "initial_development.json")
    for run in (full, resumed):
        assert read_json(run, "latest.json")["global_step"] == 4
        assert read_json(run, "run_config.json")["student_temperature"] == 0.05
    first_history = read_json(full, "training_history.json")["epochs"]
    second_history = read_json(resumed, "training_history.json")["epochs"]
    for left, right in zip(first_history, second_history):
        left.pop("epoch_time_seconds")
        right.pop("epoch_time_seconds")
        assert left == right
    left_state = torch.load(full / "epochs/epoch-002/model/tiny_model.pt", weights_only=True)
    right_state = torch.load(resumed / "epochs/epoch-002/model/tiny_model.pt", weights_only=True)
    assert all(torch.equal(left_state[key], right_state[key]) for key in left_state)
    if treatment == "distilled":
        assert {"kl_loss", "hard_loss", "total_loss", "teacher_entropy"} <= set(first_history[0])


def test_resume_rejects_changed_temperature_and_preserves_original(run_inputs, tmp_path):
    output = tmp_path / "run"
    args = run_inputs + ["--output-dir", str(output)]
    assert distilled_main(args) == 0
    original = (output / "run_config.json").read_bytes()
    with pytest.raises(ValueError, match="Resume configuration"):
        distilled_main(args + ["--resume", "--student-temperature", "0.1"])
    assert (output / "run_config.json").read_bytes() == original


def test_uncheckpointed_run_restarts_after_trainer_fix(run_inputs, tmp_path, monkeypatch):
    output = tmp_path / "run"
    arguments = run_inputs + ["--output-dir", str(output)]
    original_epoch = trainer.train_one_epoch

    def fail_before_first_checkpoint(*args, **kwargs):
        raise FloatingPointError("simulated FP16 overflow")

    monkeypatch.setattr(trainer, "train_one_epoch", fail_before_first_checkpoint)
    with pytest.raises(FloatingPointError, match="overflow"):
        trainer.main(arguments)
    failed_config = read_json(output, "run_config.json")
    failed_config["training_code_sha256"] = "pre-overflow-retry-trainer"
    (output / "run_config.json").write_text(json.dumps(failed_config))

    monkeypatch.setattr(trainer, "train_one_epoch", original_epoch)
    assert trainer.main(arguments + ["--resume"]) == 0

    backups = list((output / "abandoned_runs").glob("*/run_config.json"))
    assert len(backups) == 1
    assert json.loads(backups[0].read_text())["training_code_sha256"] == (
        "pre-overflow-retry-trainer"
    )
    assert read_json(output, "latest.json")["completed_epoch"] == 2


def test_same_pretrained_initial_evaluation_for_both_treatments(run_inputs, tmp_path):
    for treatment in ("hard_label", "distilled"):
        trainer.main(run_inputs + ["--output-dir", str(tmp_path / treatment)], treatment=treatment)
    assert read_json(tmp_path / "hard_label", "initial_development.json") == read_json(
        tmp_path / "distilled", "initial_development.json"
    )


def test_distilled_cli_defaults_preserve_legacy_output_directory():
    hard = trainer.parse_args([])
    distilled = trainer.parse_args([], treatment="distilled")
    assert hard.output_dir.name == "hard_label_student_tau005"
    assert distilled.output_dir.name == "distilled_student"
    assert hard.student_temperature == distilled.student_temperature == 0.05
    assert distilled.teacher_temperature == 0.3
    assert distilled.hard_label_weight == 0.1


def test_comparison_accepts_matched_runs_and_rejects_unfair_or_unverified_results(run_inputs, tmp_path):
    hard, distilled = tmp_path / "hard", tmp_path / "distilled"
    trainer.main(run_inputs + ["--output-dir", str(hard)])
    distilled_main(run_inputs + ["--output-dir", str(distilled)])
    with pytest.raises(ValueError, match="Diagnostic"):
        compare_student_runs(hard, distilled)
    report = compare_student_runs(hard, distilled, allow_diagnostic=True)
    assert report["fairness_verified"] is True
    assert report["diagnostic_run"] is True
    assert report["question_count"] == 2
    assert report["student_temperature"] == 0.05
    assert report["teacher_temperature"] == 0.3
    assert report["hard_label_weight"] == 0.1
    for name in ("mrr", "recall_at_5"):
        assert report["distilled_minus_hard"][name] == pytest.approx(
            report["models"]["Distilled BGE-small"][name] - report["models"]["Hard-label BGE-small"][name]
        )
    config_path = distilled / "run_config.json"
    original = config_path.read_text()
    config = json.loads(original)
    config["student_temperature"] = 1.0
    config_path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="Student controls differ"):
        compare_student_runs(hard, distilled, allow_diagnostic=True)
    config_path.write_text(original)
    verification = read_json(distilled, "best_reload_verification.json")
    verification["reload_verified"] = False
    (distilled / "best_reload_verification.json").write_text(json.dumps(verification))
    with pytest.raises(ValueError, match="reload verification"):
        compare_student_runs(hard, distilled, allow_diagnostic=True)


def test_comparison_cannot_relabel_small_inputs_as_a_full_run(run_inputs, tmp_path):
    hard, distilled = tmp_path / "hard", tmp_path / "distilled"
    trainer.main(run_inputs + ["--output-dir", str(hard)])
    distilled_main(run_inputs + ["--output-dir", str(distilled)])
    for directory in (hard, distilled):
        config_path = directory / "run_config.json"
        config = json.loads(config_path.read_text())
        config["limit_train"] = None
        config["limit_dev"] = None
        config_path.write_text(json.dumps(config))

    with pytest.raises(ValueError, match="fixed complete experiment"):
        compare_student_runs(hard, distilled)


def test_nonfinite_gradients_abort_before_any_optimizer_step(monkeypatch):
    model = TinySentenceEncoder()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.)
    model.embedding.weight.register_hook(lambda grad: grad * float("nan"))
    before = model.embedding.weight.detach().clone()
    with pytest.raises(FloatingPointError, match="gradient norm"):
        trainer.train_one_epoch(
            model, training_rows(), optimizer, scheduler, device=torch.device("cpu"),
            questions_per_batch=1, seed=42, epoch=1, max_gradient_norm=1., treatment="distilled",
        )
    assert torch.equal(before, model.embedding.weight)
    assert not optimizer.state


def test_partial_checkpoint_files_are_preserved_when_retraining(tmp_path):
    model = TinySentenceEncoder()
    optimizer = torch.optim.AdamW(model.parameters())
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.)
    partial = tmp_path / "epochs/.epoch-001.incomplete"
    partial.mkdir(parents=True)
    (partial / "partial-data.txt").write_text("preserve me")
    checkpoint = trainer.save_epoch_checkpoint(
        tmp_path, model, optimizer, scheduler, completed_epoch=1, global_step=1,
        scaler=None, epoch_metrics={"epoch": 1},
    )
    assert (checkpoint / "trainer_state.pt").exists()
    abandoned = list((tmp_path / "epochs").glob(".abandoned-001-*"))
    assert len(abandoned) == 1
    assert (abandoned[0] / "partial-data.txt").read_text() == "preserve me"
