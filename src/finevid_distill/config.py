"""Load and validate the beginner experiment contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml


EXPECTED_COMPARISONS = [
    "bm25",
    "frozen_bge_small",
    "hard_label_bge_small",
    "distilled_bge_small",
    "qwen_teacher",
]
EXPECTED_METRICS = [
    "recall_at_1",
    "recall_at_5",
    "mrr",
    "ndcg_at_10",
    "complete_recall_at_5",
]


class ConfigError(ValueError):
    """Raised when an experiment configuration violates the fixed contract."""


def load_config(path: str | Path) -> dict[str, Any]:
    """Read a YAML configuration and verify the fixed beginner experiment."""
    config_path = Path(path)
    with config_path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if not isinstance(config, dict):
        raise ConfigError("The configuration root must be a mapping.")

    validate_beginner_config(config)
    return config


def validate_beginner_config(config: Mapping[str, Any]) -> None:
    """Validate the choices that define the beginner experiment."""
    try:
        experiment = config["experiment"]
        dataset = config["dataset"]
        models = config["models"]
        evaluation = config["evaluation"]
        split_policy = config["split_policy"]
        comparisons = config["comparisons"]
        training = config["training"]
    except KeyError as error:
        raise ConfigError(f"Missing required section: {error.args[0]}") from error

    checks = {
        "dataset.name": (dataset.get("name"), "FinQA"),
        "dataset.retrieval_unit": (dataset.get("retrieval_unit"), "report"),
        "dataset.candidate_unit": (
            dataset.get("candidate_unit"),
            "evidence_entry",
        ),
        "dataset.candidate_pool": (
            dataset.get("candidate_pool"),
            "all_prose_entries_and_table_rows_in_the_question_report",
        ),
        "teacher model": (
            models.get("teacher", {}).get("model_id"),
            "Qwen/Qwen3-Reranker-0.6B",
        ),
        "teacher score type": (
            models.get("teacher", {}).get("cached_score_type"),
            "raw_logit_difference",
        ),
        "teacher cached temperature": (
            models.get("teacher", {}).get("temperature_applied_when_cached"),
            False,
        ),
        "student model": (
            models.get("student", {}).get("model_id"),
            "BAAI/bge-small-en-v1.5",
        ),
        "experiment.seed": (experiment.get("seed"), 42),
        "training candidate count": (
            dataset.get("training_candidates", {}).get("approximate_per_question"),
            8,
        ),
        "training positives": (
            dataset.get("training_candidates", {}).get("positives"),
            "all_gold_evidence",
        ),
        "training negative strategy": (
            dataset.get("training_candidates", {}).get("negative_strategy"),
            "seeded_uniform_without_replacement_within_report",
        ),
        "hard-label objective": (
            training.get("hard_label_objective"),
            "listwise_cross_entropy",
        ),
        "hard-label target": (
            training.get("hard_label_target"),
            "equal_probability_over_all_gold_candidates",
        ),
        "evaluation.primary_metric": (evaluation.get("primary_metric"), "mrr"),
        "split_policy.allow_test_tuning": (
            split_policy.get("allow_test_tuning"),
            False,
        ),
    }

    for label, (actual, expected) in checks.items():
        if actual != expected:
            raise ConfigError(f"{label} must be {expected!r}; got {actual!r}.")

    comparison_ids = [comparison.get("id") for comparison in comparisons]
    if comparison_ids != EXPECTED_COMPARISONS:
        raise ConfigError(
            "comparisons must contain the five required systems in contract order; "
            f"got {comparison_ids!r}."
        )
    hard_label_supervision = comparisons[2].get("supervision")
    if hard_label_supervision != "equal_probability_over_all_gold_candidates":
        raise ConfigError(
            "hard-label supervision must be equal_probability_over_all_gold_candidates; "
            f"got {hard_label_supervision!r}."
        )

    if evaluation.get("metrics") != EXPECTED_METRICS:
        raise ConfigError(
            f"evaluation.metrics must be {EXPECTED_METRICS!r}; "
            f"got {evaluation.get('metrics')!r}."
        )
