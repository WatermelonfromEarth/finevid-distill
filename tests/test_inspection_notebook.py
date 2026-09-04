import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "01_inspect_finqa.ipynb"


def test_inspection_notebook_is_executed_and_complete() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    code_cells = [
        cell for cell in notebook["cells"] if cell["cell_type"] == "code"
    ]
    outputs = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
    ]
    stream_text = "\n".join(
        "".join(output.get("text", ""))
        if isinstance(output.get("text", ""), list)
        else output.get("text", "")
        for output in outputs
    )
    markdown = "\n".join(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "markdown"
    )

    assert code_cells
    assert all(cell["execution_count"] is not None for cell in code_cells)
    assert not [output for output in outputs if output["output_type"] == "error"]
    assert stream_text.count("RAW RECORD") == 10
    assert "12,205 / 12,205 train+dev gold values resolved" in stream_text
    assert "Schema conclusion: exact `gold_inds` mapping" in markdown
    assert "Candidate-count distributions" in markdown
    assert "test split was not loaded" in markdown
