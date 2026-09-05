"""Package source and development inputs for Colab without credentials or models."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def package_project(root: Path, output: Path) -> dict:
    paths = set()
    for pattern in (
        "src/**/*.py",
        "configs/*.yaml",
        "tests/*.py",
        "scripts/*.py",
        "notebooks/*.ipynb",
    ):
        paths.update(root.glob(pattern))
    paths.update(root.glob("outputs/hard_label_run/*.json"))
    paths.update(root / name for name in (
        "README.md", "pyproject.toml", "requirements-colab.txt",
        "data/processed/train.jsonl", "data/processed/dev.jsonl",
        "outputs/data_statistics.json", "outputs/dev_baselines.json",
        "outputs/dev_teacher_comparison.json",
    ))
    manifest = {"purpose": "FinEvid-Distill Milestone 10 Colab source bundle", "files": {}}
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            relative = path.relative_to(root).as_posix()
            data = path.read_bytes()
            manifest["files"][relative] = hashlib.sha256(data).hexdigest()
            info = ZipInfo(relative)
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)
        info = ZipInfo("bundle_manifest.json")
        info.compress_type = ZIP_DEFLATED
        archive.writestr(info, json.dumps(manifest, indent=2, sort_keys=True))
    return {"output": str(output), "files": len(paths), "bytes": output.stat().st_size,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package_project(Path(__file__).resolve().parents[1], args.output), indent=2))


if __name__ == "__main__":
    main()
