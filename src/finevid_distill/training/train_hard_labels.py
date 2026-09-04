"""Train BGE-small with equal-mass hard labels and listwise cross-entropy."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import random
import time
from collections.abc import Mapping, Sequence
from contextlib import nullcontext
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

from finevid_distill.data.build_training_rows import (
    EXPECTED_SEED,
    TARGET_CANDIDATES,
)
from finevid_distill.evaluation.evaluate import (
    evaluate_ranker,
    format_markdown_table,
    load_jsonl,
    write_json,
)
from finevid_distill.models.bge_ranker import (
    BGE_MODEL_ID,
    BGE_MODEL_REVISION,
    BGE_QUERY_INSTRUCTION,
    BGERanker,
    resolve_device,
)


DEFAULT_EPOCHS = 3
DEFAULT_QUESTIONS_PER_BATCH = 8
DEFAULT_LEARNING_RATE = 2e-5
DEFAULT_WEIGHT_DECAY = 0.01
DEFAULT_WARMUP_RATIO = 0.1
DEFAULT_MAX_GRADIENT_NORM = 1.0
DEFAULT_MAX_SEQUENCE_LENGTH = 512


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def set_reproducible_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def validate_loaded_training_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError("No training rows were loaded.")
    seen: set[str] = set()
    for row in rows:
        question_id = row.get("question_id")
        if not isinstance(question_id, str) or not question_id:
            raise ValueError("Every training row needs a question_id.")
        if question_id in seen:
            raise ValueError(f"Duplicate training question ID: {question_id}")
        seen.add(question_id)
        if not isinstance(row.get("question"), str) or not row["question"].strip():
            raise ValueError(f"Empty training question for {question_id}.")

        fields = [
            row.get("candidate_ids"),
            row.get("candidate_texts"),
            row.get("positive_mask"),
            row.get("teacher_scores"),
        ]
        if not all(isinstance(field, list) for field in fields):
            raise ValueError(f"Malformed training-row lists for {question_id}.")
        lengths = {len(field) for field in fields}
        if len(lengths) != 1 or not fields[0]:
            raise ValueError(f"Training-row lengths do not match for {question_id}.")
        if len(fields[0]) != len(set(fields[0])):
            raise ValueError(f"Duplicate candidate IDs for {question_id}.")
        if any(value not in (0, 1) for value in fields[2]) or not any(fields[2]):
            raise ValueError(f"Invalid or zero-positive mask for {question_id}.")
        if len(fields[0]) > max(TARGET_CANDIDATES, sum(fields[2])):
            raise ValueError(f"Too many candidates in the fixed row for {question_id}.")
        if any(not isinstance(text, str) or not text.strip() for text in fields[1]):
            raise ValueError(f"Empty candidate text for {question_id}.")
        try:
            numeric_scores = [float(score) for score in fields[3]]
        except (TypeError, ValueError) as error:
            raise ValueError(f"Non-numeric teacher scores for {question_id}.") from error
        if not all(math.isfinite(score) for score in numeric_scores):
            raise ValueError(f"Non-finite teacher scores for {question_id}.")


def equal_positive_target(
    positive_mask: Sequence[int] | torch.Tensor,
    *,
    device: torch.device | str | None = None,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Place equal probability mass on every gold candidate and zero elsewhere."""
    mask = torch.as_tensor(positive_mask, dtype=dtype, device=device)
    if mask.ndim != 1 or mask.numel() == 0:
        raise ValueError("positive_mask must be a non-empty one-dimensional vector.")
    if not torch.all((mask == 0) | (mask == 1)):
        raise ValueError("positive_mask must be binary.")
    positive_count = mask.sum()
    if positive_count.item() <= 0:
        raise ValueError("positive_mask must contain at least one positive.")
    return mask / positive_count


def listwise_cross_entropy(
    score_rows: Sequence[torch.Tensor],
    positive_masks: Sequence[Sequence[int] | torch.Tensor],
) -> torch.Tensor:
    """Mean cross-entropy from listwise scores to equal-mass gold targets."""
    if not score_rows or len(score_rows) != len(positive_masks):
        raise ValueError("Scores and positive masks must contain the same non-zero rows.")
    losses: list[torch.Tensor] = []
    for scores, positive_mask in zip(score_rows, positive_masks, strict=True):
        if scores.ndim != 1 or scores.numel() == 0:
            raise ValueError("Every score row must be a non-empty vector.")
        target = equal_positive_target(
            positive_mask,
            device=scores.device,
            dtype=scores.dtype,
        )
        if target.shape != scores.shape:
            raise ValueError("A score row and its target mask have different lengths.")
        losses.append(-(target * F.log_softmax(scores, dim=0)).sum())
    return torch.stack(losses).mean()


def _move_features(features: Mapping[str, Any], device: torch.device) -> dict[str, Any]:
    return {
        key: value.to(device) if hasattr(value, "to") else value
        for key, value in features.items()
    }


def encode_with_grad(
    model: Any,
    texts: Sequence[str],
    *,
    device: torch.device,
) -> torch.Tensor:
    preprocess = getattr(model, "preprocess", None)
    features = (
        preprocess(list(texts))
        if callable(preprocess)
        else model.tokenize(list(texts))
    )
    features = _move_features(features, device)
    output = model(features)
    if "sentence_embedding" not in output:
        raise ValueError("Student model did not return sentence embeddings.")
    return F.normalize(output["sentence_embedding"], p=2, dim=1)


def training_batch_loss(
    model: Any,
    rows: Sequence[Mapping[str, Any]],
    *,
    device: torch.device,
    query_instruction: str = BGE_QUERY_INSTRUCTION,
) -> torch.Tensor:
    if not rows:
        raise ValueError("Cannot train on an empty batch.")
    questions = [query_instruction + str(row["question"]) for row in rows]
    candidate_texts = [
        str(text)
        for row in rows
        for text in row["candidate_texts"]
    ]
    question_embeddings = encode_with_grad(model, questions, device=device)
    candidate_embeddings = encode_with_grad(model, candidate_texts, device=device)

    score_rows: list[torch.Tensor] = []
    offset = 0
    for question_embedding, row in zip(question_embeddings, rows, strict=True):
        candidate_count = len(row["candidate_texts"])
        block = candidate_embeddings[offset : offset + candidate_count]
        score_rows.append(block @ question_embedding)
        offset += candidate_count
    if offset != len(candidate_embeddings):
        raise ValueError("Candidate embeddings could not be partitioned by question.")
    return listwise_cross_entropy(
        score_rows,
        [row["positive_mask"] for row in rows],
    )


def epoch_batches(
    rows: Sequence[Mapping[str, Any]],
    *,
    questions_per_batch: int,
    seed: int,
    epoch: int,
) -> list[list[Mapping[str, Any]]]:
    if questions_per_batch <= 0:
        raise ValueError("questions_per_batch must be positive.")
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed + epoch * 1_000_003)
    order = torch.randperm(len(rows), generator=generator).tolist()
    return [
        [rows[index] for index in order[start : start + questions_per_batch]]
        for start in range(0, len(order), questions_per_batch)
    ]


def train_one_epoch(
    model: Any,
    rows: Sequence[Mapping[str, Any]],
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    *,
    device: torch.device,
    questions_per_batch: int,
    seed: int,
    epoch: int,
    max_gradient_norm: float,
    scaler: Any | None = None,
    use_fp16: bool = False,
    show_progress: bool = True,
) -> dict[str, float | int]:
    model.train()
    total_loss = 0.0
    total_questions = 0
    gradient_norms: list[float] = []
    batches = epoch_batches(
        rows,
        questions_per_batch=questions_per_batch,
        seed=seed,
        epoch=epoch,
    )
    for batch_index, batch in enumerate(batches, start=1):
        optimizer.zero_grad(set_to_none=True)
        context = (
            torch.autocast(device_type="cuda", dtype=torch.float16)
            if use_fp16
            else nullcontext()
        )
        with context:
            loss = training_batch_loss(model, batch, device=device)
        if scaler is not None:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
        else:
            loss.backward()
        gradient_norm = torch.nn.utils.clip_grad_norm_(
            model.parameters(), max_gradient_norm
        )
        if not torch.isfinite(gradient_norm):
            raise FloatingPointError("Encountered a non-finite gradient norm.")
        if scaler is not None:
            scaler.step(optimizer)
            scaler.update()
        else:
            optimizer.step()
        scheduler.step()

        total_loss += float(loss.detach().cpu()) * len(batch)
        total_questions += len(batch)
        gradient_norms.append(float(gradient_norm.detach().cpu()))
        if show_progress and (
            batch_index == 1
            or batch_index == len(batches)
            or batch_index % 25 == 0
        ):
            print(
                f"Epoch {epoch}: batch {batch_index:,}/{len(batches):,}, "
                f"mean_loss={total_loss / total_questions:.6f}",
                flush=True,
            )
    return {
        "training_loss": total_loss / total_questions,
        "gradient_norm": sum(gradient_norms) / len(gradient_norms),
        "optimizer_steps": len(batches),
        "learning_rate": float(optimizer.param_groups[0]["lr"]),
    }


def linear_warmup_decay(
    current_step: int,
    *,
    warmup_steps: int,
    total_steps: int,
) -> float:
    if warmup_steps > 0 and current_step < warmup_steps:
        return current_step / max(1, warmup_steps)
    return max(
        0.0,
        (total_steps - current_step) / max(1, total_steps - warmup_steps),
    )


def capture_rng_state() -> dict[str, Any]:
    return {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch_cpu": torch.random.get_rng_state(),
        "torch_cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
    }


def restore_rng_state(state: Mapping[str, Any]) -> None:
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.random.set_rng_state(state["torch_cpu"])
    if torch.cuda.is_available() and state.get("torch_cuda") is not None:
        torch.cuda.set_rng_state_all(state["torch_cuda"])


def save_epoch_checkpoint(
    output_dir: Path,
    model: Any,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    *,
    completed_epoch: int,
    global_step: int,
    scaler: Any | None,
    epoch_metrics: Mapping[str, Any],
) -> Path:
    epochs_dir = output_dir / "epochs"
    epochs_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = epochs_dir / f"epoch-{completed_epoch:03d}"
    if checkpoint.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {checkpoint}")
    temporary = epochs_dir / f".epoch-{completed_epoch:03d}.incomplete"
    if temporary.exists():
        raise FileExistsError(
            f"Incomplete checkpoint exists; inspect it before retrying: {temporary}"
        )
    temporary.mkdir()
    model.save_pretrained(temporary / "model")
    trainer_state = {
        "completed_epoch": completed_epoch,
        "global_step": global_step,
        "optimizer": optimizer.state_dict(),
        "scheduler": scheduler.state_dict(),
        "scaler": scaler.state_dict() if scaler is not None else None,
        "rng": capture_rng_state(),
    }
    state_temporary = temporary / "trainer_state.pt.tmp"
    torch.save(trainer_state, state_temporary)
    state_temporary.replace(temporary / "trainer_state.pt")
    write_json(dict(epoch_metrics), temporary / "epoch_metrics.json")
    temporary.replace(checkpoint)
    return checkpoint


def load_trainer_state(
    checkpoint: Path,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    *,
    scaler: Any | None,
) -> dict[str, Any]:
    state = torch.load(
        checkpoint / "trainer_state.pt",
        map_location="cpu",
        weights_only=False,
    )
    optimizer.load_state_dict(state["optimizer"])
    scheduler.load_state_dict(state["scheduler"])
    if scaler is not None and state.get("scaler") is not None:
        scaler.load_state_dict(state["scaler"])
    restore_rng_state(state["rng"])
    return state


def load_student_model(
    source: str | Path,
    *,
    revision: str | None,
    device: str,
    max_sequence_length: int,
    local_files_only: bool,
) -> Any:
    from sentence_transformers import SentenceTransformer

    kwargs: dict[str, Any] = {
        "device": device,
        "local_files_only": local_files_only,
    }
    if revision is not None:
        kwargs["revision"] = revision
    model = SentenceTransformer(str(source), **kwargs)
    model.max_seq_length = max_sequence_length
    return model


def evaluate_student(
    model: Any,
    dev_records: Sequence[Mapping[str, Any]],
    *,
    device: str,
    batch_size: int,
    show_progress: bool,
) -> dict[str, float]:
    ranker = BGERanker(
        device=device,
        batch_size=batch_size,
        show_progress=show_progress,
        model_instance=model,
        label="Hard-label BGE-small",
    )
    return evaluate_ranker(dev_records, ranker)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train-rows",
        type=Path,
        default=root / "data" / "processed" / "train_rows.jsonl",
    )
    parser.add_argument(
        "--dev-data",
        type=Path,
        default=root / "data" / "processed" / "dev.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "outputs" / "checkpoints" / "hard_label_student",
    )
    parser.add_argument("--model", default=BGE_MODEL_ID)
    parser.add_argument("--revision", default=BGE_MODEL_REVISION)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seed", type=int, default=EXPECTED_SEED)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument(
        "--questions-per-batch", type=int, default=DEFAULT_QUESTIONS_PER_BATCH
    )
    parser.add_argument("--learning-rate", type=float, default=DEFAULT_LEARNING_RATE)
    parser.add_argument("--weight-decay", type=float, default=DEFAULT_WEIGHT_DECAY)
    parser.add_argument("--warmup-ratio", type=float, default=DEFAULT_WARMUP_RATIO)
    parser.add_argument(
        "--max-gradient-norm", type=float, default=DEFAULT_MAX_GRADIENT_NORM
    )
    parser.add_argument(
        "--max-sequence-length", type=int, default=DEFAULT_MAX_SEQUENCE_LENGTH
    )
    parser.add_argument("--evaluation-batch-size", type=int, default=64)
    parser.add_argument("--mixed-precision", choices=("none", "fp16"), default="fp16")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--allow-cpu", action="store_true")
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--limit-train", type=int)
    parser.add_argument("--limit-dev", type=int)
    parser.add_argument("--no-progress", action="store_true")
    return parser.parse_args(argv)


def _validate_args(args: argparse.Namespace) -> None:
    if args.seed != EXPECTED_SEED:
        raise ValueError(f"The beginner experiment seed must be {EXPECTED_SEED}.")
    if args.dev_data.name != "dev.jsonl":
        raise ValueError("Only the development split may be used during training.")
    positive_values = {
        "epochs": args.epochs,
        "questions_per_batch": args.questions_per_batch,
        "learning_rate": args.learning_rate,
        "max_gradient_norm": args.max_gradient_norm,
        "max_sequence_length": args.max_sequence_length,
        "evaluation_batch_size": args.evaluation_batch_size,
    }
    for name, value in positive_values.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive.")
    if args.weight_decay < 0 or not 0 <= args.warmup_ratio < 1:
        raise ValueError("weight_decay must be non-negative and warmup_ratio in [0, 1).")


def _run_configuration(
    args: argparse.Namespace,
    *,
    train_rows_hash: str,
    dev_data_hash: str,
) -> dict[str, Any]:
    return {
        "model_id": args.model,
        "model_revision": args.revision,
        "seed": args.seed,
        "epochs": args.epochs,
        "questions_per_batch": args.questions_per_batch,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "warmup_ratio": args.warmup_ratio,
        "max_gradient_norm": args.max_gradient_norm,
        "max_sequence_length": args.max_sequence_length,
        "mixed_precision": args.mixed_precision,
        "objective": "listwise_cross_entropy",
        "target": "equal_probability_over_all_gold_candidates",
        "query_instruction": BGE_QUERY_INSTRUCTION,
        "normalize_embeddings": True,
        "train_rows_sha256": train_rows_hash,
        "dev_data_sha256": dev_data_hash,
        "limit_train": args.limit_train,
        "limit_dev": args.limit_dev,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _validate_args(args)
    device_name = resolve_device(args.device)
    if device_name == "cpu" and not args.allow_cpu:
        raise RuntimeError(
            "Full BGE training requires a GPU. Use the Colab training notebook, or "
            "pass --allow-cpu only for a small --limit-train diagnostic."
        )
    if args.mixed_precision == "fp16" and device_name != "cuda":
        raise ValueError("fp16 training requires a CUDA device.")

    set_reproducible_seed(args.seed)
    train_rows = load_jsonl(args.train_rows, args.limit_train)
    dev_records = load_jsonl(args.dev_data, args.limit_dev)
    validate_loaded_training_rows(train_rows)
    output_dir: Path = args.output_dir
    latest_path = output_dir / "latest.json"
    run_config_path = output_dir / "run_config.json"
    history_path = output_dir / "training_history.json"

    run_config = _run_configuration(
        args,
        train_rows_hash=sha256_file(args.train_rows),
        dev_data_hash=sha256_file(args.dev_data),
    )
    if args.resume:
        if not latest_path.exists() or not run_config_path.exists():
            raise FileNotFoundError("No resumable hard-label checkpoint was found.")
        stored_config = json.loads(run_config_path.read_text(encoding="utf-8"))
        if stored_config != run_config:
            raise ValueError("Resume configuration differs from the original run.")
        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        resume_checkpoint = output_dir / latest["checkpoint"]
        model = load_student_model(
            resume_checkpoint / "model",
            revision=None,
            device=device_name,
            max_sequence_length=args.max_sequence_length,
            local_files_only=True,
        )
        history = json.loads(history_path.read_text(encoding="utf-8"))["epochs"]
        start_epoch = int(latest["completed_epoch"]) + 1
        global_step = int(latest["global_step"])
    else:
        if latest_path.exists() or run_config_path.exists():
            raise FileExistsError(
                f"Output already contains a run; use --resume or a new directory: {output_dir}"
            )
        output_dir.mkdir(parents=True, exist_ok=True)
        write_json(run_config, run_config_path)
        model = load_student_model(
            args.model,
            revision=args.revision,
            device=device_name,
            max_sequence_length=args.max_sequence_length,
            local_files_only=args.local_files_only,
        )
        history = []
        start_epoch = 1
        global_step = 0

    model.to(torch.device(device_name))
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    steps_per_epoch = math.ceil(len(train_rows) / args.questions_per_batch)
    total_steps = steps_per_epoch * args.epochs
    warmup_steps = int(total_steps * args.warmup_ratio)
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer,
        lambda step: linear_warmup_decay(
            step,
            warmup_steps=warmup_steps,
            total_steps=total_steps,
        ),
    )
    use_fp16 = args.mixed_precision == "fp16"
    scaler = torch.amp.GradScaler("cuda", enabled=True) if use_fp16 else None

    if args.resume:
        state = load_trainer_state(
            resume_checkpoint,
            optimizer,
            scheduler,
            scaler=scaler,
        )
        if int(state["completed_epoch"]) + 1 != start_epoch:
            raise ValueError("Latest checkpoint and pointer disagree about the epoch.")

    best_path = output_dir / "best.json"
    if best_path.exists():
        best = json.loads(best_path.read_text(encoding="utf-8"))
        best_mrr = float(best["development_metrics"]["mrr"])
    else:
        best = None
        best_mrr = -math.inf

    for epoch in range(start_epoch, args.epochs + 1):
        started = time.perf_counter()
        train_metrics = train_one_epoch(
            model,
            train_rows,
            optimizer,
            scheduler,
            device=torch.device(device_name),
            questions_per_batch=args.questions_per_batch,
            seed=args.seed,
            epoch=epoch,
            max_gradient_norm=args.max_gradient_norm,
            scaler=scaler,
            use_fp16=use_fp16,
            show_progress=not args.no_progress,
        )
        global_step += int(train_metrics["optimizer_steps"])
        development_metrics = evaluate_student(
            model,
            dev_records,
            device=device_name,
            batch_size=args.evaluation_batch_size,
            show_progress=not args.no_progress,
        )
        epoch_record = {
            "epoch": epoch,
            **train_metrics,
            "development_mrr": development_metrics["mrr"],
            "development_ndcg_at_10": development_metrics["ndcg_at_10"],
            "development_metrics": development_metrics,
            "epoch_time_seconds": time.perf_counter() - started,
        }
        history.append(epoch_record)
        checkpoint = save_epoch_checkpoint(
            output_dir,
            model,
            optimizer,
            scheduler,
            completed_epoch=epoch,
            global_step=global_step,
            scaler=scaler,
            epoch_metrics=epoch_record,
        )
        relative_checkpoint = checkpoint.relative_to(output_dir).as_posix()
        latest = {
            "completed_epoch": epoch,
            "global_step": global_step,
            "checkpoint": relative_checkpoint,
        }
        write_json(latest, latest_path)
        write_json({"epochs": history}, history_path)
        if development_metrics["mrr"] > best_mrr:
            best_mrr = development_metrics["mrr"]
            best = {
                **latest,
                "development_metrics": development_metrics,
            }
            write_json(best, best_path)
        print(
            f"Epoch {epoch}/{args.epochs}: loss={train_metrics['training_loss']:.6f}, "
            f"dev_mrr={development_metrics['mrr']:.6f}, "
            f"dev_ndcg@10={development_metrics['ndcg_at_10']:.6f}"
        )

    if best is None:
        raise RuntimeError("Training produced no best checkpoint.")
    best_checkpoint = output_dir / best["checkpoint"]
    expected_metrics = best["development_metrics"]

    del optimizer, scheduler, scaler, model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    reloaded_model = load_student_model(
        best_checkpoint / "model",
        revision=None,
        device=device_name,
        max_sequence_length=args.max_sequence_length,
        local_files_only=True,
    )
    reloaded_metrics = evaluate_student(
        reloaded_model,
        dev_records,
        device=device_name,
        batch_size=args.evaluation_batch_size,
        show_progress=not args.no_progress,
    )
    for metric, expected in expected_metrics.items():
        if not math.isclose(reloaded_metrics[metric], expected, abs_tol=1e-12):
            raise RuntimeError(f"Reloaded checkpoint changed development {metric}.")
    verification = {
        "checkpoint": best["checkpoint"],
        "completed_epoch": best["completed_epoch"],
        "development_metrics": reloaded_metrics,
        "reload_verified": True,
    }
    write_json(verification, output_dir / "best_reload_verification.json")
    print()
    print(format_markdown_table({"Hard-label BGE-small": reloaded_metrics}))
    print(f"\nBest checkpoint reloaded successfully: {best_checkpoint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
