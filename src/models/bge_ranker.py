"""Requested-path entry point for the frozen BGE ranker."""

from finevid_distill.models.bge_ranker import (
    BGE_MODEL_ID,
    BGE_MODEL_REVISION,
    BGE_QUERY_INSTRUCTION,
    BGERanker,
)

__all__ = [
    "BGE_MODEL_ID",
    "BGE_MODEL_REVISION",
    "BGE_QUERY_INSTRUCTION",
    "BGERanker",
]
