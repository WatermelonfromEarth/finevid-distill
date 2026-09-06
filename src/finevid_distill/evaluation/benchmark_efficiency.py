"""Benchmark Qwen and the selected distilled BGE student on identical hardware."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import statistics
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from finevid_distill.evaluation.evaluate import load_jsonl, write_json
from finevid_distill.evaluation.final_selection import (
    EXPECTED_TEST_DATA_SHA256,
    EXPECTED_TEST_QUESTIONS,
    sha256_file,
    validate_selection_against_runs,
)
from finevid_distill.models.bge_ranker import BGE_QUERY_INSTRUCTION
from finevid_distill.models.teacher import QwenTeacher


BENCHMARK_CANDIDATES = 100


def model_statistics(module: Any) -> dict[str, int]:
    parameters = list(module.parameters())
    buffers = list(module.buffers())
    return {
        "parameter_count": sum(parameter.numel() for parameter in parameters),
        "trainable_parameter_count": sum(
            parameter.numel() for parameter in parameters if parameter.requires_grad
        ),
        "model_size_bytes": sum(
            tensor.numel() * tensor.element_size() for tensor in parameters + buffers
        ),
    }


def build_benchmark_sample(
    records: Sequence[Mapping[str, Any]],
    *,
    candidate_count: int = BENCHMARK_CANDIDATES,
) -> tuple[str, str, list[str], str]:
    if not records or candidate_count <= 0:
        raise ValueError("Benchmark sample requires records and a positive candidate count.")
    candidates: list[str] = []
    seen: set[str] = set()
    for record in records:
        for candidate in record["candidates"]:
            text = str(candidate["text"])
            if text not in seen:
                seen.add(text)
                candidates.append(text)
            if len(candidates) == candidate_count:
                payload = json.dumps(
                    {"question_id": records[0]["question_id"], "candidates": candidates},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
                return (
                    str(records[0]["question_id"]),
                    str(records[0]["question"]),
                    candidates,
                    hashlib.sha256(payload).hexdigest(),
                )
    raise ValueError(f"Could not collect {candidate_count} unique benchmark candidates.")


def median_time_seconds(
    operation: Callable[[], Any],
    *,
    warmup: int,
    repeats: int,
    synchronize: Callable[[], None],
) -> float:
    if warmup < 0 or repeats <= 0:
        raise ValueError("Warmup must be non-negative and repeats must be positive.")
    for _ in range(warmup):
        operation()
        synchronize()
    durations: list[float] = []
    for _ in range(repeats):
        synchronize()
        started = time.perf_counter()
        operation()
        synchronize()
        durations.append(time.perf_counter() - started)
    result = statistics.median(durations)
    if not math.isfinite(result) or result <= 0:
        raise ValueError("Benchmark timer returned a non-positive duration.")
    return result


def format_quality_efficiency_table(models: Mapping[str, Mapping[str, Any]]) -> str:
    headers = (
        "Model", "NDCG@10", "Parameters", "Model MiB", "Peak GPU MiB",
        "Candidate precompute (s)", "Query latency (ms)", "Rank 100 (ms)",
        "Candidates/s",
    )
    lines = ["| " + " | ".join(headers) + " |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for label, values in models.items():
        precompute = values.get("candidate_encoding_time_seconds")
        peak = values.get("peak_memory_bytes")
        row = (
            label,
            f"{values['ndcg_at_10']:.6f}",
            f"{values['parameter_count']:,}",
            f"{values['model_size_bytes'] / 2**20:.2f}",
            "n/a" if peak is None else f"{peak / 2**20:.2f}",
            "n/a" if precompute is None else f"{precompute:.6f}",
            f"{values['query_latency_seconds'] * 1000:.3f}",
            f"{values['rank_100_time_seconds'] * 1000:.3f}",
            f"{values['candidates_per_second']:.2f}",
        )
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def validate_efficiency_payload(
    payload: Mapping[str, Any], quality_results: Mapping[str, Any]
) -> None:
    if payload.get("schema_version") != 1 or payload.get("identical_hardware_verified") is not True:
        raise ValueError("Efficiency result schema or same-hardware verification is invalid.")
    hardware = payload.get("hardware", {})
    if not str(hardware.get("device", "")).startswith("cuda:") or not hardware.get("device_name"):
        raise ValueError("Efficiency result does not identify a CUDA device.")
    if not isinstance(hardware.get("total_memory_bytes"), int) or hardware["total_memory_bytes"] <= 0:
        raise ValueError("Efficiency result has invalid device memory.")
    sample = payload.get("sample", {})
    if sample.get("candidate_count") != BENCHMARK_CANDIDATES or len(
        str(sample.get("sample_sha256", ""))
    ) != 64:
        raise ValueError("Efficiency benchmark sample is invalid.")
    models = payload.get("models", {})
    if set(models) != {"Qwen teacher", "Distilled BGE"}:
        raise ValueError("Efficiency result must compare Qwen teacher and Distilled BGE.")
    for label, values in models.items():
        for key in (
            "parameter_count", "model_size_bytes", "peak_memory_bytes",
            "query_latency_seconds", "rank_100_time_seconds", "candidates_per_second",
        ):
            value = values.get(key)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"Invalid {key} for {label}.")
        expected_rate = BENCHMARK_CANDIDATES / values["rank_100_time_seconds"]
        if not math.isclose(values["candidates_per_second"], expected_rate, rel_tol=1e-12):
            raise ValueError(f"Candidates/second is inconsistent for {label}.")
        expected_ndcg = quality_results["models"][label]["ndcg_at_10"]
        if values.get("ndcg_at_10") != expected_ndcg:
            raise ValueError(f"Quality and efficiency NDCG differ for {label}.")
    teacher, student = models["Qwen teacher"], models["Distilled BGE"]
    if teacher.get("candidate_precomputation_supported") is not False or teacher.get(
        "candidate_encoding_time_seconds"
    ) is not None:
        raise ValueError("Teacher candidate-precomputation fields are invalid.")
    if student.get("candidate_precomputation_supported") is not True:
        raise ValueError("Student must report separate candidate precomputation.")
    if not isinstance(student.get("candidate_encoding_time_seconds"), (int, float)) or not math.isfinite(
        student["candidate_encoding_time_seconds"]
    ) or student["candidate_encoding_time_seconds"] <= 0:
        raise ValueError("Student candidate precomputation time is invalid.")
    if payload.get("teacher_quality_retained") != quality_results.get("teacher_quality_retained"):
        raise ValueError("Quality-retained values differ between final and efficiency results.")


def _cuda_context(device: str) -> tuple[Callable[[], None], dict[str, Any]]:
    import torch

    if not device.startswith("cuda") or not torch.cuda.is_available():
        raise RuntimeError("The final efficiency benchmark requires a CUDA GPU.")
    index = torch.cuda.current_device()

    def synchronize() -> None:
        torch.cuda.synchronize(index)

    properties = torch.cuda.get_device_properties(index)
    hardware = {
        "device": f"cuda:{index}",
        "device_name": properties.name,
        "total_memory_bytes": properties.total_memory,
        "compute_capability": list(torch.cuda.get_device_capability(index)),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
    }
    return synchronize, hardware


def _peak_memory(operation: Callable[[], Any], synchronize: Callable[[], None]) -> int:
    import torch

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    operation()
    synchronize()
    return int(torch.cuda.max_memory_allocated())


def benchmark_teacher(
    question: str,
    candidates: Sequence[str],
    *,
    device: str,
    batch_size: int,
    warmup: int,
    repeats: int,
    synchronize: Callable[[], None],
) -> dict[str, Any]:
    teacher = QwenTeacher(device=device)
    cross_encoder = teacher.model
    stats = model_statistics(cross_encoder.model)
    single_pair = [(question, candidates[0])]
    all_pairs = [(question, candidate) for candidate in candidates]
    query_latency = median_time_seconds(
        lambda: teacher.score_pairs(single_pair, batch_size=1, show_progress=False),
        warmup=warmup,
        repeats=repeats,
        synchronize=synchronize,
    )
    rank_time = median_time_seconds(
        lambda: teacher.score_pairs(all_pairs, batch_size=batch_size, show_progress=False),
        warmup=1,
        repeats=repeats,
        synchronize=synchronize,
    )
    peak = _peak_memory(
        lambda: teacher.score_pairs(all_pairs, batch_size=batch_size, show_progress=False),
        synchronize,
    )
    del teacher, cross_encoder
    gc.collect()
    import torch

    torch.cuda.empty_cache()
    return {
        **stats,
        "candidate_precomputation_supported": False,
        "candidate_encoding_time_seconds": None,
        "query_latency_definition": "one query-candidate cross-encoder score",
        "query_latency_seconds": query_latency,
        "rank_100_time_seconds": rank_time,
        "candidates_per_second": len(candidates) / rank_time,
        "peak_memory_bytes": peak,
    }


def benchmark_student(
    model_path: Path,
    question: str,
    candidates: Sequence[str],
    *,
    device: str,
    batch_size: int,
    warmup: int,
    repeats: int,
    synchronize: Callable[[], None],
) -> dict[str, Any]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(str(model_path), device=device, local_files_only=True)
    model.eval()
    stats = model_statistics(model)

    def encode_candidates():
        return model.encode(
            list(candidates), batch_size=batch_size, normalize_embeddings=True,
            convert_to_numpy=True, show_progress_bar=False,
        )

    candidate_time = median_time_seconds(
        encode_candidates,
        warmup=1,
        repeats=repeats,
        synchronize=synchronize,
    )
    candidate_embeddings = np.asarray(encode_candidates())
    instructed_question = BGE_QUERY_INSTRUCTION + question

    def encode_query():
        return model.encode(
            [instructed_question], batch_size=1, normalize_embeddings=True,
            convert_to_numpy=True, show_progress_bar=False,
        )

    def rank_candidates():
        query = np.asarray(encode_query())[0]
        scores = candidate_embeddings @ query
        return np.argsort(-scores, kind="stable")

    query_latency = median_time_seconds(
        encode_query, warmup=warmup, repeats=repeats, synchronize=synchronize
    )
    rank_time = median_time_seconds(
        rank_candidates, warmup=warmup, repeats=repeats, synchronize=synchronize
    )
    candidate_peak = _peak_memory(encode_candidates, synchronize)
    rank_peak = _peak_memory(rank_candidates, synchronize)
    del model, candidate_embeddings
    gc.collect()
    import torch

    torch.cuda.empty_cache()
    return {
        **stats,
        "candidate_precomputation_supported": True,
        "candidate_encoding_time_seconds": candidate_time,
        "query_latency_definition": "encode one instructed query",
        "query_latency_seconds": query_latency,
        "rank_100_time_seconds": rank_time,
        "candidates_per_second": len(candidates) / rank_time,
        "peak_memory_bytes": max(candidate_peak, rank_peak),
        "candidate_precompute_peak_memory_bytes": candidate_peak,
        "online_rank_peak_memory_bytes": rank_peak,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=root / "outputs/final_selection.json")
    parser.add_argument("--test-data", type=Path, default=root / "data/processed/test.jsonl")
    parser.add_argument("--quality-results", type=Path, required=True)
    parser.add_argument(
        "--hard-dir", type=Path, default=root / "outputs/checkpoints/hard_label_student_tau005"
    )
    parser.add_argument(
        "--distilled-dir", type=Path, default=root / "outputs/checkpoints/distilled_student"
    )
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--teacher-batch-size", type=int, default=16)
    parser.add_argument("--student-batch-size", type=int, default=64)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path, default=root / "outputs/efficiency_results.json")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if min(args.teacher_batch_size, args.student_batch_size, args.repeats) <= 0 or args.warmup < 0:
        raise ValueError("Batch sizes/repeats must be positive and warmup non-negative.")
    if sha256_file(args.test_data) != EXPECTED_TEST_DATA_SHA256:
        raise ValueError("Benchmark test data does not match the frozen split.")
    records = load_jsonl(args.test_data)
    if len(records) != EXPECTED_TEST_QUESTIONS:
        raise ValueError("Benchmark test question count changed.")
    selected = validate_selection_against_runs(
        args.selection, args.hard_dir, args.distilled_dir
    )
    quality = json.loads(args.quality_results.read_text(encoding="utf-8"))
    if (
        quality.get("split") != "test"
        or quality.get("test_data_sha256") != EXPECTED_TEST_DATA_SHA256
        or quality.get("selection_sha256") != sha256_file(args.selection)
    ):
        raise ValueError("Quality results do not match the locked final evaluation.")
    question_id, question, candidates, sample_sha = build_benchmark_sample(records)
    synchronize, hardware = _cuda_context(args.device)
    teacher = benchmark_teacher(
        question, candidates, device=args.device, batch_size=args.teacher_batch_size,
        warmup=args.warmup, repeats=args.repeats, synchronize=synchronize,
    )
    student = benchmark_student(
        selected["distilled"], question, candidates, device=args.device,
        batch_size=args.student_batch_size, warmup=args.warmup,
        repeats=args.repeats, synchronize=synchronize,
    )
    teacher["ndcg_at_10"] = quality["models"]["Qwen teacher"]["ndcg_at_10"]
    student["ndcg_at_10"] = quality["models"]["Distilled BGE"]["ndcg_at_10"]
    models = {"Qwen teacher": teacher, "Distilled BGE": student}
    payload = {
        "schema_version": 1,
        "hardware": hardware,
        "identical_hardware_verified": True,
        "sample": {
            "question_id": question_id,
            "candidate_count": len(candidates),
            "sample_sha256": sample_sha,
        },
        "methodology": {
            "warmup_runs": args.warmup,
            "measured_repeats": args.repeats,
            "reported_statistic": "median",
            "peak_memory_definition": "maximum CUDA bytes allocated with the model resident",
            "student_online_ranking": "precomputed normalized candidates plus query encode and cosine ranking",
            "teacher_online_ranking": "cross-encode all query-candidate pairs",
        },
        "models": models,
        "teacher_quality_retained": quality["teacher_quality_retained"],
    }
    validate_efficiency_payload(payload, quality)
    write_json(payload, args.output)
    print(format_quality_efficiency_table(models))
    print(f"\nSaved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
