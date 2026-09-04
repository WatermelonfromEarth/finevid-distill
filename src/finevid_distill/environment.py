"""Print device selection and core dependency versions."""

from __future__ import annotations

import argparse
import importlib.metadata
import platform
import sys
from pathlib import Path
from typing import Any

import torch

from finevid_distill.config import load_config


DISTRIBUTIONS = (
    "torch",
    "transformers",
    "sentence-transformers",
    "datasets",
    "rank-bm25",
    "numpy",
    "pandas",
    "scikit-learn",
    "PyYAML",
    "pytest",
    "ipykernel",
    "nbconvert",
)


def default_config_path() -> Path:
    """Return the repository's default beginner configuration path."""
    return Path(__file__).resolve().parents[2] / "configs" / "beginner.yaml"


def resolve_device(requested: str) -> str:
    """Resolve ``auto`` without allocating a model or tensor."""
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    mps = getattr(torch.backends, "mps", None)
    if mps is not None and mps.is_available():
        return "mps"
    return "cpu"


def package_versions() -> dict[str, str]:
    """Return installed versions, preserving missing packages in the report."""
    versions: dict[str, str] = {}
    for distribution in DISTRIBUTIONS:
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            versions[distribution] = "not installed"
    return versions


def build_report(config: dict[str, Any]) -> str:
    """Build a stable, human-readable environment report."""
    requested_device = str(config["runtime"]["device"])
    lines = [
        f"Python: {platform.python_version()}",
        f"Platform: {platform.platform()}",
        f"Configured device: {requested_device}",
        f"Resolved device: {resolve_device(requested_device)}",
        "Package versions:",
    ]
    lines.extend(
        f"  {distribution}: {version}"
        for distribution, version in package_versions().items()
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config_path(),
        help="Path to the experiment YAML file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config)
    print(build_report(config))
    return 0


if __name__ == "__main__":
    sys.exit(main())
