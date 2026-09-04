import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "02_colab_teacher.ipynb"
COLAB_REQUIREMENTS = ROOT / "requirements-colab.txt"


def test_colab_teacher_notebook_has_gpu_gate_and_no_test_evaluation() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
    )

    assert notebook["nbformat"] == 4
    assert notebook["metadata"]["accelerator"] == "GPU"
    assert "torch.cuda.is_available()" in source
    assert "teacher_mrr > frozen_bge_mrr" in source
    assert "--splits', 'dev'" in source
    assert "--splits', 'train'" in source
    assert "--split', 'test'" not in source
    assert "teacher_test_scores" not in source
    assert "x-access-token:" not in source
    assert "GIT_ASKPASS" in source


def test_colab_requirements_do_not_replace_cuda_pytorch() -> None:
    requirements = [
        line.strip().lower()
        for line in COLAB_REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    assert not any(line.startswith("torch") for line in requirements)
