#!/usr/bin/env python3
"""Execute the Route C B0--B2 paired local incremental-overhead experiment.

The experiment is deliberately process-level and paired.  Every baseline run is
executed in a fresh Python process after an identical full-path warm-up.  Within
a paired block, B0, B1 and B2 receive the same workload, seed, source fixture,
operation count and deterministic timestamps; only the processing boundary
changes.

The retained measurements describe this Python reference pipeline on the
reported host.  They are not production-EHR latency, hospital service-level,
network-capacity, organisational-cost or scalability measurements.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import tempfile
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from trustevidence.backends.a2_merkle import (
    LocalA2MerkleLog,
    RetainedCheckpoint,
    attach_receipt,
    verify_envelope_receipt,
)
from trustevidence.canonical import canonicalise_te, normalise_timestamp_ms, strict_json_loads
from trustevidence.crypto import b64url_encode, commit_payload
from trustevidence.hashing import (
    core_digest_bytes,
    core_signature_message,
    leaf_input_bytes,
)
from trustevidence.hie import (
    HIE_COMMITMENT_CONTEXT,
    HIE_ENVELOPE_PROFILE,
    HIE_ENVELOPE_VERSION,
    HIE_REPRESENTATION_PROFILE,
    verify_hie_envelope_receipt,
)
from trustevidence.hie_state import RetainedHIEVerifier
from trustevidence.hie_validation import validate_hie_disclosure_event, validate_hie_envelope
from trustevidence.profiles import ENVELOPE_PROFILE, ENVELOPE_VERSION
from trustevidence.testing import (
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_EMITTER_KEY_ID,
    FIXTURE_LOG_ID,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)
from trustevidence.validators import validate_envelope, validate_monitoring_event

try:
    from experiments import run_hie_hero_case as hie_case
except ModuleNotFoundError:  # direct script execution places experiments/ on sys.path
    import run_hie_hero_case as hie_case

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results_expected" / "cmpb_reference" / "c5_hie_overhead"
W1_SOURCE = ROOT / "data_examples" / "hie_disclosure" / "source" / "source_clinical_bundle.json"
W2_SOURCE = ROOT / "data_examples" / "c5_overhead" / "wearable_monitoring_batch.json"
W2_EVENT_TEMPLATE = ROOT / "data_examples" / "personal_monitoring" / "aggregation_event.json"
FHIR_RESOURCES = ROOT / "standards" / "fhir_ig" / "input" / "resources"

RUN_ID = "route-c-hie-overhead-001"
SOFTWARE_STATUS = "working-branch-pre-v2.2.0"
BASELINES = ("B0", "B1", "B2")
ALL_WORKLOADS = ("W1-HIE-DISCLOSURE", "W2-WEARABLE-BATCH")
CONFIRMATORY_WORKLOADS = ("W1-HIE-DISCLOSURE",)
COMPARISONS = (
    ("B1-B0", "B1", "B0"),
    ("B2-B1", "B2", "B1"),
    ("B2-B0", "B2", "B0"),
)
STAGES = ("M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7")
PRIMARY_METRICS = (
    ("run_duration_ms", "ms"),
    ("m7_p50_ms", "ms"),
    ("m7_p95_ms", "ms"),
    ("m7_p99_ms", "ms"),
    ("total_application_bytes_median", "bytes"),
    ("storage_proxy_final_bytes", "bytes"),
)
DEFAULT_PILOT_BLOCKS = 5
DEFAULT_RETAINED_BLOCKS = 20
DEFAULT_OPERATIONS = 128
DEFAULT_WARMUP = 8
DEFAULT_BOOTSTRAP_RESAMPLES = 10_000
BASE_SEED = 2026072305
W2_COMMITMENT_CONTEXT = "wearable-batch-source-v1"
W2_NONCE_DOMAIN = "Route C C5 deterministic TEST-ONLY W2 nonce"
W1_NONCE_DOMAIN = "Route C C5 deterministic TEST-ONLY W1 nonce"

RUN_FIELDS = [
    "run_id",
    "software_status",
    "phase",
    "workload_id",
    "paired_block_id",
    "baseline",
    "baseline_order",
    "order_position",
    "seed",
    "warmup_count",
    "operation_count",
    "process_pid",
    "start_utc",
    "end_utc",
    "process_wall_ms",
    "run_duration_ms",
    "m7_sum_ms",
    "m7_p50_ms",
    "m7_p95_ms",
    "m7_p99_ms",
    "m0_p50_ms",
    "m1_p50_ms",
    "m2_p50_ms",
    "m3_p50_ms",
    "m4_p50_ms",
    "m5_p50_ms",
    "m6_p50_ms",
    "source_fhir_bytes_median",
    "audit_projection_bytes_median",
    "trust_evidence_envelope_bytes_median",
    "complete_portable_envelope_bytes_median",
    "signature_material_bytes_median",
    "receipt_bytes_median",
    "inclusion_proof_bytes_median",
    "total_application_bytes_median",
    "storage_proxy_final_bytes",
    "valid_cases",
    "validation_failures",
    "verification_failures",
    "expected_invalid_cases",
    "expected_invalid_rejections",
    "false_accepts",
    "false_rejects",
    "retry_count",
    "source_sha256",
    "source_digest_preserved",
    "payload_exclusion_findings",
    "passed",
]

PAIR_FIELDS = [
    "run_id",
    "workload_id",
    "paired_block_id",
    "seed",
    "baseline_order",
    "comparison",
    "run_duration_increment_ms",
    "m7_p50_increment_ms",
    "m7_p95_increment_ms",
    "m7_p99_increment_ms",
    "total_application_bytes_increment",
    "storage_proxy_bytes_increment",
]

AGGREGATE_FIELDS = [
    "run_id",
    "workload_id",
    "comparison",
    "metric",
    "unit",
    "n_pairs",
    "median_increment",
    "mean_increment",
    "ci95_low",
    "ci95_high",
    "minimum_increment",
    "maximum_increment",
    "estimator",
    "claim_boundary",
]


@dataclass(slots=True)
class WorkerContext:
    workload_id: str
    baseline: str
    phase: str
    block_id: str
    seed: int
    operation_count: int
    warmup_count: int
    audit_templates: list[dict[str, Any]] = field(default_factory=list)
    monitoring_template: dict[str, Any] | None = None
    log: LocalA2MerkleLog | None = None
    hie_state: RetainedHIEVerifier | None = None
    generic_checkpoint: RetainedCheckpoint | None = None
    storage_proxy_accumulator: int = 0
    last_complete_envelope: dict[str, Any] | None = None
    last_source_sha256: str = ""
    expected_source_sha256: str = ""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def decimal(value: float) -> str:
    return f"{value:.9f}"


def integer(value: int | bool) -> str:
    return str(int(value))


def boolean(value: bool) -> str:
    return str(bool(value)).lower()


def nearest_rank(values: Sequence[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(probability * len(ordered)))
    return ordered[rank - 1]


def percentile_ns(values: Sequence[int], probability: float) -> float:
    return nearest_rank([value / 1_000_000 for value in values], probability)


def median_int(values: Sequence[int]) -> int:
    return int(statistics.median(values)) if values else 0


def stable_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_commit() -> str:
    value = os.environ.get("GITHUB_SHA")
    if value:
        return value
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except OSError:
        pass
    return "not-available"


def package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def hardware_profile() -> dict[str, Any]:
    memory_kib: int | None = None
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
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor() or "not-reported",
        "logical_cpu_count": os.cpu_count(),
        "memory_total_kib": memory_kib,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "packages": {
            "teasim-trustevidence": package_version("teasim-trustevidence"),
            "cryptography": package_version("cryptography"),
            "jsonschema": package_version("jsonschema"),
            "rfc8785": package_version("rfc8785"),
        },
        "measurement_boundary": "single GitHub-hosted or local Python process; warmed local filesystem; no application network",
    }


def operation_timestamp(index: int, *, base: datetime) -> str:
    value = base + timedelta(seconds=index)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def deterministic_nonce(domain: str, *, seed: int, operation_index: int) -> bytes:
    return hashlib.sha256(f"{domain}:{seed}:{operation_index}".encode("utf-8")).digest()


def source_path(workload_id: str) -> Path:
    if workload_id == "W1-HIE-DISCLOSURE":
        return W1_SOURCE
    if workload_id == "W2-WEARABLE-BATCH":
        return W2_SOURCE
    raise ValueError(f"Unknown workload: {workload_id}")


def local_validate_source(workload_id: str, value: Any) -> None:
    if not isinstance(value, dict) or value.get("resourceType") != "Bundle":
        raise ValueError("source fixture must be a FHIR Bundle object")
    entries = value.get("entry")
    if not isinstance(entries, list) or not entries:
        raise ValueError("source Bundle must contain entries")
    resources = [item.get("resource") for item in entries if isinstance(item, dict)]
    resource_types = [item.get("resourceType") for item in resources if isinstance(item, dict)]
    if workload_id == "W1-HIE-DISCLOSURE":
        if resource_types.count("DiagnosticReport") != 1:
            raise ValueError("W1 requires one DiagnosticReport")
        if resource_types.count("Observation") != 3:
            raise ValueError("W1 requires three synthetic laboratory Observations")
        if "Patient" not in resource_types or "Organization" not in resource_types:
            raise ValueError("W1 source context is incomplete")
    else:
        if resource_types.count("Observation") != 1 or resource_types.count("Provenance") != 1:
            raise ValueError("W2 requires one batch-summary Observation and one Provenance")
        observation = next(
            item for item in resources if isinstance(item, dict) and item.get("resourceType") == "Observation"
        )
        components = observation.get("component", [])
        values = {
            item.get("code", {}).get("coding", [{}])[0].get("code"): item.get("valueInteger")
            for item in components
            if isinstance(item, dict)
        }
        if values.get("sample-count") != 288 or values.get("missingness-count") != 4:
            raise ValueError("W2 batch counts differ from the frozen workload")
        if "valueQuantity" in observation or "valueSampledData" in observation:
            raise ValueError("W2 fixture must not contain raw monitoring values")


def load_and_validate_source(workload_id: str) -> tuple[dict[str, Any], bytes, str]:
    raw = source_path(workload_id).read_text(encoding="utf-8")
    value = strict_json_loads(raw)
    local_validate_source(workload_id, value)
    canonical = canonicalise_te(value)
    return value, canonical, hashlib.sha256(canonical).hexdigest()


def load_w1_audit_templates() -> list[dict[str, Any]]:
    names = [
        "Patient-patient-hie-001.json",
        "Organization-hospital-a.json",
        "Organization-hospital-b.json",
        "Device-evidence-service-a.json",
        "Device-authorisation-service-a.json",
        "Practitioner-recipient-role-b.json",
        "PractitionerRole-authorised-reader-b.json",
        "Consent-consent-hie-001.json",
        "AuditEvent-authorisation-decision-hie-001.json",
        "AuditEvent-privacy-disclosure-source-hie-001.json",
        "Provenance-evidence-provenance-hie-001.json",
    ]
    return [json.loads((FHIR_RESOURCES / name).read_text(encoding="utf-8")) for name in names]


def build_w1_conventional_projection(
    templates: Sequence[dict[str, Any]], *, operation_token: str
) -> dict[str, Any]:
    bundle = {
        "resourceType": "Bundle",
        "id": f"conventional-audit-w1-{operation_token}",
        "identifier": {
            "system": "urn:te:c5:conventional-audit-bundle",
            "value": operation_token,
        },
        "type": "collection",
        "timestamp": "2026-07-14T09:30:01Z",
        "entry": [],
    }
    for template in templates:
        resource = deepcopy(template)
        bundle["entry"].append(
            {
                "fullUrl": f"https://example.org/fhir/{resource['resourceType']}/{resource['id']}",
                "resource": resource,
            }
        )
    return bundle


def build_w2_conventional_projection(
    source: dict[str, Any], *, operation_token: str
) -> dict[str, Any]:
    entries = source["entry"]
    resources = [item["resource"] for item in entries]
    observation = next(item for item in resources if item["resourceType"] == "Observation")
    provenance = next(item for item in resources if item["resourceType"] == "Provenance")
    patient = next(item for item in resources if item["resourceType"] == "Patient")
    device = next(item for item in resources if item["resourceType"] == "Device")
    audit = {
        "resourceType": "AuditEvent",
        "id": f"wearable-batch-audit-{operation_token}",
        "meta": {"security": deepcopy(source.get("meta", {}).get("security", []))},
        "type": {
            "system": "http://dicom.nema.org/resources/ontology/DCM",
            "code": "110100",
            "display": "Application Activity",
        },
        "subtype": [
            {
                "system": "urn:te:c5:audit-subtype",
                "code": "wearable-batch-aggregation",
            }
        ],
        "action": "E",
        "recorded": "2026-07-16T00:00:01Z",
        "outcome": "0",
        "agent": [
            {
                "who": {"reference": "Device/wearable-aggregation-service-c5"},
                "requestor": False,
            }
        ],
        "source": {
            "observer": {"reference": "Device/wearable-aggregation-service-c5"},
        },
        "entity": [
            {
                "what": {"reference": "Observation/wearable-batch-summary-c5-001"},
                "detail": [
                    {"type": "sample-count", "valueString": "288"},
                    {"type": "missingness-count", "valueString": "4"},
                    {"type": "operation-token", "valueString": operation_token},
                ],
            }
        ],
    }
    selected = [deepcopy(patient), deepcopy(device), deepcopy(observation), deepcopy(provenance), audit]
    bundle = {
        "resourceType": "Bundle",
        "id": f"conventional-audit-w2-{operation_token}",
        "identifier": {
            "system": "urn:te:c5:conventional-audit-bundle",
            "value": operation_token,
        },
        "type": "collection",
        "timestamp": "2026-07-16T00:00:01Z",
        "entry": [
            {
                "fullUrl": f"https://example.org/fhir/{item['resourceType']}/{item['id']}",
                "resource": item,
            }
            for item in selected
        ],
    }
    return bundle


def build_conventional_projection(
    context: WorkerContext, source: dict[str, Any], *, operation_token: str
) -> dict[str, Any]:
    if context.workload_id == "W1-HIE-DISCLOSURE":
        return build_w1_conventional_projection(context.audit_templates, operation_token=operation_token)
    return build_w2_conventional_projection(source, operation_token=operation_token)


def generic_core_from_event(event: dict[str, Any], *, emitted_at: str) -> dict[str, Any]:
    source = event["source_boundary"]
    facts = deepcopy(event["event_facts"])
    for key in ("effective_at", "activity_started_at", "activity_ended_at", "window_start", "window_end"):
        if key in facts:
            facts[key] = normalise_timestamp_ms(facts[key])
    core: dict[str, Any] = {
        "evidence_id": f"urn:te:evidence:c5:{hashlib.sha256(event['source_event_id'].encode()).hexdigest()[:32]}",
        "event_id": event["source_event_id"],
        "event_type": event["event_type"],
        "occurred_at": normalise_timestamp_ms(event["occurred_at"]),
        "emitted_at": normalise_timestamp_ms(emitted_at),
        "time_source": deepcopy(source["time_source"]),
        "emitter": {
            "emitter_id": source["source_id"],
            "role_code": source["source_role_code"],
            "key_id": source["key_id"],
        },
        "subject_context": deepcopy(event["subject_context"]),
        "objects": deepcopy(event["object_contexts"]),
        "purpose_code": event["purpose_code"],
        "outcome": deepcopy(event["outcome"]),
        "privacy_profile": deepcopy(event["privacy_profile"]),
        "event_facts": facts,
    }
    if source.get("organisation_ref_token"):
        core["emitter"]["organisation_ref_token"] = source["organisation_ref_token"]
    if event.get("actor_context"):
        core["actor"] = deepcopy(event["actor_context"])
    if event.get("policy_context"):
        policy = event["policy_context"]
        if policy.get("policy_binding"):
            core["policy_binding"] = deepcopy(policy["policy_binding"])
        if policy.get("consent_binding"):
            core["consent_binding"] = deepcopy(policy["consent_binding"])
    return core


def hie_core_from_event(event: dict[str, Any], *, emitted_at: str) -> dict[str, Any]:
    source = event["source_boundary"]
    return {
        "evidence_id": f"urn:te:evidence:c5:{hashlib.sha256(event['source_event_id'].encode()).hexdigest()[:32]}",
        "event_id": event["source_event_id"],
        "event_type": event["event_type"],
        "occurred_at": normalise_timestamp_ms(event["occurred_at"]),
        "emitted_at": normalise_timestamp_ms(emitted_at),
        "time_source": deepcopy(source["time_source"]),
        "emitter": {
            "emitter_id": source["source_id"],
            "role_code": source["source_role_code"],
            "organisation_ref_token": source["organisation_ref_token"],
            "key_id": source["key_id"],
        },
        "subject_context": deepcopy(event["subject_context"]),
        "objects": deepcopy(event["object_contexts"]),
        "purpose_code": event["purpose_code"],
        "outcome": deepcopy(event["outcome"]),
        "privacy_profile": deepcopy(event["privacy_profile"]),
        "event_facts": deepcopy(event["event_facts"]),
        "actor": deepcopy(event["actor_context"]),
        "policy_binding": deepcopy(event["policy_context"]["policy_binding"]),
        "consent_binding": deepcopy(event["policy_context"]["consent_binding"]),
    }


def sign_core(core: dict[str, Any], *, envelope_profile: str) -> tuple[dict[str, str], str]:
    digest = core_digest_bytes(core, envelope_profile=envelope_profile)
    message = core_signature_message(
        digest,
        algorithm="Ed25519",
        key_id=FIXTURE_EMITTER_KEY_ID,
    )
    signature = fixture_emitter_private_key().sign(message)
    return {
        "algorithm": "Ed25519",
        "key_id": FIXTURE_EMITTER_KEY_ID,
        "signature": b64url_encode(signature),
    }, digest.hex()


def build_w1_event(
    source_bytes: bytes, *, seed: int, operation_index: int, operation_token: str
) -> dict[str, Any]:
    nonce = deterministic_nonce(W1_NONCE_DOMAIN, seed=seed, operation_index=operation_index)
    commitment = commit_payload(
        source_bytes,
        nonce=nonce,
        representation_profile=HIE_REPRESENTATION_PROFILE,
        commitment_context=HIE_COMMITMENT_CONTEXT,
    )
    policy_digest = hashlib.sha256(hie_case.implementation.policy_bytes()).hexdigest()
    event = hie_case.implementation.build_event(commitment, policy_digest)
    event["source_event_id"] = f"urn:te:event:c5-w1-{operation_token}"
    validation = validate_hie_disclosure_event(event)
    if not validation.accepted:
        raise ValueError(f"W1 event rejected: {validation.codes}")
    return event


def build_w2_event(
    context: WorkerContext,
    source_bytes: bytes,
    *,
    seed: int,
    operation_index: int,
    operation_token: str,
) -> dict[str, Any]:
    if context.monitoring_template is None:
        raise RuntimeError("W2 monitoring template was not loaded")
    nonce = deterministic_nonce(W2_NONCE_DOMAIN, seed=seed, operation_index=operation_index)
    commitment = commit_payload(
        source_bytes,
        nonce=nonce,
        representation_profile=HIE_REPRESENTATION_PROFILE,
        commitment_context=W2_COMMITMENT_CONTEXT,
    )
    event = deepcopy(context.monitoring_template)
    event["source_event_id"] = f"urn:te:event:c5-w2-{operation_token}"
    event["object_contexts"][0]["payload_binding"] = {
        "commitment_profile": "sha256-nonce-v1",
        "representation_profile": HIE_REPRESENTATION_PROFILE,
        "commitment_context": W2_COMMITMENT_CONTEXT,
        "commitment": commitment,
    }
    validation = validate_monitoring_event(event)
    if not validation.accepted:
        raise ValueError(f"W2 event rejected: {validation.codes}")
    return event


def emitter_keys() -> dict[str, Any]:
    return {FIXTURE_EMITTER_KEY_ID: fixture_emitter_private_key().public_key()}


def receipt_keys() -> dict[str, Any]:
    return {FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()}


def payload_exclusion_findings(value: Any) -> int:
    forbidden_keys = {
        "valueQuantity",
        "valueSampledData",
        "valueStringClinical",
        "diagnosticImage",
        "raw_payload",
    }
    findings = 0
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden_keys:
                findings += 1
            findings += payload_exclusion_findings(child)
    elif isinstance(value, list):
        findings += sum(payload_exclusion_findings(item) for item in value)
    return findings


def setup_context(
    *,
    workload_id: str,
    baseline: str,
    phase: str,
    block_id: str,
    seed: int,
    operation_count: int,
    warmup_count: int,
) -> WorkerContext:
    context = WorkerContext(
        workload_id=workload_id,
        baseline=baseline,
        phase=phase,
        block_id=block_id,
        seed=seed,
        operation_count=operation_count,
        warmup_count=warmup_count,
    )
    if workload_id == "W1-HIE-DISCLOSURE":
        context.audit_templates = load_w1_audit_templates()
        context.hie_state = RetainedHIEVerifier(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID)
    else:
        context.monitoring_template = json.loads(W2_EVENT_TEMPLATE.read_text(encoding="utf-8"))
    context.log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    _, source_bytes, source_digest = load_and_validate_source(workload_id)
    context.expected_source_sha256 = source_digest
    context.last_source_sha256 = source_digest
    return context


def reset_timed_state(context: WorkerContext) -> None:
    context.log = LocalA2MerkleLog(backend_id=FIXTURE_BACKEND_ID, log_id=FIXTURE_LOG_ID)
    context.storage_proxy_accumulator = 0
    context.last_complete_envelope = None
    context.generic_checkpoint = None
    if context.workload_id == "W1-HIE-DISCLOSURE":
        context.hie_state = RetainedHIEVerifier(FIXTURE_BACKEND_ID, FIXTURE_LOG_ID)


def process_operation(
    context: WorkerContext,
    *,
    operation_index: int,
    measure: bool,
) -> dict[str, Any]:
    token = f"{context.phase[:1]}{context.block_id.lower()}-o{operation_index:03d}"
    stages = {stage: 0 for stage in STAGES}
    total_start = time.perf_counter_ns()

    start = time.perf_counter_ns()
    source, source_bytes, source_digest = load_and_validate_source(context.workload_id)
    stages["M0"] = time.perf_counter_ns() - start
    context.last_source_sha256 = source_digest

    source_size = len(source_bytes)
    audit_size = 0
    signed_envelope_size = 0
    complete_envelope_size = 0
    signature_size = 0
    receipt_size = 0
    proof_size = 0
    storage_proxy = 0
    accepted = True
    error_code = "PASS"
    projection: dict[str, Any] | None = None

    if context.baseline in {"B1", "B2"}:
        start = time.perf_counter_ns()
        projection = build_conventional_projection(context, source, operation_token=token)
        projection_bytes = canonicalise_te(projection)
        audit_size = len(projection_bytes)
        stages["M1"] = time.perf_counter_ns() - start

    if context.baseline == "B2":
        if context.log is None:
            raise RuntimeError("A2 log is unavailable")

        start = time.perf_counter_ns()
        if context.workload_id == "W1-HIE-DISCLOSURE":
            event = build_w1_event(
                source_bytes,
                seed=context.seed,
                operation_index=operation_index,
                operation_token=token,
            )
        else:
            event = build_w2_event(
                context,
                source_bytes,
                seed=context.seed,
                operation_index=operation_index,
                operation_token=token,
            )
        stages["M2"] = time.perf_counter_ns() - start

        start = time.perf_counter_ns()
        emitted_at = operation_timestamp(
            operation_index,
            base=datetime(2026, 7, 16, 1, 0, tzinfo=timezone.utc),
        )
        if context.workload_id == "W1-HIE-DISCLOSURE":
            core = hie_core_from_event(event, emitted_at=emitted_at)
            envelope_profile = HIE_ENVELOPE_PROFILE
            envelope_version = HIE_ENVELOPE_VERSION
        else:
            core = generic_core_from_event(event, emitted_at=emitted_at)
            envelope_profile = ENVELOPE_PROFILE
            envelope_version = ENVELOPE_VERSION
        # Canonicalisation and digest construction are the M3 boundary.
        digest_bytes = core_digest_bytes(core, envelope_profile=envelope_profile)
        stages["M3"] = time.perf_counter_ns() - start

        start = time.perf_counter_ns()
        message = core_signature_message(
            digest_bytes,
            algorithm="Ed25519",
            key_id=FIXTURE_EMITTER_KEY_ID,
        )
        core["emitter_signature"] = {
            "algorithm": "Ed25519",
            "key_id": FIXTURE_EMITTER_KEY_ID,
            "signature": b64url_encode(fixture_emitter_private_key().sign(message)),
        }
        envelope = {
            "envelope_version": envelope_version,
            "profile": envelope_profile,
            "evidence_core": core,
        }
        envelope_validation = (
            validate_hie_envelope(envelope)
            if context.workload_id == "W1-HIE-DISCLOSURE"
            else validate_envelope(envelope)
        )
        if not envelope_validation.accepted:
            accepted = False
            error_code = envelope_validation.primary_code
        signed_envelope_bytes = canonicalise_te(envelope)
        signed_envelope_size = len(signed_envelope_bytes)
        stages["M4"] = time.perf_counter_ns() - start

        start = time.perf_counter_ns()
        digest_hex = digest_bytes.hex()
        previous_size = context.log.tree_size
        index = context.log.append_core_digest(digest_hex)
        receipt = context.log.issue_receipt(
            index,
            issued_at=operation_timestamp(
                operation_index,
                base=datetime(2026, 7, 16, 2, 0, tzinfo=timezone.utc),
            ),
            private_key=fixture_backend_private_key(),
            signer_key_id=FIXTURE_BACKEND_KEY_ID,
        )
        consistency: Mapping[str, Any] | None = None
        if previous_size > 0:
            consistency = context.log.issue_consistency_proof(previous_size)
        complete = attach_receipt(envelope, receipt)
        receipt_bytes = canonicalise_te(receipt)
        proof_bytes = canonicalise_te(receipt["inclusion_proof"])
        complete_bytes = canonicalise_te(complete)
        receipt_size = len(receipt_bytes)
        proof_size = len(proof_bytes)
        complete_envelope_size = len(complete_bytes)
        signature_size = len(canonicalise_te(core["emitter_signature"])) + len(
            canonicalise_te(receipt["receipt_signature"])
        )
        leaf_input = leaf_input_bytes(
            backend_id=FIXTURE_BACKEND_ID,
            log_id=FIXTURE_LOG_ID,
            core_digest_hex_value=digest_hex,
        )
        context.storage_proxy_accumulator += 32 + len(leaf_input) + receipt_size + proof_size
        checkpoint_value = {
            "backend_id": FIXTURE_BACKEND_ID,
            "log_id": FIXTURE_LOG_ID,
            "tree_size": context.log.tree_size,
            "root_digest": context.log.root_digest,
        }
        storage_proxy = context.storage_proxy_accumulator + len(canonicalise_te(checkpoint_value))
        stages["M5"] = time.perf_counter_ns() - start

        start = time.perf_counter_ns()
        if context.workload_id == "W1-HIE-DISCLOSURE":
            if context.hie_state is None:
                raise RuntimeError("HIE retained verifier is unavailable")
            verification = context.hie_state.verify_and_update(
                complete,
                emitter_keys=emitter_keys(),
                receipt_keys=receipt_keys(),
                consistency_proof=consistency,
            )
        else:
            verification = verify_envelope_receipt(
                complete,
                emitter_keys=emitter_keys(),
                receipt_keys=receipt_keys(),
                expected_backend_id=FIXTURE_BACKEND_ID,
                expected_log_id=FIXTURE_LOG_ID,
                retained_checkpoint=context.generic_checkpoint,
                consistency_proof=consistency,
            )
            if verification.accepted:
                context.generic_checkpoint = RetainedCheckpoint(
                    FIXTURE_BACKEND_ID,
                    FIXTURE_LOG_ID,
                    int(receipt["tree_size"]),
                    str(receipt["root_digest"]),
                )
        if not verification.accepted:
            accepted = False
            error_code = verification.primary_code
        stages["M6"] = time.perf_counter_ns() - start
        context.last_complete_envelope = complete

    stages["M7"] = time.perf_counter_ns() - total_start
    total_application = source_size + audit_size + complete_envelope_size
    findings = 0
    if context.baseline in {"B1", "B2"} and projection is not None:
        findings += payload_exclusion_findings(projection)
    if context.baseline == "B2" and context.last_complete_envelope is not None:
        findings += payload_exclusion_findings(context.last_complete_envelope)

    return {
        "operation_index": operation_index,
        "accepted": accepted,
        "error_code": error_code,
        "stages_ns": stages,
        "source_fhir_bytes": source_size,
        "audit_projection_bytes": audit_size,
        "trust_evidence_envelope_bytes": signed_envelope_size,
        "complete_portable_envelope_bytes": complete_envelope_size,
        "signature_material_bytes": signature_size,
        "receipt_bytes": receipt_size,
        "inclusion_proof_bytes": proof_size,
        "total_application_bytes": total_application,
        "storage_proxy_bytes": storage_proxy,
        "source_sha256": source_digest,
        "source_digest_preserved": source_digest == context.expected_source_sha256,
        "payload_exclusion_findings": findings,
        "measured": measure,
    }


def run_warmup(context: WorkerContext) -> None:
    original = context.baseline
    context.baseline = "B2"
    reset_timed_state(context)
    for index in range(context.warmup_count):
        result = process_operation(context, operation_index=index, measure=False)
        if not result["accepted"]:
            raise RuntimeError(f"Warm-up failed: {result['error_code']}")
    context.baseline = original
    reset_timed_state(context)


def verify_expected_invalid(context: WorkerContext) -> tuple[int, int, int]:
    if context.baseline != "B2" or context.last_complete_envelope is None:
        return 0, 0, 0
    candidate = deepcopy(context.last_complete_envelope)
    candidate["evidence_core"]["outcome"]["reason_code"] = "c5-mutated-after-signing"
    if context.workload_id == "W1-HIE-DISCLOSURE":
        result = verify_hie_envelope_receipt(
            candidate,
            emitter_keys=emitter_keys(),
            receipt_keys=receipt_keys(),
            expected_backend_id=FIXTURE_BACKEND_ID,
            expected_log_id=FIXTURE_LOG_ID,
        )
    else:
        result = verify_envelope_receipt(
            candidate,
            emitter_keys=emitter_keys(),
            receipt_keys=receipt_keys(),
            expected_backend_id=FIXTURE_BACKEND_ID,
            expected_log_id=FIXTURE_LOG_ID,
        )
    rejected = not result.accepted
    return 1, int(rejected), int(not rejected)


def summarise_worker(
    context: WorkerContext,
    operations: Sequence[dict[str, Any]],
    *,
    start_utc: str,
    end_utc: str,
    loop_duration_ns: int,
) -> dict[str, Any]:
    stage_values: dict[str, list[int]] = {
        stage: [int(item["stages_ns"][stage]) for item in operations]
        for stage in STAGES
    }
    expected_invalid, invalid_rejections, false_accepts = verify_expected_invalid(context)
    valid_cases = sum(int(item["accepted"]) for item in operations)
    validation_failures = sum(
        int(not item["accepted"] and str(item["error_code"]).startswith("TE-E-SCHEMA"))
        for item in operations
    )
    verification_failures = sum(int(not item["accepted"]) for item in operations) - validation_failures
    digest_preserved = all(bool(item["source_digest_preserved"]) for item in operations)
    findings = sum(int(item["payload_exclusion_findings"]) for item in operations)
    passed = (
        valid_cases == context.operation_count
        and validation_failures == 0
        and verification_failures == 0
        and invalid_rejections == expected_invalid
        and false_accepts == 0
        and digest_preserved
        and findings == 0
    )

    def median_field(name: str) -> int:
        return median_int([int(item[name]) for item in operations])

    summary: dict[str, Any] = {
        "run_id": RUN_ID,
        "software_status": SOFTWARE_STATUS,
        "phase": context.phase,
        "workload_id": context.workload_id,
        "paired_block_id": context.block_id,
        "baseline": context.baseline,
        "seed": context.seed,
        "warmup_count": context.warmup_count,
        "operation_count": context.operation_count,
        "process_pid": os.getpid(),
        "start_utc": start_utc,
        "end_utc": end_utc,
        "run_duration_ms": loop_duration_ns / 1_000_000,
        "m7_sum_ms": sum(stage_values["M7"]) / 1_000_000,
        "m7_p50_ms": percentile_ns(stage_values["M7"], 0.50),
        "m7_p95_ms": percentile_ns(stage_values["M7"], 0.95),
        "m7_p99_ms": percentile_ns(stage_values["M7"], 0.99),
        "source_fhir_bytes_median": median_field("source_fhir_bytes"),
        "audit_projection_bytes_median": median_field("audit_projection_bytes"),
        "trust_evidence_envelope_bytes_median": median_field("trust_evidence_envelope_bytes"),
        "complete_portable_envelope_bytes_median": median_field("complete_portable_envelope_bytes"),
        "signature_material_bytes_median": median_field("signature_material_bytes"),
        "receipt_bytes_median": median_field("receipt_bytes"),
        "inclusion_proof_bytes_median": median_field("inclusion_proof_bytes"),
        "total_application_bytes_median": median_field("total_application_bytes"),
        "storage_proxy_final_bytes": int(operations[-1]["storage_proxy_bytes"]),
        "valid_cases": valid_cases,
        "validation_failures": validation_failures,
        "verification_failures": verification_failures,
        "expected_invalid_cases": expected_invalid,
        "expected_invalid_rejections": invalid_rejections,
        "false_accepts": false_accepts,
        "false_rejects": context.operation_count - valid_cases,
        "retry_count": 0,
        "source_sha256": context.last_source_sha256,
        "source_digest_preserved": digest_preserved,
        "payload_exclusion_findings": findings,
        "passed": passed,
    }
    for stage in STAGES[:-1]:
        summary[f"{stage.lower()}_p50_ms"] = percentile_ns(stage_values[stage], 0.50)
    return summary


def serialise_run_row(summary: Mapping[str, Any]) -> dict[str, str]:
    row: dict[str, str] = {}
    float_fields = {
        "process_wall_ms",
        "run_duration_ms",
        "m7_sum_ms",
        "m7_p50_ms",
        "m7_p95_ms",
        "m7_p99_ms",
        "m0_p50_ms",
        "m1_p50_ms",
        "m2_p50_ms",
        "m3_p50_ms",
        "m4_p50_ms",
        "m5_p50_ms",
        "m6_p50_ms",
    }
    bool_fields = {"source_digest_preserved", "passed"}
    for field_name in RUN_FIELDS:
        value = summary[field_name]
        if field_name in float_fields:
            row[field_name] = decimal(float(value))
        elif field_name in bool_fields:
            row[field_name] = boolean(bool(value))
        else:
            row[field_name] = str(value)
    return row


def worker_main(args: argparse.Namespace) -> int:
    context = setup_context(
        workload_id=args.workload,
        baseline=args.baseline,
        phase=args.phase,
        block_id=args.block_id,
        seed=args.seed,
        operation_count=args.operations,
        warmup_count=args.warmup,
    )
    run_warmup(context)
    start_utc = utc_now()
    loop_start = time.perf_counter_ns()
    operations = [
        process_operation(context, operation_index=index, measure=True)
        for index in range(args.operations)
    ]
    loop_duration_ns = time.perf_counter_ns() - loop_start
    end_utc = utc_now()
    summary = summarise_worker(
        context,
        operations,
        start_utc=start_utc,
        end_utc=end_utc,
        loop_duration_ns=loop_duration_ns,
    )
    output = {"summary": summary, "operations": operations}
    write_json(args.worker_output, output)
    return 0 if summary["passed"] else 1


def deterministic_order(*, phase: str, block_number: int) -> tuple[int, list[str]]:
    phase_offset = 0 if phase == "pilot" else 100_000
    seed = BASE_SEED + phase_offset + block_number
    order = list(BASELINES)
    random.Random(seed).shuffle(order)
    return seed, order


def run_worker_process(
    *,
    phase: str,
    workload: str,
    block_id: str,
    baseline: str,
    seed: int,
    operations: int,
    warmup: int,
    output_path: Path,
) -> tuple[dict[str, Any], float]:
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        "--phase",
        phase,
        "--workload",
        workload,
        "--block-id",
        block_id,
        "--baseline",
        baseline,
        "--seed",
        str(seed),
        "--operations",
        str(operations),
        "--warmup",
        str(warmup),
        "--worker-output",
        str(output_path),
    ]
    wall_start = time.perf_counter_ns()
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    wall_ms = (time.perf_counter_ns() - wall_start) / 1_000_000
    if result.returncode != 0:
        raise RuntimeError(
            f"worker failed phase={phase} workload={workload} block={block_id} baseline={baseline}\n"
            + result.stdout
        )
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    return payload, wall_ms


def bootstrap_ci(
    values: Sequence[float], *, seed: int, resamples: int
) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], values[0]
    rng = random.Random(seed)
    n = len(values)
    estimates: list[float] = []
    for _ in range(resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        estimates.append(float(statistics.median(sample)))
    return nearest_rank(estimates, 0.025), nearest_rank(estimates, 0.975)


def build_pair_rows(retained: Sequence[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], dict[str, dict[str, str]]] = {}
    for row in retained:
        grouped.setdefault((row["workload_id"], row["paired_block_id"]), {})[
            row["baseline"]
        ] = row
    pairs: list[dict[str, str]] = []
    for (workload, block_id), baselines in sorted(grouped.items()):
        if set(baselines) != set(BASELINES):
            raise ValueError(f"Incomplete paired block: {workload}/{block_id}")
        for comparison, upper_name, lower_name in COMPARISONS:
            upper = baselines[upper_name]
            lower = baselines[lower_name]
            pairs.append(
                {
                    "run_id": RUN_ID,
                    "workload_id": workload,
                    "paired_block_id": block_id,
                    "seed": upper["seed"],
                    "baseline_order": upper["baseline_order"],
                    "comparison": comparison,
                    "run_duration_increment_ms": decimal(
                        float(upper["run_duration_ms"]) - float(lower["run_duration_ms"])
                    ),
                    "m7_p50_increment_ms": decimal(
                        float(upper["m7_p50_ms"]) - float(lower["m7_p50_ms"])
                    ),
                    "m7_p95_increment_ms": decimal(
                        float(upper["m7_p95_ms"]) - float(lower["m7_p95_ms"])
                    ),
                    "m7_p99_increment_ms": decimal(
                        float(upper["m7_p99_ms"]) - float(lower["m7_p99_ms"])
                    ),
                    "total_application_bytes_increment": str(
                        int(upper["total_application_bytes_median"])
                        - int(lower["total_application_bytes_median"])
                    ),
                    "storage_proxy_bytes_increment": str(
                        int(upper["storage_proxy_final_bytes"])
                        - int(lower["storage_proxy_final_bytes"])
                    ),
                }
            )
    return pairs


def build_aggregate_rows(
    pairs: Sequence[dict[str, str]], *, bootstrap_resamples: int, workloads: Sequence[str]
) -> list[dict[str, str]]:
    metric_map = {
        "run_duration_ms": "run_duration_increment_ms",
        "m7_p50_ms": "m7_p50_increment_ms",
        "m7_p95_ms": "m7_p95_increment_ms",
        "m7_p99_ms": "m7_p99_increment_ms",
        "total_application_bytes_median": "total_application_bytes_increment",
        "storage_proxy_final_bytes": "storage_proxy_bytes_increment",
    }
    rows: list[dict[str, str]] = []
    for workload in workloads:
        for comparison, _, _ in COMPARISONS:
            selected = [
                row
                for row in pairs
                if row["workload_id"] == workload and row["comparison"] == comparison
            ]
            for metric_index, (metric, unit) in enumerate(PRIMARY_METRICS):
                values = [float(row[metric_map[metric]]) for row in selected]
                ci_low, ci_high = bootstrap_ci(
                    values,
                    seed=BASE_SEED + metric_index + sum(ord(c) for c in workload + comparison),
                    resamples=bootstrap_resamples,
                )
                rows.append(
                    {
                        "run_id": RUN_ID,
                        "workload_id": workload,
                        "comparison": comparison,
                        "metric": metric,
                        "unit": unit,
                        "n_pairs": str(len(values)),
                        "median_increment": decimal(float(statistics.median(values))),
                        "mean_increment": decimal(float(statistics.mean(values))),
                        "ci95_low": decimal(ci_low),
                        "ci95_high": decimal(ci_high),
                        "minimum_increment": decimal(min(values)),
                        "maximum_increment": decimal(max(values)),
                        "estimator": "paired-block median; deterministic percentile bootstrap 95% CI",
                        "claim_boundary": "local reference-pipeline increment; not production EHR or hospital latency",
                    }
                )
    return rows


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def output_file_digests(output_dir: Path) -> dict[str, str]:
    return {
        path.relative_to(output_dir).as_posix(): file_sha256(path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "execution_manifest.json"
    }


def build_readme(summary: Mapping[str, Any]) -> str:
    return f"""# Route C C5 local incremental-overhead evidence

This directory retains the process-level paired B0--B2 experiment for the
selected frozen synthetic workload(s). Pilot runs are retained but excluded
from the confirmatory estimates.

## Frozen execution

- pilot paired blocks: {summary['pilot_blocks']}
- retained paired blocks: {summary['retained_blocks']}
- baselines per block: B0, B1 and B2
- confirmatory workloads: {", ".join(summary["workload_ids"])}
- secondary workload status: {summary["secondary_workload_omission"] or "included"}
- operation samples per process-level run: {summary['operations_per_run']}
- identical full-path warm-up operations per process: {summary['warmup_operations']}
- confidence interval: deterministic percentile bootstrap over independent paired-block increments

## Baselines

- B0 parses, locally validates and canonicalises the frozen source FHIR case.
- B1 performs B0 and constructs the conventional AuditEvent/Provenance projection.
- B2 performs B1 and adds fact extraction, minimisation/semantic validation,
  TE-JCS canonicalisation, Ed25519 issuer signing, local A2 append/receipt,
  inclusion/consistency material and complete verification.

## Evidence files

- `pilot_runs.csv`: process-level pilot summaries, excluded from confirmatory analysis;
- `retained_runs.csv`: process-level retained summaries;
- `paired_increments.csv`: B1-B0, B2-B1 and B2-B0 paired differences;
- `aggregate_estimates.csv`: median paired increments and 95% bootstrap intervals;
- `pilot_operation_timings.jsonl` and `retained_operation_timings.jsonl`: raw operation-level measurements;
- `run_summary.json`: counts, correctness decisions and claim boundary;
- `hardware_profile.json`: host and software disclosure;
- `execution_manifest.json`: source commit, workflow provenance and file digests.

## Claim boundary

The retained values estimate processing, application-byte and local-storage-
proxy increments in the declared Python reference pipeline on the reported
host. They do not estimate production EHR overhead, hospital latency, network
capacity, distributed-service scalability, organisational cost reduction or a
service-level guarantee. No equivalence or negligible-overhead margin was
preregistered; therefore no such claim is made.
"""


def execute_experiment(
    output_dir: Path,
    *,
    pilot_blocks: int,
    retained_blocks: int,
    operations: int,
    warmup: int,
    bootstrap_resamples: int,
    workloads: Sequence[str],
) -> dict[str, Any]:
    if pilot_blocks < 1 or retained_blocks < 1 or operations < 8 or warmup < 1:
        raise ValueError("pilot/retained blocks and warm-up must be positive; operations must be at least eight")
    output_dir.mkdir(parents=True, exist_ok=True)
    started_utc = utc_now()
    process_rows: dict[str, list[dict[str, str]]] = {"pilot": [], "retained": []}
    operation_rows: dict[str, list[dict[str, Any]]] = {"pilot": [], "retained": []}

    with tempfile.TemporaryDirectory(prefix="route-c-c5-") as tmp_text:
        tmp = Path(tmp_text)
        for phase, block_count in (("pilot", pilot_blocks), ("retained", retained_blocks)):
            for block_number in range(1, block_count + 1):
                seed, order = deterministic_order(phase=phase, block_number=block_number)
                block_id = f"{phase[0].upper()}{block_number:03d}"
                order_text = ">".join(order)
                for workload in workloads:
                    for order_position, baseline in enumerate(order, 1):
                        worker_path = tmp / f"{phase}-{workload}-{block_id}-{baseline}.json"
                        payload, process_wall_ms = run_worker_process(
                            phase=phase,
                            workload=workload,
                            block_id=block_id,
                            baseline=baseline,
                            seed=seed,
                            operations=operations,
                            warmup=warmup,
                            output_path=worker_path,
                        )
                        summary = payload["summary"]
                        summary["baseline_order"] = order_text
                        summary["order_position"] = order_position
                        summary["process_wall_ms"] = process_wall_ms
                        process_rows[phase].append(serialise_run_row(summary))
                        for operation in payload["operations"]:
                            operation_rows[phase].append(
                                {
                                    "run_id": RUN_ID,
                                    "phase": phase,
                                    "workload_id": workload,
                                    "paired_block_id": block_id,
                                    "baseline": baseline,
                                    "baseline_order": order_text,
                                    "order_position": order_position,
                                    "seed": seed,
                                    **operation,
                                }
                            )
                        print(
                            f"C5 progress phase={phase} block={block_id} workload={workload} baseline={baseline}",
                            file=sys.stderr,
                            flush=True,
                        )

    retained = sorted(
        process_rows["retained"],
        key=lambda row: (row["workload_id"], row["paired_block_id"], int(row["order_position"])),
    )
    pilot = sorted(
        process_rows["pilot"],
        key=lambda row: (row["workload_id"], row["paired_block_id"], int(row["order_position"])),
    )
    pairs = build_pair_rows(retained)
    aggregates = build_aggregate_rows(
        pairs, bootstrap_resamples=bootstrap_resamples, workloads=workloads
    )

    write_csv(output_dir / "pilot_runs.csv", pilot, RUN_FIELDS)
    write_csv(output_dir / "retained_runs.csv", retained, RUN_FIELDS)
    write_csv(output_dir / "paired_increments.csv", pairs, PAIR_FIELDS)
    write_csv(output_dir / "aggregate_estimates.csv", aggregates, AGGREGATE_FIELDS)
    for phase in ("pilot", "retained"):
        path = output_dir / f"{phase}_operation_timings.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for row in sorted(
                operation_rows[phase],
                key=lambda item: (
                    item["workload_id"],
                    item["paired_block_id"],
                    item["order_position"],
                    item["operation_index"],
                ),
            ):
                handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

    all_rows = pilot + retained
    summary = {
        "run_id": RUN_ID,
        "software_status": SOFTWARE_STATUS,
        "started_utc": started_utc,
        "completed_utc": utc_now(),
        "pilot_blocks": pilot_blocks,
        "retained_blocks": retained_blocks,
        "workload_count": len(workloads),
        "workload_ids": list(workloads),
        "secondary_workload_omission": (
            None
            if "W2-WEARABLE-BATCH" in workloads
            else "W2 was omitted from confirmatory materialisation under the frozen critical-path clause; no W2 overhead estimate is claimed"
        ),
        "baseline_count": len(BASELINES),
        "operations_per_run": operations,
        "warmup_operations": warmup,
        "bootstrap_resamples": bootstrap_resamples,
        "pilot_process_runs": len(pilot),
        "retained_process_runs": len(retained),
        "retained_operation_samples": len(operation_rows["retained"]),
        "paired_increment_rows": len(pairs),
        "aggregate_estimate_rows": len(aggregates),
        "failed_process_runs": sum(row["passed"] != "true" for row in all_rows),
        "validation_failures": sum(int(row["validation_failures"]) for row in all_rows),
        "verification_failures": sum(int(row["verification_failures"]) for row in all_rows),
        "false_accepts": sum(int(row["false_accepts"]) for row in all_rows),
        "false_rejects": sum(int(row["false_rejects"]) for row in all_rows),
        "expected_invalid_cases": sum(int(row["expected_invalid_cases"]) for row in all_rows),
        "expected_invalid_rejections": sum(
            int(row["expected_invalid_rejections"]) for row in all_rows
        ),
        "payload_exclusion_findings": sum(
            int(row["payload_exclusion_findings"]) for row in all_rows
        ),
        "source_digest_failures": sum(
            row["source_digest_preserved"] != "true" for row in all_rows
        ),
        "pilot_excluded_from_confirmatory_estimates": True,
        "independent_replicate": "fresh Python process per baseline/workload/paired block",
        "pairing": "same workload, seed, source fixture, operation count and timestamps within each block",
        "order_randomisation": "deterministic shuffled B0/B1/B2 order; the same order is applied to every selected workload in each block",
        "p99_definition": f"nearest-rank p99 over {operations} operation samples per process-level run",
        "primary_estimator": "median paired-block increment with deterministic percentile-bootstrap 95% interval",
        "claim_boundary": {
            "supported": "local reference-pipeline processing, application-byte and storage-proxy increments on the reported host",
            "not_supported": [
                "production EHR overhead",
                "hospital latency or service-level acceptability",
                "network or distributed-service scalability",
                "organisational cost reduction",
                "deployment readiness",
                "negligible or equivalent overhead",
            ],
        },
    }
    summary["passed"] = (
        summary["failed_process_runs"] == 0
        and summary["validation_failures"] == 0
        and summary["verification_failures"] == 0
        and summary["false_accepts"] == 0
        and summary["false_rejects"] == 0
        and summary["expected_invalid_cases"] == summary["expected_invalid_rejections"]
        and summary["payload_exclusion_findings"] == 0
        and summary["source_digest_failures"] == 0
    )
    write_json(output_dir / "run_summary.json", summary)
    write_json(output_dir / "hardware_profile.json", hardware_profile())
    (output_dir / "README.md").write_text(build_readme(summary), encoding="utf-8", newline="\n")
    manifest = {
        "run_id": RUN_ID,
        "source_commit": repository_commit(),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID", "not-available"),
        "workflow_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "not-available"),
        "python_executable": sys.executable,
        "command_parameters": {
            "pilot_blocks": pilot_blocks,
            "retained_blocks": retained_blocks,
            "operations": operations,
            "warmup": warmup,
            "bootstrap_resamples": bootstrap_resamples,
            "workloads": list(workloads),
        },
        "source_files": {
            W1_SOURCE.relative_to(ROOT).as_posix(): file_sha256(W1_SOURCE),
            W2_SOURCE.relative_to(ROOT).as_posix(): file_sha256(W2_SOURCE),
            W2_EVENT_TEMPLATE.relative_to(ROOT).as_posix(): file_sha256(W2_EVENT_TEMPLATE),
            Path(__file__).resolve().relative_to(ROOT).as_posix(): file_sha256(Path(__file__).resolve()),
            "docs/route_c/MEASUREMENT_PROTOCOL.md": file_sha256(
                ROOT / "docs" / "route_c" / "MEASUREMENT_PROTOCOL.md"
            ),
        },
        "output_files": output_file_digests(output_dir),
    }
    write_json(output_dir / "execution_manifest.json", manifest)
    return summary


def recompute_derived(output_dir: Path, summary: Mapping[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    retained = read_csv(output_dir / "retained_runs.csv")
    pairs = build_pair_rows(retained)
    aggregates = build_aggregate_rows(
        pairs,
        bootstrap_resamples=int(summary["bootstrap_resamples"]),
        workloads=tuple(summary["workload_ids"]),
    )
    return pairs, aggregates


def check_outputs(output_dir: Path, *, require_full: bool = True) -> int:
    required = {
        "README.md",
        "pilot_runs.csv",
        "retained_runs.csv",
        "paired_increments.csv",
        "aggregate_estimates.csv",
        "pilot_operation_timings.jsonl",
        "retained_operation_timings.jsonl",
        "run_summary.json",
        "hardware_profile.json",
        "execution_manifest.json",
    }
    missing = sorted(name for name in required if not (output_dir / name).is_file())
    errors: list[str] = []
    if missing:
        errors.extend(f"missing: {name}" for name in missing)
    if errors:
        print("C5-OVERHEAD-CHECK: FAIL")
        print("\n".join(errors))
        return 1

    summary = json.loads((output_dir / "run_summary.json").read_text(encoding="utf-8"))
    pilot = read_csv(output_dir / "pilot_runs.csv")
    retained = read_csv(output_dir / "retained_runs.csv")
    pairs = read_csv(output_dir / "paired_increments.csv")
    aggregates = read_csv(output_dir / "aggregate_estimates.csv")
    pilot_raw = read_jsonl(output_dir / "pilot_operation_timings.jsonl")
    retained_raw = read_jsonl(output_dir / "retained_operation_timings.jsonl")

    workloads = tuple(summary["workload_ids"])
    expected_pilot = int(summary["pilot_blocks"]) * len(workloads) * len(BASELINES)
    expected_retained = int(summary["retained_blocks"]) * len(workloads) * len(BASELINES)
    expected_pairs = int(summary["retained_blocks"]) * len(workloads) * len(COMPARISONS)
    expected_aggregates = len(workloads) * len(COMPARISONS) * len(PRIMARY_METRICS)
    expected_pilot_raw = expected_pilot * int(summary["operations_per_run"])
    expected_retained_raw = expected_retained * int(summary["operations_per_run"])

    checks = [
        (len(pilot) == expected_pilot, f"pilot rows={len(pilot)}, expected={expected_pilot}"),
        (len(retained) == expected_retained, f"retained rows={len(retained)}, expected={expected_retained}"),
        (len(pairs) == expected_pairs, f"pair rows={len(pairs)}, expected={expected_pairs}"),
        (len(aggregates) == expected_aggregates, f"aggregate rows={len(aggregates)}, expected={expected_aggregates}"),
        (len(pilot_raw) == expected_pilot_raw, f"pilot raw rows={len(pilot_raw)}, expected={expected_pilot_raw}"),
        (len(retained_raw) == expected_retained_raw, f"retained raw rows={len(retained_raw)}, expected={expected_retained_raw}"),
        (bool(summary.get("pilot_excluded_from_confirmatory_estimates")), "pilot exclusion flag is false"),
        (bool(summary.get("passed")), "run summary does not report PASS"),
    ]
    if require_full:
        checks.extend(
            [
                (int(summary["pilot_blocks"]) == DEFAULT_PILOT_BLOCKS, "full pilot block count differs from protocol"),
                (int(summary["retained_blocks"]) >= DEFAULT_RETAINED_BLOCKS, "fewer than twenty retained paired blocks"),
                (int(summary["operations_per_run"]) >= DEFAULT_OPERATIONS, "fewer than 128 operations per process run"),
            ]
        )
    for accepted, message in checks:
        if not accepted:
            errors.append(message)

    for phase_name, rows in (("pilot", pilot), ("retained", retained)):
        groups: dict[tuple[str, str], list[dict[str, str]]] = {}
        for row in rows:
            groups.setdefault((row["workload_id"], row["paired_block_id"]), []).append(row)
            if row["passed"] != "true":
                errors.append(f"failed {phase_name} run: {row['workload_id']}/{row['paired_block_id']}/{row['baseline']}")
            if row["source_digest_preserved"] != "true":
                errors.append(f"source digest failure: {row['workload_id']}/{row['paired_block_id']}/{row['baseline']}")
            if int(row["payload_exclusion_findings"]):
                errors.append(f"payload exclusion finding: {row['workload_id']}/{row['paired_block_id']}/{row['baseline']}")
        for key, members in groups.items():
            if {row["baseline"] for row in members} != set(BASELINES):
                errors.append(f"incomplete block {key}")
            if {row["seed"] for row in members}.__len__() != 1:
                errors.append(f"seed mismatch in block {key}")
            if {row["baseline_order"] for row in members}.__len__() != 1:
                errors.append(f"order mismatch in block {key}")
            if sorted(int(row["order_position"]) for row in members) != [1, 2, 3]:
                errors.append(f"order positions invalid in block {key}")

    derived_pairs, derived_aggregates = recompute_derived(output_dir, summary)
    if stable_json_bytes(pairs) != stable_json_bytes(derived_pairs):
        errors.append("paired_increments.csv differs from deterministic recomputation")
    if stable_json_bytes(aggregates) != stable_json_bytes(derived_aggregates):
        errors.append("aggregate_estimates.csv differs from deterministic recomputation")

    manifest = json.loads((output_dir / "execution_manifest.json").read_text(encoding="utf-8"))
    expected_digests = output_file_digests(output_dir)
    if manifest.get("output_files") != expected_digests:
        errors.append("execution_manifest output digests are stale")

    if errors:
        print("C5-OVERHEAD-CHECK: FAIL")
        print("\n".join(errors))
        return 1
    print(
        "C5-OVERHEAD-CHECK: PASS "
        f"({len(retained)} retained process runs, {len(retained_raw)} raw timings, "
        f"{len(pairs)} paired increments, {len(aggregates)} aggregate estimates)"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pilot-blocks", type=int, default=DEFAULT_PILOT_BLOCKS)
    parser.add_argument("--retained-blocks", type=int, default=DEFAULT_RETAINED_BLOCKS)
    parser.add_argument("--operations", type=int, default=DEFAULT_OPERATIONS)
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP)
    parser.add_argument("--bootstrap-resamples", type=int, default=DEFAULT_BOOTSTRAP_RESAMPLES)
    parser.add_argument("--workloads", nargs="+", choices=ALL_WORKLOADS, default=list(CONFIRMATORY_WORKLOADS))
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--check", action="store_true")

    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--phase", choices=("pilot", "retained"), help=argparse.SUPPRESS)
    parser.add_argument("--workload", choices=ALL_WORKLOADS, help=argparse.SUPPRESS)
    parser.add_argument("--block-id", help=argparse.SUPPRESS)
    parser.add_argument("--baseline", choices=BASELINES, help=argparse.SUPPRESS)
    parser.add_argument("--seed", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--worker-output", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.worker:
        required = (args.phase, args.workload, args.block_id, args.baseline, args.seed, args.worker_output)
        if any(value is None for value in required):
            raise SystemExit("worker mode requires phase, workload, block-id, baseline, seed and worker-output")
        return worker_main(args)

    output = args.output_dir.resolve()
    if args.check:
        return check_outputs(output, require_full=not args.quick)
    if args.quick:
        args.pilot_blocks = 1
        args.retained_blocks = 2
        args.operations = 8
        args.warmup = 1
        args.bootstrap_resamples = 500
    summary = execute_experiment(
        output,
        pilot_blocks=args.pilot_blocks,
        retained_blocks=args.retained_blocks,
        operations=args.operations,
        warmup=args.warmup,
        bootstrap_resamples=args.bootstrap_resamples,
        workloads=tuple(args.workloads),
    )
    result = check_outputs(output, require_full=not args.quick)
    print(json.dumps(summary, sort_keys=True))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
