import json
from pathlib import Path

import pytest

from finevid_distill.data.build_dataset import (
    OFFICIAL_SPLITS,
    build_all_splits,
    build_question,
    format_table_row,
)
from finevid_distill.data.validate_dataset import (
    DatasetValidationError,
    validate_dataset,
)


ROOT = Path(__file__).resolve().parents[1]


def raw_record(question_id: str, question: str = "What is revenue?") -> dict:
    return {
        "id": question_id,
        "pre_text": ["gold evidence", "duplicate source text"],
        "post_text": ["duplicate source text", "last prose candidate"],
        "table": [["metric", "2024"], ["revenue", "10"]],
        "qa": {
            "question": question,
            "answer": "10",
            "program": "add(5, 5)",
            "exe_ans": 10,
            "gold_inds": {"text_0": "gold evidence"},
        },
    }


def write_raw_fixture(raw_dir: Path) -> None:
    raw_dir.mkdir(parents=True)
    for split in OFFICIAL_SPLITS:
        record = raw_record(
            f"{split}/report.pdf-1",
            question=f"What is {split} revenue?",
        )
        (raw_dir / f"{split}.json").write_text(
            json.dumps([record]), encoding="utf-8"
        )


def test_build_question_creates_every_candidate_and_maps_gold() -> None:
    record = raw_record("company/report.pdf-2")
    record["qa"]["gold_inds"] = {
        "text_-1": "last prose candidate",
        "table_1": "metric the revenue of 2024 is 10 ;",
    }

    result = build_question(record)

    assert result["question_id"] == "company/report.pdf-2"
    assert result["report_id"] == "company/report.pdf"
    assert [candidate["candidate_id"] for candidate in result["candidates"]] == [
        "pre-text-0",
        "pre-text-1",
        "post-text-0",
        "post-text-1",
        "table-row-0",
        "table-row-1",
    ]
    assert result["positive_candidate_ids"] == ["post-text-1", "table-row-1"]
    assert not ({"answer", "program", "exe_ans", "gold_inds"} & set(result))


def test_table_format_is_deterministic_and_readable() -> None:
    table = [["metric", "2023", "2024"], ["revenue", "9", "10"]]

    assert format_table_row(table, 0) == "metric | 2023 | 2024"
    assert format_table_row(table, 1) == "revenue | 2023: 9 | 2024: 10"


def test_regeneration_with_seed_42_is_byte_identical(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    write_raw_fixture(raw_dir)

    first = build_all_splits(raw_dir, first_dir, seed=42)
    second = build_all_splits(raw_dir, second_dir, seed=42)

    for split in OFFICIAL_SPLITS:
        assert first[split]["sha256"] == second[split]["sha256"]
        assert (first_dir / f"{split}.jsonl").read_bytes() == (
            second_dir / f"{split}.jsonl"
        ).read_bytes()


def test_validator_accepts_clean_data_and_reports_source_duplicates(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    write_raw_fixture(raw_dir)
    build_all_splits(raw_dir, processed_dir, seed=42)

    statistics = validate_dataset(
        raw_dir,
        processed_dir,
        statistics_path=tmp_path / "statistics.json",
        manual_inspection_path=tmp_path / "inspection.md",
        seed=42,
        manual_review_complete=True,
    )

    assert statistics["valid"] is True
    assert statistics["gold_mapping"]["percentage"] == 100.0
    assert statistics["duplicate_candidate_text"]["questions_with_duplicates"] == 3
    assert statistics["leakage"]["detected"] is False
    assert all(
        result["identical"] for result in statistics["reproducibility"].values()
    )


def test_validator_rejects_an_unmapped_positive(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    write_raw_fixture(raw_dir)
    build_all_splits(raw_dir, processed_dir, seed=42)
    train_path = processed_dir / "train.jsonl"
    record = json.loads(train_path.read_text(encoding="utf-8"))
    record["positive_candidate_ids"] = ["missing-candidate"]
    train_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    with pytest.raises(DatasetValidationError, match="unmapped_gold_evidence"):
        validate_dataset(
            raw_dir,
            processed_dir,
            statistics_path=tmp_path / "statistics.json",
            manual_inspection_path=tmp_path / "inspection.md",
            seed=42,
        )


def test_checked_in_full_dataset_statistics() -> None:
    statistics = json.loads(
        (ROOT / "outputs" / "data_statistics.json").read_text(encoding="utf-8")
    )

    assert statistics["valid"] is True
    assert statistics["gold_mapping"] == {
        "annotations": 14108,
        "mapped": 14108,
        "percentage": 100.0,
    }
    assert all(count == 0 for count in statistics["fatal_issue_counts"].values())
    assert statistics["leakage"]["detected"] is False
    assert statistics["manual_inspection"]["sample_size"] == 100
