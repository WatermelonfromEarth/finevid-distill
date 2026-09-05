"""Package development inputs or the explicitly locked final test bundle for Colab."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def package_project(root: Path, output: Path, *, include_final_test: bool = False) -> dict:
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
        "outputs/dev_teacher_comparison.json", "outputs/final_selection.json",
    ))
    purpose = "FinEvid-Distill Milestone 10 Colab source bundle"
    if include_final_test:
        paths.update(
            root / name
            for name in ("data/processed/test.jsonl",)
        )
        purpose = "FinEvid-Distill Milestones 11-12 locked final Colab bundle"
    manifest = {
        "purpose": purpose,
        "test_access_gate": "frozen final selection" if include_final_test else "test excluded",
        "files": {},
    }
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
    parser.add_argument("--include-final-test", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            package_project(
                Path(__file__).resolve().parents[1],
                args.output,
                include_final_test=args.include_final_test,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
