import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts.package_colab import package_project


def test_colab_bundle_is_manifested_and_excludes_private_or_test_artifacts(
    tmp_path: Path,
) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "bundle.zip"

    result = package_project(root, output)

    assert result["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    with ZipFile(output) as archive:
        names = set(archive.namelist())
        manifest = json.loads(archive.read("bundle_manifest.json"))
        assert names == set(manifest["files"]) | {"bundle_manifest.json"}
        for name, expected_hash in manifest["files"].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected_hash
        assert "src/finevid_distill/training/train_distilled.py" in names
        assert "notebooks/01_inspect_finqa.ipynb" in names
        assert "notebooks/02_colab_teacher.ipynb" in names
        assert "notebooks/03_colab_hard_label.ipynb" in names
        assert "notebooks/04_colab_distilled.ipynb" in names
        assert "data/processed/train.jsonl" in names
        assert "data/processed/dev.jsonl" in names
        assert "outputs/hard_label_run/run_config.json" in names
        forbidden_fragments = (
            "test.jsonl",
            "teacher_train_scores",
            "teacher_dev_scores",
            "train_rows.jsonl",
            "checkpoint",
            "GITHUB_TOKEN",
            ".safetensors",
        )
        assert not any(
            fragment in name
            for name in names
            for fragment in forbidden_fragments
        )


def test_bundle_is_byte_reproducible(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    package_project(root, first)
    package_project(root, second)

    assert first.read_bytes() == second.read_bytes()


def test_final_bundle_requires_selection_and_includes_locked_test(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / "data/processed/test.jsonl").exists():
        pytest.skip("Development-only bundle intentionally excludes the public test file.")
    output = tmp_path / "final.zip"

    package_project(root, output, include_final_test=True)

    with ZipFile(output) as archive:
        names = set(archive.namelist())
        manifest = json.loads(archive.read("bundle_manifest.json"))
        assert manifest["test_access_gate"] == "frozen final selection"
        assert "outputs/final_selection.json" in names
        assert "data/processed/test.jsonl" in names
        assert "notebooks/05_colab_final_evaluation.ipynb" in names
