#!/usr/bin/env python3
"""Recompute descriptive workload summaries from retained raw timing rows."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results_local" / "quick"


def nearest_rank(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[max(1, math.ceil(probability * len(ordered))) - 1]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = (args.output_dir or input_dir).resolve()
    timing_path = input_dir / "raw_runs" / "timing_samples.csv"
    metadata_path = input_dir / "run_metadata.json"
    if not timing_path.is_file() or not metadata_path.is_file():
        raise SystemExit(f"workload raw rows or run metadata missing under {input_dir}")

    with timing_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["descriptor_id"], []).append(row)

    summaries: list[dict[str, Any]] = []
    sizes: list[dict[str, Any]] = []
    for descriptor_id in sorted(grouped, key=lambda value: int(value[1:])):
        group = grouped[descriptor_id]
        appends = [float(row["elapsed_ms"]) for row in group if row["operation"] == "append"]
        verifies = [float(row["elapsed_ms"]) for row in group if row["operation"] == "verify"]
        verify_rows = [row for row in group if row["operation"] == "verify"]
        mutations = [row for row in group if row["operation"] == "deep-proof-mutation"]
        tree_size = int(group[0]["tree_size"])
        repetitions = len({row["repetition"] for row in group if row["operation"] == "append"})
        receipt_sizes = [int(row["receipt_bytes"]) for row in verify_rows]
        proof_sizes = [int(row["proof_bytes"]) for row in verify_rows]
        summaries.append({
            "run_id": metadata["run_id"],
            "descriptor_id": descriptor_id,
            "tree_size": tree_size,
            "repetitions": repetitions,
            "event_count": len(appends),
            "append_p50_ms": f"{statistics.median(appends):.9f}",
            "append_p95_ms": f"{nearest_rank(appends, 0.95):.9f}",
            "verify_p50_ms": f"{statistics.median(verifies):.9f}",
            "verify_p95_ms": f"{nearest_rank(verifies, 0.95):.9f}",
            "receipt_bytes_median": int(statistics.median(receipt_sizes)),
            "proof_bytes_median": int(statistics.median(proof_sizes)),
            "successful_receipt_checks": sum(row["accepted"] == "true" for row in verify_rows),
            "ordinary_verification_failures": sum(row["accepted"] != "true" for row in verify_rows),
            "validation_failures": 0,
            "mutation_cases": len(mutations),
            "mutation_rejections": sum(row["accepted"] == "false" and row["error_code"] == "TE-E-PROOF-PATH" for row in mutations),
            "measurement_class": "single-host descriptive local reference",
        })
        sizes.append({
            "run_id": metadata["run_id"],
            "descriptor_id": descriptor_id,
            "tree_size": tree_size,
            "expected_authentication_path_depth": int(math.log2(tree_size)) if tree_size > 0 else 0,
            "receipt_bytes_min": min(receipt_sizes),
            "receipt_bytes_median": int(statistics.median(receipt_sizes)),
            "receipt_bytes_max": max(receipt_sizes),
            "proof_bytes_min": min(proof_sizes),
            "proof_bytes_median": int(statistics.median(proof_sizes)),
            "proof_bytes_max": max(proof_sizes),
        })

    write_csv(output_dir / "workload_passage_summary_recomputed.csv", summaries)
    write_csv(output_dir / "receipt_size_summary_recomputed.csv", sizes)

    original = list(csv.DictReader((input_dir / "workload_passage_summary.csv").open(newline="", encoding="utf-8")))
    original_sizes = list(csv.DictReader((input_dir / "receipt_size_summary.csv").open(newline="", encoding="utf-8")))
    passed = original == [{k: str(v) for k, v in row.items()} for row in summaries] and original_sizes == [
        {k: str(v) for k, v in row.items()} for row in sizes
    ]
    print(json.dumps({"input_dir": str(input_dir), "rows": len(rows), "summary_match": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
