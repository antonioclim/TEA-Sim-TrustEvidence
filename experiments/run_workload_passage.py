#!/usr/bin/env python3
"""Run the bounded synthetic personal-monitoring passage.

The full reference protocol uses 12 repetitions at 128, 512 and 2,048 leaves,
32 sampled receipt checks per repetition and one re-signed proof mutation per
repetition.  Timings are single-host descriptive measurements.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
import statistics
import sys
import time
from copy import deepcopy
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

from trustevidence.backends.a2_merkle import LocalA2MerkleLog, attach_receipt, verify_envelope_receipt
from trustevidence.canonical import canonicalise_te
from trustevidence.crypto import sign_receipt
from trustevidence.envelope import build_signed_envelope
from trustevidence.harness.workload import WorkloadDescriptor, iter_synthetic_events, load_event_templates, sample_indices
from trustevidence.hashing import proof_digest_hex
from trustevidence.testing import (
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_EMITTER_KEY_ID,
    FIXTURE_LOG_ID,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)
from trustevidence.validators import validate_envelope, validate_monitoring_event

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "data_examples" / "personal_monitoring"
DEFAULT_OUTPUT = ROOT / "results_local" / "full_workload"
FULL_RUN_ID = "cmpb-workload-reference-001"
QUICK_RUN_ID = "cmpb-workload-quick-001"


def nearest_rank(values: list[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(probability * len(ordered)))
    return ordered[rank - 1]


def flip_hex(value: str) -> str:
    raw = bytearray.fromhex(value)
    raw[0] ^= 1
    return raw.hex()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def hardware_profile() -> dict[str, Any]:
    memory_kib = None
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                memory_kib = int(line.split()[1])
                break
    except OSError:
        pass
    return {
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or "not-reported",
        "logical_cpu_count": os.cpu_count(),
        "memory_total_kib": memory_kib,
        "python_version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "software": {
            "teasim-trustevidence": version("teasim-trustevidence"),
            "cryptography": version("cryptography"),
            "jsonschema": version("jsonschema"),
            "rfc8785": version("rfc8785"),
        },
    }


def verify(envelope: dict[str, Any]):
    return verify_envelope_receipt(
        envelope,
        emitter_keys={FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()},
        receipt_keys={FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()},
        expected_backend_id=FIXTURE_BACKEND_ID,
        expected_log_id=FIXTURE_LOG_ID,
    )


def run_descriptor(
    descriptor: WorkloadDescriptor,
    *,
    repetition_start: int,
    templates: dict[str, dict],
    timing_rows: list[dict[str, Any]],
    event_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    validation_failures = 0
    ordinary_verification_failures = 0
    successful_receipt_checks = 0
    mutation_rejections = 0
    mutation_cases = 0
    append_times: list[float] = []
    verify_times: list[float] = []
    receipt_sizes: list[int] = []
    proof_sizes: list[int] = []

    repetition_stop = repetition_start + descriptor.repetitions
    for repetition in range(repetition_start, repetition_stop):
        log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
        selected = set(sample_indices(descriptor.tree_size, descriptor.verification_samples))
        selected_envelopes: dict[int, dict[str, Any]] = {}

        for index, template_name, event, emitted_at in iter_synthetic_events(
            templates,
            descriptor_id=descriptor.descriptor_id,
            repetition=repetition,
            tree_size=descriptor.tree_size,
        ):
            event_start = time.perf_counter_ns()
            input_result = validate_monitoring_event(event)
            if not input_result.accepted:
                validation_failures += 1
                event_rows.append({
                    "descriptor_id": descriptor.descriptor_id,
                    "repetition": repetition,
                    "event_index": index,
                    "event_id": event.get("source_event_id", ""),
                    "event_type": event.get("event_type", ""),
                    "template": template_name,
                    "accepted": False,
                    "error_code": input_result.primary_code,
                    "core_digest": "",
                })
                continue

            envelope, digest = build_signed_envelope(
                event,
                emitted_at=emitted_at,
                private_key=fixture_emitter_private_key(),
            )
            envelope_result = validate_envelope(envelope)
            if not envelope_result.accepted:
                validation_failures += 1
                event_rows.append({
                    "descriptor_id": descriptor.descriptor_id,
                    "repetition": repetition,
                    "event_index": index,
                    "event_id": event["source_event_id"],
                    "event_type": event["event_type"],
                    "template": template_name,
                    "accepted": False,
                    "error_code": envelope_result.primary_code,
                    "core_digest": digest,
                })
                continue

            append_start = time.perf_counter_ns()
            appended_index = log.append_core_digest(digest)
            append_ms = (time.perf_counter_ns() - append_start) / 1_000_000
            passage_ms = (time.perf_counter_ns() - event_start) / 1_000_000
            append_times.append(append_ms)
            timing_rows.append({
                "descriptor_id": descriptor.descriptor_id,
                "tree_size": descriptor.tree_size,
                "repetition": repetition,
                "operation": "append",
                "event_index": index,
                "event_type": event["event_type"],
                "elapsed_ms": f"{append_ms:.9f}",
                "passage_ms": f"{passage_ms:.9f}",
                "receipt_bytes": "",
                "proof_bytes": "",
                "accepted": "true",
                "error_code": "PASS",
            })
            event_rows.append({
                "descriptor_id": descriptor.descriptor_id,
                "repetition": repetition,
                "event_index": index,
                "event_id": event["source_event_id"],
                "event_type": event["event_type"],
                "template": template_name,
                "accepted": True,
                "error_code": "PASS",
                "core_digest": digest,
            })
            if appended_index != index:
                raise RuntimeError("append index diverged from deterministic event index")
            if index in selected:
                selected_envelopes[index] = envelope

        if log.tree_size != descriptor.tree_size:
            raise RuntimeError(
                f"{descriptor.descriptor_id} repetition {repetition}: "
                f"tree_size={log.tree_size}, expected {descriptor.tree_size}"
            )

        receipts: dict[int, dict[str, Any]] = {}
        for index in sorted(selected):
            receipt = log.issue_receipt(
                index,
                issued_at="2026-07-03T04:00:00.000Z",
                private_key=fixture_backend_private_key(),
                signer_key_id=FIXTURE_BACKEND_KEY_ID,
            )
            receipts[index] = receipt
            complete = attach_receipt(selected_envelopes[index], receipt)
            verify_start = time.perf_counter_ns()
            result = verify(complete)
            verify_ms = (time.perf_counter_ns() - verify_start) / 1_000_000
            verify_times.append(verify_ms)
            receipt_bytes = len(canonicalise_te(receipt))
            proof_bytes = len(canonicalise_te(receipt["inclusion_proof"]))
            receipt_sizes.append(receipt_bytes)
            proof_sizes.append(proof_bytes)
            if result.accepted:
                successful_receipt_checks += 1
            else:
                ordinary_verification_failures += 1
            timing_rows.append({
                "descriptor_id": descriptor.descriptor_id,
                "tree_size": descriptor.tree_size,
                "repetition": repetition,
                "operation": "verify",
                "event_index": index,
                "event_type": selected_envelopes[index]["evidence_core"]["event_type"],
                "elapsed_ms": f"{verify_ms:.9f}",
                "passage_ms": "",
                "receipt_bytes": receipt_bytes,
                "proof_bytes": proof_bytes,
                "accepted": str(result.accepted).lower(),
                "error_code": result.primary_code,
            })

        # One deep, re-signed proof mutation per repetition.  Re-signing avoids
        # treating a stale signature as the only rejection layer.
        for mutation_number in range(descriptor.deep_mutations):
            mutation_cases += 1
            candidate_index = sorted(selected)[(repetition + mutation_number) % len(selected)]
            original = receipts[candidate_index]
            if not original["inclusion_proof"]["siblings"]:
                candidate_index = sorted(selected)[-1]
                original = receipts[candidate_index]
            mutated = deepcopy(original)
            mutated["inclusion_proof"]["siblings"][0] = flip_hex(
                mutated["inclusion_proof"]["siblings"][0]
            )
            mutated["inclusion_proof_digest"] = proof_digest_hex(mutated["inclusion_proof"])
            mutated.pop("receipt_signature", None)
            signature, _ = sign_receipt(
                mutated,
                private_key=fixture_backend_private_key(),
                key_id=FIXTURE_BACKEND_KEY_ID,
            )
            mutated["receipt_signature"] = signature
            complete = attach_receipt(selected_envelopes[candidate_index], mutated)
            result = verify(complete)
            rejected = not result.accepted and "TE-E-PROOF-PATH" in result.codes
            mutation_rejections += int(rejected)
            timing_rows.append({
                "descriptor_id": descriptor.descriptor_id,
                "tree_size": descriptor.tree_size,
                "repetition": repetition,
                "operation": "deep-proof-mutation",
                "event_index": candidate_index,
                "event_type": selected_envelopes[candidate_index]["evidence_core"]["event_type"],
                "elapsed_ms": "",
                "passage_ms": "",
                "receipt_bytes": len(canonicalise_te(mutated)),
                "proof_bytes": len(canonicalise_te(mutated["inclusion_proof"])),
                "accepted": str(result.accepted).lower(),
                "error_code": result.primary_code,
            })

        print(
            f"progress descriptor={descriptor.descriptor_id} "
            f"repetition={repetition}/{repetition_stop - 1}",
            file=sys.stderr,
            flush=True,
        )

    return {
        "descriptor_id": descriptor.descriptor_id,
        "tree_size": descriptor.tree_size,
        "repetitions": descriptor.repetitions,
        "repetition_start": repetition_start,
        "repetition_stop": repetition_stop - 1,
        "event_count": descriptor.tree_size * descriptor.repetitions,
        "append_p50_ms": statistics.median(append_times),
        "append_p95_ms": nearest_rank(append_times, 0.95),
        "verify_p50_ms": statistics.median(verify_times),
        "verify_p95_ms": nearest_rank(verify_times, 0.95),
        "receipt_bytes_median": int(statistics.median(receipt_sizes)),
        "proof_bytes_median": int(statistics.median(proof_sizes)),
        "receipt_bytes_min": min(receipt_sizes),
        "receipt_bytes_max": max(receipt_sizes),
        "proof_bytes_min": min(proof_sizes),
        "proof_bytes_max": max(proof_sizes),
        "successful_receipt_checks": successful_receipt_checks,
        "ordinary_verification_failures": ordinary_verification_failures,
        "validation_failures": validation_failures,
        "mutation_cases": mutation_cases,
        "mutation_rejections": mutation_rejections,
        "expected_authentication_path_depth": int(math.log2(descriptor.tree_size)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tree-sizes", type=int, nargs="+", default=[128, 512, 2048])
    parser.add_argument("--repetitions", type=int, default=12)
    parser.add_argument("--verification-samples", type=int, default=32)
    parser.add_argument("--repetition-start", type=int, default=1)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    if args.quick:
        args.tree_sizes = [16, 32]
        args.repetitions = 1
        args.verification_samples = 8
        args.repetition_start = 1
        run_id = QUICK_RUN_ID
    else:
        run_id = FULL_RUN_ID
    if any(size <= 1 for size in args.tree_sizes):
        raise SystemExit("tree sizes must exceed one")
    if args.repetitions <= 0 or args.verification_samples <= 0 or args.repetition_start <= 0:
        raise SystemExit("repetitions, repetition-start and verification samples must be positive")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    raw = output / "raw_runs"
    raw.mkdir(parents=True, exist_ok=True)

    templates = load_event_templates(EXAMPLES)
    timing_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    start = time.perf_counter()
    for size in args.tree_sizes:
        descriptor = WorkloadDescriptor(
            descriptor_id=f"W{size}",
            tree_size=size,
            repetitions=args.repetitions,
            verification_samples=args.verification_samples,
        )
        summaries.append(
            run_descriptor(
                descriptor,
                repetition_start=args.repetition_start,
                templates=templates,
                timing_rows=timing_rows,
                event_rows=event_rows,
            )
        )
    elapsed = time.perf_counter() - start

    timing_fields = [
        "descriptor_id", "tree_size", "repetition", "operation", "event_index",
        "event_type", "elapsed_ms", "passage_ms", "receipt_bytes", "proof_bytes",
        "accepted", "error_code",
    ]
    write_csv(raw / "timing_samples.csv", timing_rows, timing_fields)
    with (raw / "workload_events.jsonl").open("w", encoding="utf-8") as handle:
        for row in event_rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

    summary_rows: list[dict[str, Any]] = []
    size_rows: list[dict[str, Any]] = []
    for item in summaries:
        summary_rows.append({
            "run_id": run_id,
            "descriptor_id": item["descriptor_id"],
            "tree_size": item["tree_size"],
            "repetitions": item["repetitions"],
            "event_count": item["event_count"],
            "append_p50_ms": f"{item['append_p50_ms']:.9f}",
            "append_p95_ms": f"{item['append_p95_ms']:.9f}",
            "verify_p50_ms": f"{item['verify_p50_ms']:.9f}",
            "verify_p95_ms": f"{item['verify_p95_ms']:.9f}",
            "receipt_bytes_median": item["receipt_bytes_median"],
            "proof_bytes_median": item["proof_bytes_median"],
            "successful_receipt_checks": item["successful_receipt_checks"],
            "ordinary_verification_failures": item["ordinary_verification_failures"],
            "validation_failures": item["validation_failures"],
            "mutation_cases": item["mutation_cases"],
            "mutation_rejections": item["mutation_rejections"],
            "measurement_class": "single-host descriptive local reference",
        })
        size_rows.append({
            "run_id": run_id,
            "descriptor_id": item["descriptor_id"],
            "tree_size": item["tree_size"],
            "expected_authentication_path_depth": item["expected_authentication_path_depth"],
            "receipt_bytes_min": item["receipt_bytes_min"],
            "receipt_bytes_median": item["receipt_bytes_median"],
            "receipt_bytes_max": item["receipt_bytes_max"],
            "proof_bytes_min": item["proof_bytes_min"],
            "proof_bytes_median": item["proof_bytes_median"],
            "proof_bytes_max": item["proof_bytes_max"],
        })

    write_csv(output / "workload_passage_summary.csv", summary_rows, list(summary_rows[0]))
    write_csv(output / "receipt_size_summary.csv", size_rows, list(size_rows[0]))
    profile = hardware_profile()
    dump_json(output / "hardware_profile.json", profile)
    metadata = {
        "run_id": run_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "tree_sizes": args.tree_sizes,
        "repetitions": args.repetitions,
        "repetition_start": args.repetition_start,
        "repetition_stop": args.repetition_start + args.repetitions - 1,
        "verification_samples_per_repetition": args.verification_samples,
        "deep_mutations_per_repetition": 1,
        "event_templates": len(templates),
        "total_events": sum(item["event_count"] for item in summaries),
        "successful_receipt_checks": sum(item["successful_receipt_checks"] for item in summaries),
        "validation_failures": sum(item["validation_failures"] for item in summaries),
        "ordinary_verification_failures": sum(item["ordinary_verification_failures"] for item in summaries),
        "mutation_cases": sum(item["mutation_cases"] for item in summaries),
        "mutation_rejections": sum(item["mutation_rejections"] for item in summaries),
        "elapsed_seconds": round(elapsed, 6),
        "measurement_boundary": "single-host descriptive local reference",
        "input_boundary": "deterministic synthetic monitoring-accountability events",
    }
    dump_json(output / "run_metadata.json", metadata)

    expected_receipts = len(args.tree_sizes) * args.repetitions * min(args.verification_samples, min(args.tree_sizes))
    passed = (
        metadata["validation_failures"] == 0
        and metadata["ordinary_verification_failures"] == 0
        and metadata["successful_receipt_checks"] == expected_receipts
        and metadata["mutation_rejections"] == metadata["mutation_cases"]
    )
    print(json.dumps({"run_id": run_id, "passed": passed, **metadata}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
