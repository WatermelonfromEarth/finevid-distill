from finevid_distill.data.finqa import (
    candidate_counts,
    gold_format,
    normalize_annotation_spacing,
    parse_gold_key,
    resolve_gold_evidence,
    serialize_table_row,
)


def example_record() -> dict:
    return {
        "id": "report.pdf-1",
        "pre_text": ["before zero", "before one"],
        "post_text": ["after zero", "after one"],
        "table": [["metric", "2024"], ["revenue", "$10"]],
        "qa": {
            "gold_inds": {
                "text_2": "after zero",
                "table_1": "metric the revenue of 2024 is $10 ;",
            }
        },
    }


def test_gold_keys_parse_source_and_integer_index() -> None:
    assert parse_gold_key("text_12") == ("text", 12)
    assert parse_gold_key("table_0") == ("table", 0)
    assert parse_gold_key("text_-1") == ("text", -1)


def test_gold_values_resolve_to_combined_text_and_table_rows() -> None:
    resolved = resolve_gold_evidence(example_record())

    assert resolved[0]["source_field"] == "post_text"
    assert resolved[0]["source_index"] == 0
    assert resolved[0]["raw_evidence"] == "after zero"
    assert resolved[1]["source_field"] == "table"
    assert resolved[1]["raw_evidence"] == ["revenue", "$10"]
    assert resolved[1]["exact_value_match"] is True


def test_negative_text_index_resolves_legacy_last_sentence() -> None:
    record = example_record()
    record["qa"]["gold_inds"] = {"text_-1": "after one"}

    resolved = resolve_gold_evidence(record)

    assert resolved[0]["combined_text_index"] == 3
    assert resolved[0]["source_field"] == "post_text"
    assert resolved[0]["source_index"] == 1


def test_formats_and_candidate_counts() -> None:
    record = example_record()

    assert gold_format(record) == ("table+text", 2)
    assert candidate_counts(record) == {
        "pre_text_candidates": 2,
        "post_text_candidates": 2,
        "prose_candidates": 4,
        "table_row_candidates": 2,
        "all_evidence_candidates": 6,
        "gold_supporting_facts": 2,
    }


def test_table_serialization_and_annotation_spacing() -> None:
    record = example_record()

    assert serialize_table_row(record["table"], 1) == (
        "metric the revenue of 2024 is $10 ;"
    )
    assert normalize_annotation_spacing("year ended december 31 , value .") == (
        "year ended december 31, value."
    )
