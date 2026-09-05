import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

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
        assert "notebooks/04_colab_distilled.ipynb" in names
        assert "data/processed/train.jsonl" in names
        assert "data/processed/dev.jsonl" in names
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
