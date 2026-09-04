from pathlib import Path

import pytest

from finevid_distill.config import ConfigError, load_config, validate_beginner_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "beginner.yaml"


def test_beginner_config_locks_experiment_contract() -> None:
    config = load_config(CONFIG_PATH)

    assert config["dataset"]["name"] == "FinQA"
    assert config["dataset"]["retrieval_unit"] == "report"
    assert config["dataset"]["candidate_unit"] == "evidence_entry"
    assert (
        config["dataset"]["candidate_pool"]
        == "all_prose_entries_and_table_rows_in_the_question_report"
    )
    assert config["models"]["teacher"]["model_id"] == "Qwen/Qwen3-Reranker-0.6B"
    assert config["models"]["student"]["model_id"] == "BAAI/bge-small-en-v1.5"
    assert config["experiment"]["seed"] == 42
    assert config["dataset"]["training_candidates"]["approximate_per_question"] == 8
    assert config["dataset"]["training_candidates"]["positives"] == "all_gold_evidence"
    assert (
        config["dataset"]["training_candidates"]["negative_strategy"]
        == "seeded_uniform_without_replacement_within_report"
    )
    assert config["training"]["hard_label_objective"] == "listwise_cross_entropy"
    assert (
        config["training"]["hard_label_target"]
        == "equal_probability_over_all_gold_candidates"
    )
    assert config["split_policy"]["allow_test_tuning"] is False
    assert config["evaluation"]["metrics"] == [
        "recall_at_1",
        "recall_at_5",
        "mrr",
        "ndcg_at_10",
        "complete_recall_at_5",
    ]
    assert config["models"]["teacher"]["cached_score_type"] == "raw_logit_difference"
    assert config["models"]["teacher"]["temperature_applied_when_cached"] is False


def test_beginner_config_contains_all_required_comparisons() -> None:
    config = load_config(CONFIG_PATH)

    assert [row["id"] for row in config["comparisons"]] == [
        "bm25",
        "frozen_bge_small",
        "hard_label_bge_small",
        "distilled_bge_small",
        "qwen_teacher",
    ]
    hard_label = next(
        row for row in config["comparisons"] if row["id"] == "hard_label_bge_small"
    )
    assert hard_label["supervision"] == "equal_probability_over_all_gold_candidates"


def test_validator_rejects_scope_drift() -> None:
    config = load_config(CONFIG_PATH)
    config["experiment"]["seed"] = 7

    with pytest.raises(ConfigError, match="experiment.seed"):
        validate_beginner_config(config)
