import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "03_colab_hard_label.ipynb"


def test_hard_label_notebook_uses_fixed_rows_dev_only_and_resumes() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
    )

    assert notebook["nbformat"] == 4
    assert notebook["metadata"]["accelerator"] == "GPU"
    assert "build_training_rows.py" in source
    assert "teacher_train_scores.jsonl" in source
    assert "train_hard_labels.py" in source
    assert "train_rows.jsonl" in source
    assert "dev.jsonl" in source
    assert "test.jsonl" not in source
    assert "latest.json" in source
    assert "--resume" in source
    assert "x-access-token:" not in source
    assert "GIT_ASKPASS" in source
