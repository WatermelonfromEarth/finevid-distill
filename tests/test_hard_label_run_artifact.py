import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "outputs" / "hard_label_run"


def read(name: str) -> dict:
    return json.loads((RUN / name).read_text(encoding="utf-8"))


def test_original_hard_label_run_is_complete_and_reload_verified() -> None:
    config = read("run_config.json")
    history = read("training_history.json")["epochs"]
    latest = read("latest.json")
    best = read("best.json")
    verification = read("best_reload_verification.json")

    assert config["train_rows_sha256"] == (
        "df56334db862a9e45504db7a1b0846c394e3e7fc9c1414dd89c101efa05a847e"
    )
    assert config["dev_data_sha256"] == hashlib.sha256(
        (ROOT / "data" / "processed" / "dev.jsonl").read_bytes()
    ).hexdigest()
    assert [row["epoch"] for row in history] == [1, 2, 3]
    assert all(row["optimizer_steps"] == 782 for row in history)
    assert latest == {
        "checkpoint": "epochs/epoch-003",
        "completed_epoch": 3,
        "global_step": 2346,
    }
    selected = max(history, key=lambda row: row["development_metrics"]["mrr"])
    assert selected["epoch"] == 1
    assert best["completed_epoch"] == selected["epoch"]
    assert best["development_metrics"] == selected["development_metrics"]
    assert verification["reload_verified"] is True
    assert verification["development_metrics"] == best["development_metrics"]
    assert best["development_metrics"]["mrr"] == pytest.approx(0.7622796108731422)
