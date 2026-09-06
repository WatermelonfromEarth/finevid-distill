"""Download the pinned official FinQA splits used by the experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from finevid_distill.data.finqa import FINQA_COMMIT, download_split


DEFAULT_SPLITS = ("train", "dev", "test")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=root / "data/raw")
    parser.add_argument(
        "--splits",
        nargs="+",
        choices=DEFAULT_SPLITS,
        default=list(DEFAULT_SPLITS),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    for split in args.splits:
        path = download_split(args.raw_dir, split)
        print(f"{split}: {path}")
    print(f"FinQA source commit: {FINQA_COMMIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
