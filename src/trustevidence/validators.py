"""Semantic, state and minimisation validation for TrustEvidence objects."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

from . import errors
from .schema import validate_structure

_NORMALISED_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
_INPUT_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$")
_EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_PHONE = re.compile(r"(?<![A-Za-z0-9])\+?[0-9][0-9 ()-]{8,}[0-9](?![A-Za-z0-9])")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_NHS = re.compile(r"\b\d{3}\s?\d{3}\s?\d{4}\b")
_ABS_PATH = re.compile(r"^(?:/home/|/Users/|/tmp/|[A-Za-z]:\\)")
_PRIVATE_ENDPOINT = re.compile(r"(?i)(?:localhost|127\.0\.0\.1|(?:10|192\.168)\.\d{1,3}\.\d{1,3})")
_UUID_URN = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

PROHIBITED_PAYLOAD_KEYS = {
    "value", "valuequantity", "valueinteger", "valuedecimal", "valuestring",
    "measurement", "measurements", "glucose", "glucose_value", "heart_rate",
    "blood_pressure", "systolic", "diastolic", "oxygen_saturation", "temperature",
    "waveform", "waveforms", "samples", "readings", "raw_payload", "payload_bytes",
    "clinical_note", "diagnosis", "narrative", "resourcetype", "nonce",
}
PROHIBITED_IDENTIFIER_KEYS = {
    "patient_name", "given_name", "family_name", "full_name", "email", "phone",
    "telephone", "address", "postal_address", "mrn", "medical_record_number", "ssn",
    "national_identifier", "national_id", "nhs_number", "identifier_value",
}

ALLOWED_TRANSITIONS = {
    ("draft", "active"),
    ("active", "inactive"),
    ("active", "revoked"),
    ("active", "superseded"),
    ("draft", "entered-in-error"),
    ("active", "entered-in-error"),
    ("inactive", "entered-in-error"),
    ("revoked", "entered-in-error"),
    ("superseded", "entered-in-error"),
}


@dataclass(frozen=True, slots=True)
class ValidationResult:
    accepted: bool
    issues: tuple[errors.ValidationIssue, ...]

    @property
    def primary_code(self) -> str:
        return "PASS" if self.accepted else self.issues[0].code

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(issue.code for issue in self.issues)


def _issue(code: str, path: str, message: str, layer: str = "semantic") -> errors.ValidationIssue:
    return errors.ValidationIssue(code=code, path=path, message=message, layer=layer)


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any, str | None]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, child, key
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, child, None
            yield from _walk(child, child_path)


def _leakage_issues(instance: Any) -> list[errors.ValidationIssue]:
    found: list[errors.ValidationIssue] = []
    for path, value, key in _walk(instance):
        key_norm = key.lower().replace("-", "_") if key else None
        if key_norm in PROHIBITED_PAYLOAD_KEYS:
            found.append(_issue(errors.MIN_PAYLOAD, path, f"Prohibited payload-like key: {key}", "minimisation"))
            continue
        if key_norm in PROHIBITED_IDENTIFIER_KEYS:
            found.append(_issue(errors.MIN_IDENTIFIER, path, f"Prohibited direct-identifier key: {key}", "minimisation"))
            continue
        if isinstance(value, str):
            # UUID URNs are opaque evidence identifiers.  Their digit/hyphen
            # layout can accidentally satisfy permissive telephone-number
            # regular expressions, so only the exact UUID-URN grammar is
            # exempted from numeric identifier heuristics.  Email detection
            # and infrastructure screening still apply to every string.
            numeric_identifier = (
                not _UUID_URN.fullmatch(value)
                and (_SSN.search(value) or _NHS.search(value) or _PHONE.search(value))
            )
            if _EMAIL.search(value) or numeric_identifier:
                found.append(_issue(errors.MIN_IDENTIFIER, path, "Direct-identifier pattern detected", "minimisation"))
            elif _ABS_PATH.search(value) or _PRIVATE_ENDPOINT.search(value):
                found.append(_issue(errors.MIN_INFRA, path, "Local path or private infrastructure address detected", "minimisation"))
    return found


def _parse_time(value: Any, *, normalised: bool) -> datetime | None:
    if not isinstance(value, str):
        return None
    pattern = _NORMALISED_TIME if normalised else _INPUT_TIME
    if not pattern.fullmatch(value):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def normalise_timestamp(value: str) -> str:
    parsed = _parse_time(value, normalised=False)
    if parsed is None:
        raise ValueError(f"Invalid RFC 3339 timestamp: {value}")
    milliseconds = parsed.microsecond // 1000
    parsed = parsed.replace(microsecond=milliseconds * 1000)
    return parsed.strftime("%Y-%m-%dT%H:%M:%S.") + f"{milliseconds:03d}Z"


def _timestamp_issues(instance: dict[str, Any], *, normalised: bool) -> list[errors.ValidationIssue]:
    paths: list[tuple[str, Any]] = []
    if normalised:
        core = instance.get("evidence_core", {}) if isinstance(instance, dict) else {}
        paths.extend([("$.evidence_core.occurred_at", core.get("occurred_at")), ("$.evidence_core.emitted_at", core.get("emitted_at"))])
        facts = core.get("event_facts", {}) if isinstance(core.get("event_facts"), dict) else {}
        prefix = "$.evidence_core.event_facts"
        receipt = instance.get("backend_receipt") if isinstance(instance, dict) else None
        if isinstance(receipt, dict):
            paths.append(("$.backend_receipt.issued_at", receipt.get("issued_at")))
    else:
        paths.append(("$.occurred_at", instance.get("occurred_at") if isinstance(instance, dict) else None))
        facts = instance.get("event_facts", {}) if isinstance(instance, dict) and isinstance(instance.get("event_facts"), dict) else {}
        prefix = "$.event_facts"
    for key in ("effective_at", "activity_started_at", "activity_ended_at", "window_start", "window_end"):
        if key in facts:
            paths.append((f"{prefix}.{key}", facts.get(key)))
    for period_name in ("capture_period", "summary_period"):
        period = facts.get(period_name)
        if isinstance(period, dict):
            paths.extend([(f"{prefix}.{period_name}.start", period.get("start")), (f"{prefix}.{period_name}.end", period.get("end"))])
    return [
        _issue(errors.TIMESTAMP_FORMAT, path, "Timestamp is not admitted by the profile", "timestamp-admission")
        for path, value in paths
        if value is not None and _parse_time(value, normalised=normalised) is None
    ]


def _roles(objects: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for obj in objects:
        result.setdefault(str(obj.get("object_role")), []).append(obj)
    return result


def _pre_schema_semantics(instance: dict[str, Any], *, envelope: bool) -> list[errors.ValidationIssue]:
    core = instance.get("evidence_core", {}) if envelope else instance
    facts = core.get("event_facts", {}) if isinstance(core, dict) else {}
    event_type = core.get("event_type") if isinstance(core, dict) else None
    issues: list[errors.ValidationIssue] = []
    if event_type == "aggregation-event" and isinstance(facts, dict):
        count = facts.get("sample_count")
        missing = facts.get("missingness_count")
        if isinstance(count, int) and count < 1:
            issues.append(_issue(errors.AGGREGATION_COUNT, "$.evidence_core.event_facts.sample_count" if envelope else "$.event_facts.sample_count", "sample_count must be positive"))
        if isinstance(count, int) and isinstance(missing, int) and (missing < 0 or missing > count):
            issues.append(_issue(errors.AGGREGATION_COUNT, "$.evidence_core.event_facts.missingness_count" if envelope else "$.event_facts.missingness_count", "missingness_count must be between zero and sample_count"))
    if event_type == "consent-state-transition" and isinstance(facts, dict):
        previous = facts.get("previous_state")
        new = facts.get("new_state")
        if isinstance(previous, str) and isinstance(new, str):
            reason = facts.get("transition_reason_code")
            if previous == new or (previous, new) not in ALLOWED_TRANSITIONS:
                issues.append(_issue(errors.CONSENT_STATE, "$.evidence_core.event_facts" if envelope else "$.event_facts", f"Transition {previous!r} to {new!r} is not admitted"))
            elif new == "entered-in-error" and reason != "error-correction":
                issues.append(_issue(errors.CONSENT_STATE, "$.evidence_core.event_facts.transition_reason_code" if envelope else "$.event_facts.transition_reason_code", "entered-in-error requires error-correction"))
    if envelope:
        receipt = instance.get("backend_receipt")
        if isinstance(receipt, dict):
            proof = receipt.get("inclusion_proof")
            if isinstance(proof, dict):
                if proof.get("leaf_index") != receipt.get("leaf_index"):
                    issues.append(_issue(errors.PROOF_INDEX, "$.backend_receipt.inclusion_proof.leaf_index", "Proof and receipt leaf indices differ"))
                if proof.get("tree_size") != receipt.get("tree_size"):
                    issues.append(_issue(errors.PROOF_SIZE, "$.backend_receipt.inclusion_proof.tree_size", "Proof and receipt tree sizes differ"))
            index, size = receipt.get("leaf_index"), receipt.get("tree_size")
            if isinstance(size, int) and size <= 0:
                issues.append(_issue(errors.PROOF_SIZE, "$.backend_receipt.tree_size", "tree_size must be positive"))
            elif isinstance(index, int) and isinstance(size, int) and not (0 <= index < size):
                issues.append(_issue(errors.PROOF_INDEX, "$.backend_receipt.leaf_index", "leaf_index must be within tree_size"))
    return issues


def _semantic_issues(instance: dict[str, Any], *, envelope: bool) -> list[errors.ValidationIssue]:
    core = instance["evidence_core"] if envelope else instance
    objects_key = "objects" if envelope else "object_contexts"
    objects = core.get(objects_key, [])
    roles = _roles(objects) if isinstance(objects, list) else {}
    event_type = core.get("event_type")
    facts = core.get("event_facts", {})
    issues: list[errors.ValidationIssue] = []
    path_prefix = "$.evidence_core" if envelope else "$"

    # Temporal order and bounded skew.
    occurred = _parse_time(core.get("occurred_at"), normalised=envelope)
    if envelope:
        emitted = _parse_time(core.get("emitted_at"), normalised=True)
        skew_ms = core.get("time_source", {}).get("max_skew_ms", 0) if isinstance(core.get("time_source"), dict) else 0
        if occurred and emitted and (occurred - emitted).total_seconds() * 1000 > skew_ms:
            issues.append(_issue(errors.TIMESTAMP_ORDER, f"{path_prefix}.emitted_at", "emitted_at precedes occurred_at beyond declared skew"))
    for start_name, end_name in (("activity_started_at", "activity_ended_at"), ("window_start", "window_end")):
        start, end = _parse_time(facts.get(start_name), normalised=envelope), _parse_time(facts.get(end_name), normalised=envelope)
        if start and end and end <= start:
            code = errors.AGGREGATION_WINDOW if event_type == "aggregation-event" else errors.TIMESTAMP_ORDER
            issues.append(_issue(code, f"{path_prefix}.event_facts.{end_name}", f"{end_name} must be after {start_name}"))
    for period_name in ("capture_period", "summary_period"):
        period = facts.get(period_name)
        if isinstance(period, dict):
            start, end = _parse_time(period.get("start"), normalised=envelope), _parse_time(period.get("end"), normalised=envelope)
            if start and end and end <= start:
                issues.append(_issue(errors.TIMESTAMP_ORDER, f"{path_prefix}.event_facts.{period_name}.end", "Interval end must be after start"))

    # Subject consistency.
    subject = core.get("subject_context", {})
    if isinstance(subject, dict):
        status = subject.get("status")
        subject_token = subject.get("subject_ref_token")
        for index, obj in enumerate(objects if isinstance(objects, list) else []):
            obj_subject = obj.get("subject_ref_token") if isinstance(obj, dict) else None
            if status == "pseudonymous" and obj_subject is not None and obj_subject != subject_token:
                issues.append(_issue(errors.SUBJECT_CONSISTENCY, f"{path_prefix}.{objects_key}[{index}].subject_ref_token", "Object subject token differs from envelope subject token"))
            if status == "not-applicable" and obj_subject is not None:
                issues.append(_issue(errors.SUBJECT_CONSISTENCY, f"{path_prefix}.{objects_key}[{index}].subject_ref_token", "Not-applicable subject context cannot carry an object subject token"))

    # Duplicate object binding.
    seen: set[tuple[Any, Any, Any]] = set()
    for index, obj in enumerate(objects if isinstance(objects, list) else []):
        if not isinstance(obj, dict):
            continue
        key = (obj.get("object_ref_token"), obj.get("object_role"), obj.get("resource_version_token"))
        if key in seen:
            issues.append(_issue(errors.OBJECT_DUPLICATE, f"{path_prefix}.{objects_key}[{index}]", "Duplicate object token/role/version binding"))
        seen.add(key)

    required_roles = {
        "monitoring-object-registration": {"target"},
        "access-event": {"target"},
        "consent-state-transition": {"consent"},
        "provenance-transform": {"input", "output"},
        "disclosure-event": {"target"},
        "aggregation-event": {"input", "output"},
        "failure-event": {"target"},
    }
    missing_roles = required_roles.get(event_type, set()) - set(roles)
    if missing_roles:
        issues.append(_issue(errors.OBJECT_ROLE, f"{path_prefix}.{objects_key}", "Missing required object role(s): " + ", ".join(sorted(missing_roles))))

    if event_type == "access-event":
        policy = core.get("policy_binding") if envelope else core.get("policy_context", {}).get("policy_binding")
        consent = core.get("consent_binding") if envelope else core.get("policy_context", {}).get("consent_binding")
        if facts.get("decision_source_code") == "consent-policy-engine" and consent is None:
            issues.append(_issue(errors.SCHEMA_REQUIRED, path_prefix, "Consent-mediated access requires consent_binding"))
        if policy is None:
            issues.append(_issue(errors.SCHEMA_REQUIRED, path_prefix, "Access requires policy_binding"))
    if event_type == "disclosure-event":
        policy = core.get("policy_binding") if envelope else core.get("policy_context", {}).get("policy_binding")
        consent = core.get("consent_binding") if envelope else core.get("policy_context", {}).get("consent_binding")
        if policy is None or consent is None:
            issues.append(_issue(errors.SCHEMA_REQUIRED, path_prefix, "Disclosure requires policy and consent bindings"))

    if event_type == "provenance-transform" and roles.get("input") and roles.get("output"):
        for inp in roles["input"]:
            for out in roles["output"]:
                if inp.get("object_ref_token") == out.get("object_ref_token") and inp.get("resource_version_token") == out.get("resource_version_token"):
                    issues.append(_issue(errors.PROVENANCE_LINK, f"{path_prefix}.{objects_key}", "Input and output cannot be identical without a version change"))

    if event_type == "aggregation-event":
        count = facts.get("sample_count")
        missing = facts.get("missingness_count", 0)
        if isinstance(count, int) and isinstance(missing, int) and missing > count:
            issues.append(_issue(errors.AGGREGATION_COUNT, f"{path_prefix}.event_facts.missingness_count", "missingness_count exceeds sample_count"))

    if event_type == "monitoring-object-registration":
        mode = facts.get("payload_binding_mode")
        targets = roles.get("target", [])
        has_binding = any(isinstance(obj, dict) and "payload_binding" in obj for obj in targets)
        if mode == "commitment" and not has_binding:
            issues.append(_issue(errors.PAYLOAD_BINDING, f"{path_prefix}.{objects_key}", "commitment mode requires a target payload_binding"))
        if mode == "none" and has_binding:
            issues.append(_issue(errors.PAYLOAD_BINDING, f"{path_prefix}.{objects_key}", "none mode cannot carry a payload_binding"))

    if event_type == "failure-event":
        output_status = facts.get("output_status")
        if output_status == "not-created" and "output" in roles:
            issues.append(_issue(errors.FAILURE_OUTPUT, f"{path_prefix}.{objects_key}", "not-created failure cannot claim an output object"))
        # output_status describes the failed target operation, not this failure-evidence
        # envelope.  The failure evidence itself may therefore receive an A2 receipt.

    return issues


def _validate(schema_name: str, instance: Any, *, envelope: bool | None) -> ValidationResult:
    if not isinstance(instance, dict):
        return ValidationResult(False, (_issue(errors.SCHEMA_VALUE, "$", "Object must be a JSON object", "admission"),))
    issues = _leakage_issues(instance)
    if issues:
        return ValidationResult(False, tuple(issues))
    if envelope is not None:
        issues = _timestamp_issues(instance, normalised=envelope)
        if issues:
            return ValidationResult(False, tuple(issues))
        issues = _pre_schema_semantics(instance, envelope=envelope)
        if issues:
            return ValidationResult(False, tuple(issues))
    structural = validate_structure(schema_name, instance)
    if structural:
        return ValidationResult(False, tuple(structural))
    if envelope is not None:
        semantic = _semantic_issues(instance, envelope=envelope)
        if semantic:
            return ValidationResult(False, tuple(semantic))
    return ValidationResult(True, ())


def validate_monitoring_event(instance: Any) -> ValidationResult:
    return _validate("monitoring_event", instance, envelope=False)


def validate_envelope(instance: Any) -> ValidationResult:
    return _validate("trust_evidence_envelope", instance, envelope=True)


def validate_curation_result(instance: Any) -> ValidationResult:
    return _validate("curation_result", instance, envelope=None)
