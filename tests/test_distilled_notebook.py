import ast
import json
from pathlib import Path


def test_distilled_notebook_runs_both_matched_treatments_and_exports_results():
    root = Path(__file__).resolve().parents[1]
    notebook = json.loads((root / "notebooks/04_colab_distilled.ipynb").read_text())
    assert notebook["metadata"]["accelerator"] == "GPU"
    source = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
    for required in ("bundle_manifest.json", "hashlib.sha256", "build_training_rows.py",
                     "train_hard_labels.py", "train_distilled.py", "compare_students.py",
                     "hard_label_student_tau005", "distilled_student", "--resume",
                     "best_reload_verification.json", "initial_development.json"):
        assert required in source
    assert "test.jsonl" not in source
    assert "GITHUB_TOKEN" not in source
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell["execution_count"] is None
            assert cell["outputs"] == []
            python_source = "\n".join(line for line in "".join(cell["source"]).splitlines()
                                      if not line.startswith("%"))
            ast.parse(python_source)
