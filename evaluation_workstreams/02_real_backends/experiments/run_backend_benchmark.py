from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import statistics
import sys
import time
from dataclasses import asdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from typing import Any

from te_backend_upgrade.canonical import make_evidence
from te_backend_upgrade.merkle_log import MerkleLog


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct
    lo = int(rank)
    hi = min(lo + 1, len(ordered) - 1)
    frac = rank - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def sample_indices(n: int, target: int = 128) -> list[int]:
    if n <= target:
        return list(range(n))
    return sorted(set(round(i * (n - 1) / (target - 1)) for i in range(target)))


def median_int(values: list[int]) -> int:
    return int(statistics.median(values)) if values else 0


def run_merkle_once(n: int, repetition: int, raw_dir: Path, warmup: bool = False) -> dict[str, Any]:
    log = MerkleLog()
    append_latencies: list[float] = []
    objects: list[dict[str, Any]] = []
    root_history: dict[int, str] = {}
    for i in range(n):
        obj = make_evidence(repetition * 1_000_000 + i, backend="A2_MERKLE")
        t0 = time.perf_counter_ns()
        receipt = log.append(obj)
        append_latencies.append((time.perf_counter_ns() - t0) / 1_000_000)
        objects.append(obj)
        if receipt.tree_size in {1, 10, 100, 1000, n}:
            root_history[receipt.tree_size] = receipt.root_hash

    verify_latencies: list[float] = []
    receipt_sizes: list[int] = []
    proof_sizes: list[int] = []
    verify_failures = 0
    for idx in sample_indices(n):
        obj = objects[idx]
        receipt = log.inclusion_receipt(idx)
        receipt_payload = asdict(receipt)
        t0 = time.perf_counter_ns()
        ok = MerkleLog.verify_receipt(obj, receipt)
        verify_latencies.append((time.perf_counter_ns() - t0) / 1_000_000)
        if not ok:
            verify_failures += 1
        receipt_sizes.append(len(json.dumps(receipt_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")))
        proof_sizes.append(len(json.dumps(receipt.proof, sort_keys=True, separators=(",", ":")).encode("utf-8")))

    if 1000 in root_history:
        consistency_ok = log.verify_consistency_by_prefix(1000, root_history[1000])
    elif n >= 10:
        consistency_ok = log.verify_consistency_by_prefix(10, root_history[10])
    else:
        consistency_ok = True

    result: dict[str, Any] = {
        "backend": "A2_MERKLE",
        "status": "executed" if verify_failures == 0 and consistency_ok else "failed",
        "object_count": n,
        "repetition": repetition,
        "warmup_discarded": bool(warmup),
        "append_p50_ms": percentile(append_latencies, 0.50),
        "append_p95_ms": percentile(append_latencies, 0.95),
        "verify_p50_ms": percentile(verify_latencies, 0.50),
        "verify_p95_ms": percentile(verify_latencies, 0.95),
        "verification_samples": len(verify_latencies),
        "verification_failures": verify_failures,
        "storage_bytes": log.storage_bytes(),
        "receipt_size_bytes_median": median_int(receipt_sizes),
        "proof_size_bytes_median": median_int(proof_sizes),
        "root_hash": log.root_hash(),
        "consistency_by_prefix_status": "pass" if consistency_ok else "fail",
    }
    if not warmup:
        raw_path = raw_dir / f"A2_MERKLE_n{n}_rep{repetition}.json"
        raw_path.write_text(json.dumps({
            "summary": result,
            "append_latency_ms_sample_first_100": append_latencies[:100],
            "verify_latency_ms": verify_latencies,
            "root_history": root_history,
        }, indent=2, sort_keys=True), encoding="utf-8")
        result["raw_run_file"] = str(raw_path.relative_to(Path.cwd())) if raw_path.is_relative_to(Path.cwd()) else str(raw_path)
    else:
        result["raw_run_file"] = "warmup_discarded"
    return result


def summarise_merkle(n: int, reps: int, raw_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    _ = run_merkle_once(n, 0, raw_dir, warmup=True)
    rows = [run_merkle_once(n, rep + 1, raw_dir, warmup=False) for rep in range(reps)]
    summary = {
        "backend": "A2_MERKLE",
        "status": "executed" if all(r["status"] == "executed" for r in rows) else "failed",
        "object_count": n,
        "repetitions_executed": reps,
        "warmup_discarded": 1,
        "append_p50_ms": percentile([r["append_p50_ms"] for r in rows], 0.50),
        "append_p95_ms": percentile([r["append_p95_ms"] for r in rows], 0.95),
        "verify_p50_ms": percentile([r["verify_p50_ms"] for r in rows], 0.50),
        "verify_p95_ms": percentile([r["verify_p95_ms"] for r in rows], 0.95),
        "storage_bytes_median": median_int([int(r["storage_bytes"]) for r in rows]),
        "receipt_size_bytes_median": median_int([int(r["receipt_size_bytes_median"]) for r in rows]),
        "proof_size_bytes_median": median_int([int(r["proof_size_bytes_median"]) for r in rows]),
        "verification_samples_per_repetition": rows[0]["verification_samples"] if rows else 0,
        "tamper_detection_status": "see tamper_detection_results.csv",
        "raw_run_files": ";".join(str(r["raw_run_file"]) for r in rows),
        "interpretation": "local reference-implementation measurement; not production performance",
    }
    return rows, summary


def postgres_status_row() -> dict[str, Any]:
    return {
        "backend": "A1_POSTGRES",
        "status": "unavailable_current_runtime",
        "object_count": "not_executed",
        "repetitions_executed": 0,
        "warmup_discarded": 0,
        "append_p50_ms": "not_measured",
        "append_p95_ms": "not_measured",
        "verify_p50_ms": "not_measured",
        "verify_p95_ms": "not_measured",
        "storage_bytes_median": "not_measured",
        "receipt_size_bytes_median": "not_applicable",
        "proof_size_bytes_median": "not_applicable",
        "verification_samples_per_repetition": 0,
        "tamper_detection_status": "not_executed",
        "raw_run_files": "benchmark_outputs/probes/postgres_probe.json",
        "interpretation": "PostgreSQL schema and adapter present; Docker/psql/local DSN unavailable in current runtime",
    }


def a3_status_row() -> dict[str, Any]:
    return {
        "backend": "A3_TRANSPARENCY_LEDGER_LIKE",
        "status": "adapter_only_not_executed",
        "object_count": "not_executed",
        "repetitions_executed": 0,
        "warmup_discarded": 0,
        "append_p50_ms": "not_measured",
        "append_p95_ms": "not_measured",
        "verify_p50_ms": "not_measured",
        "verify_p95_ms": "not_measured",
        "storage_bytes_median": "not_measured",
        "receipt_size_bytes_median": "not_measured",
        "proof_size_bytes_median": "not_measured",
        "verification_samples_per_repetition": 0,
        "tamper_detection_status": "not_executed",
        "raw_run_files": "benchmark_outputs/probes/a3_probe.json",
        "interpretation": "Rekor/Trillian/Fabric service execution not available; only synthetic hash-commitment adapter present",
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "backend", "status", "object_count", "repetitions_executed", "warmup_discarded",
        "append_p50_ms", "append_p95_ms", "verify_p50_ms", "verify_p95_ms",
        "storage_bytes_median", "receipt_size_bytes_median", "proof_size_bytes_median",
        "verification_samples_per_repetition", "tamper_detection_status", "raw_run_files", "interpretation"
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["merkle", "postgres", "all"], default="all")
    parser.add_argument("--objects", nargs="+", type=int, default=[1000, 10000])
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--out", default="benchmark_outputs/backend_benchmark_summary.csv")
    parser.add_argument("--raw-dir", default="benchmark_outputs/raw_runs")
    parser.add_argument("--dsn-env", default="TEA_POSTGRES_DSN")
    args = parser.parse_args()
    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, Any]] = []
    raw_summaries: list[dict[str, Any]] = []

    if args.backend in {"all", "merkle"}:
        for n in args.objects:
            rows, summary = summarise_merkle(n, args.repetitions, raw_dir)
            raw_summaries.extend(rows)
            summary_rows.append(summary)

    if args.backend in {"all", "postgres"}:
        # Full PostgreSQL execution is intentionally not silent. It requires an explicit DSN.
        dsn = os.environ.get(args.dsn_env, "")
        if args.backend == "postgres" and not dsn:
            raise SystemExit(f"{args.dsn_env} not set; PostgreSQL execution not attempted")
        if args.backend == "all" and not dsn:
            summary_rows.append(postgres_status_row())
        elif dsn:
            raise SystemExit("PostgreSQL execution path is available only through scripts/probe_postgres.py plus a disposable DSN in this stage kit")

    if args.backend == "all":
        summary_rows.append(a3_status_row())

    write_csv(Path(args.out), summary_rows)
    raw_summary_path = raw_dir / "raw_run_index.json"
    raw_summary_path.write_text(json.dumps(raw_summaries, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
