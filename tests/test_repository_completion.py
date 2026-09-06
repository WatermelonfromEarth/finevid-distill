from pathlib import Path

from finevid_distill.data import download_finqa
from finevid_distill.evaluation.audit_repository import audit_repository


ROOT = Path(__file__).resolve().parents[1]


def test_repository_audit_passes_for_tracked_deliverables() -> None:
    result = audit_repository(ROOT)
    assert result["status"] == "passed"
    assert result["tracked_files_checked"] == 11
    assert result["test_questions"] == 1147
    assert result["research_answer"] == "no"
    assert result["external_artifacts"]["status"] == "not_checked"


def test_download_cli_uses_pinned_helper(tmp_path, monkeypatch, capsys) -> None:
    calls: list[tuple[Path, str]] = []

    def fake_download(raw_dir: Path, split: str) -> Path:
        calls.append((raw_dir, split))
        return raw_dir / f"{split}.json"

    monkeypatch.setattr(download_finqa, "download_split", fake_download)
    assert download_finqa.main(
        ["--raw-dir", str(tmp_path), "--splits", "train", "test"]
    ) == 0
    assert calls == [(tmp_path, "train"), (tmp_path, "test")]
    assert download_finqa.FINQA_COMMIT in capsys.readouterr().out


def test_readme_contains_final_sections() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_sections = (
        "Project objective",
        "Teacher–student architecture",
        "Dataset construction",
        "Development baselines",
        "Final results",
        "Efficiency comparison",
        "Example success and failure cases",
        "Limitations",
        "Reproduction commands",
        "Planned intermediate extensions",
    )

    for section in required_sections:
        assert f"## {section}" in readme

    assert len(readme.split()) < 2_000
