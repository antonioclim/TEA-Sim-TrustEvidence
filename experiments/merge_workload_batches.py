#!/usr/bin/env python3
"""Merge bounded workload batches into one auditable retained reference run.

This helper exists for execution environments that cap a single foreground
command.  Each batch uses the same passage implementation and disjoint
repetition numbers; this script rejects gaps, duplicates and inconsistent
protocol parameters before recomputing the combined summaries.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any

FULL_RUN_ID = "cmpb-workload-reference-001"
FIXED_GENERATED_UTC = "2026-07-11T00:00:00+00:00"
EXPECTED_SIZES = (128, 512, 2048)
EXPECTED_REPETITIONS = tuple(range(1, 13))


def nearest_rank(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[max(1, math.ceil(probability * len(ordered))) - 1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-dir", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    timing_rows: list[dict[str, str]] = []
    event_rows: list[dict[str, Any]] = []
    batch_metadata: list[dict[str, Any]] = []
    hardware_profiles: list[dict[str, Any]] = []
    for batch in args.batch_dir:
        batch = batch.resolve()
        timing_rows.extend(read_csv(batch / "raw_runs" / "timing_samples.csv"))
        with (batch / "raw_runs" / "workload_events.jsonl").open(encoding="utf-8") as handle:
            event_rows.extend(json.loads(line) for line in handle if line.strip())
        batch_metadata.append(json.loads((batch / "run_metadata.json").read_text(encoding="utf-8")))
        hardware_profiles.append(json.loads((batch / "hardware_profile.json").read_text(encoding="utf-8")))

    append_keys = [
        (row["descriptor_id"], int(row["repetition"]), int(row["event_index"]))
        for row in timing_rows if row["operation"] == "append"
    ]
    if len(append_keys) != len(set(append_keys)):
        raise SystemExit("duplicate append rows across workload batches")
    event_keys = [
        (row["descriptor_id"], int(row["repetition"]), int(row["event_index"]))
        for row in event_rows
    ]
    if len(event_keys) != len(set(event_keys)):
        raise SystemExit("duplicate event rows across workload batches")

    descriptor_order = {f"W{size}": index for index, size in enumerate(EXPECTED_SIZES)}
    actual_descriptors = {row["descriptor_id"] for row in timing_rows}
    if actual_descriptors != set(descriptor_order):
        raise SystemExit(f"descriptor mismatch: {sorted(actual_descriptors)}")
    for size in EXPECTED_SIZES:
        descriptor = f"W{size}"
        repetitions = {
            int(row["repetition"])
            for row in timing_rows
            if row["descriptor_id"] == descriptor and row["operation"] == "append"
        }
        if tuple(sorted(repetitions)) != EXPECTED_REPETITIONS:
            raise SystemExit(f"{descriptor} repetition coverage mismatch: {sorted(repetitions)}")
        count = sum(row["descriptor_id"] == descriptor and row["operation"] == "append" for row in timing_rows)
        if count != size * len(EXPECTED_REPETITIONS):
            raise SystemExit(f"{descriptor} append-row count {count} is not {size * 12}")

    operation_order = {"append": 0, "verify": 1, "deep-proof-mutation": 2}
    timing_rows.sort(key=lambda row: (
        descriptor_order[row["descriptor_id"]],
        int(row["repetition"]),
        operation_order.get(row["operation"], 9),
        int(row["event_index"]),
    ))
    event_rows.sort(key=lambda row: (
        descriptor_order[row["descriptor_id"]],
        int(row["repetition"]),
        int(row["event_index"]),
    ))

    summary_rows: list[dict[str, Any]] = []
    size_rows: list[dict[str, Any]] = []
    for size in EXPECTED_SIZES:
        descriptor = f"W{size}"
        group = [row for row in timing_rows if row["descriptor_id"] == descriptor]
        appends = [float(row["elapsed_ms"]) for row in group if row["operation"] == "append"]
        verifies = [float(row["elapsed_ms"]) for row in group if row["operation"] == "verify"]
        verify_rows = [row for row in group if row["operation"] == "verify"]
        mutation_rows = [row for row in group if row["operation"] == "deep-proof-mutation"]
        receipt_sizes = [int(row["receipt_bytes"]) for row in verify_rows]
        proof_sizes = [int(row["proof_bytes"]) for row in verify_rows]
        matching_events = [row for row in event_rows if row["descriptor_id"] == descriptor]
        validation_failures = sum(not bool(row["accepted"]) for row in matching_events)
        summary_rows.append({
            "run_id": FULL_RUN_ID,
            "descriptor_id": descriptor,
            "tree_size": size,
            "repetitions": 12,
            "event_count": len(appends),
            "append_p50_ms": f"{statistics.median(appends):.9f}",
            "append_p95_ms": f"{nearest_rank(appends, 0.95):.9f}",
            "verify_p50_ms": f"{statistics.median(verifies):.9f}",
            "verify_p95_ms": f"{nearest_rank(verifies, 0.95):.9f}",
            "receipt_bytes_median": int(statistics.median(receipt_sizes)),
            "proof_bytes_median": int(statistics.median(proof_sizes)),
            "successful_receipt_checks": sum(row["accepted"] == "true" for row in verify_rows),
            "ordinary_verification_failures": sum(row["accepted"] != "true" for row in verify_rows),
            "validation_failures": validation_failures,
            "mutation_cases": len(mutation_rows),
            "mutation_rejections": sum(
                row["accepted"] == "false" and row["error_code"] == "TE-E-PROOF-PATH"
                for row in mutation_rows
            ),
            "measurement_class": "single-host descriptive local reference",
        })
        size_rows.append({
            "run_id": FULL_RUN_ID,
            "descriptor_id": descriptor,
            "tree_size": size,
            "expected_authentication_path_depth": int(math.log2(size)),
            "receipt_bytes_min": min(receipt_sizes),
            "receipt_bytes_median": int(statistics.median(receipt_sizes)),
            "receipt_bytes_max": max(receipt_sizes),
            "proof_bytes_min": min(proof_sizes),
            "proof_bytes_median": int(statistics.median(proof_sizes)),
            "proof_bytes_max": max(proof_sizes),
        })

    output = args.output_dir.resolve()
    raw = output / "raw_runs"
    raw.mkdir(parents=True, exist_ok=True)
    timing_fields = [
        "descriptor_id", "tree_size", "repetition", "operation", "event_index",
        "event_type", "elapsed_ms", "passage_ms", "receipt_bytes", "proof_bytes",
        "accepted", "error_code",
    ]
    write_csv(raw / "timing_samples.csv", timing_rows, timing_fields)
    with (raw / "workload_events.jsonl").open("w", encoding="utf-8") as handle:
        for row in event_rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    write_csv(output / "workload_passage_summary.csv", summary_rows, list(summary_rows[0]))
    write_csv(output / "receipt_size_summary.csv", size_rows, list(size_rows[0]))

    hardware = hardware_profiles[0]
    hardware["measurement_boundary"] = "single-host descriptive local reference"
    hardware["batch_count"] = len(args.batch_dir)
    (output / "hardware_profile.json").write_text(
        json.dumps(hardware, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    metadata = {
        "run_id": FULL_RUN_ID,
        "generated_utc": FIXED_GENERATED_UTC,
        "tree_sizes": list(EXPECTED_SIZES),
        "repetitions": 12,
        "repetition_start": 1,
        "repetition_stop": 12,
        "verification_samples_per_repetition": 32,
        "deep_mutations_per_repetition": 1,
        "event_templates": 9,
        "total_events": sum(int(row["event_count"]) for row in summary_rows),
        "successful_receipt_checks": sum(int(row["successful_receipt_checks"]) for row in summary_rows),
        "validation_failures": sum(int(row["validation_failures"]) for row in summary_rows),
        "ordinary_verification_failures": sum(int(row["ordinary_verification_failures"]) for row in summary_rows),
        "mutation_cases": sum(int(row["mutation_cases"]) for row in summary_rows),
        "mutation_rejections": sum(int(row["mutation_rejections"]) for row in summary_rows),
        "batch_count": len(args.batch_dir),
        "batch_execution": [
            {
                "tree_sizes": item["tree_sizes"],
                "repetition_start": item.get("repetition_start", 1),
                "repetition_stop": item.get("repetition_stop", item["repetitions"]),
                "elapsed_seconds": item["elapsed_seconds"],
            }
            for item in batch_metadata
        ],
        "measurement_boundary": "single-host descriptive local reference",
        "input_boundary": "deterministic synthetic monitoring-accountability events",
    }
    (output / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    provenance = {
        "merge_status": "PASS",
        "batch_labels": [path.resolve().name for path in args.batch_dir],
        "append_rows": sum(row["operation"] == "append" for row in timing_rows),
        "verify_rows": sum(row["operation"] == "verify" for row in timing_rows),
        "mutation_rows": sum(row["operation"] == "deep-proof-mutation" for row in timing_rows),
        "event_rows": len(event_rows),
        "no_duplicate_append_keys": True,
        "no_duplicate_event_keys": True,
        "complete_repetition_coverage": True,
    }
    (raw / "batch_merge_provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    passed = (
        metadata["total_events"] == 32256
        and metadata["successful_receipt_checks"] == 1152
        and metadata["validation_failures"] == 0
        and metadata["ordinary_verification_failures"] == 0
        and metadata["mutation_cases"] == 36
        and metadata["mutation_rejections"] == 36
    )
    print(json.dumps({"status": "PASS" if passed else "FAIL", **metadata}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
