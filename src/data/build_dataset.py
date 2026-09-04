"""Compatibility entry point for the requested ``src/data`` layout."""

from finevid_distill.data.build_dataset import main


if __name__ == "__main__":
    raise SystemExit(main())
