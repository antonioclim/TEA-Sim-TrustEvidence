"""Validation for the bounded Route C HIE disclosure profile."""

from __future__ import annotations

from typing import Any

from . import errors
from .schema import validate_structure
from .validators import (
    ValidationResult,
    _leakage_issues,
    _semantic_issues,
    _timestamp_issues,
)


_EXPECTED_OBJECTS = {
    "target": "diagnostic-report",
    "consent": "consent-record",
    "policy": "policy-record",
    "decision": "authorisation-decision-record",
    "provenance": "provenance-record",
}


def _issue(code: str, path: str, message: str, layer: str = "hie-semantic") -> errors.ValidationIssue:
    return errors.ValidationIssue(code=code, path=path, message=message, layer=layer)


def _extra_hie_issues(instance: dict[str, Any], *, envelope: bool) -> list[errors.ValidationIssue]:
    core = instance.get("evidence_core", {}) if envelope else instance
    objects_key = "objects" if envelope else "object_contexts"
    objects = core.get(objects_key, []) if isinstance(core, dict) else []
    prefix = "$.evidence_core" if envelope else "$"
    issues: list[errors.ValidationIssue] = []

    if core.get("event_type") != "disclosure-event":
        issues.append(_issue(errors.SCHEMA_VALUE, f"{prefix}.event_type", "HIE profile admits only disclosure-event"))

    roles: dict[str, list[dict[str, Any]]] = {}
    for index, obj in enumerate(objects if isinstance(objects, list) else []):
        if not isinstance(obj, dict):
            continue
        role = str(obj.get("object_role"))
        roles.setdefault(role, []).append(obj)
        expected = _EXPECTED_OBJECTS.get(role)
        if expected is None:
            issues.append(_issue(errors.OBJECT_ROLE, f"{prefix}.{objects_key}[{index}].object_role", f"Unsupported HIE object role: {role}"))
        elif obj.get("resource_class") != expected:
            issues.append(_issue(errors.OBJECT_ROLE, f"{prefix}.{objects_key}[{index}].resource_class", f"Role {role} requires resource class {expected}"))

    for role, expected in _EXPECTED_OBJECTS.items():
        members = roles.get(role, [])
        if len(members) != 1:
            issues.append(_issue(errors.OBJECT_ROLE, f"{prefix}.{objects_key}", f"HIE disclosure requires exactly one {role} object"))
            continue
        if role == "target":
            binding = members[0].get("payload_binding")
            if not isinstance(binding, dict):
                issues.append(_issue(errors.PAYLOAD_BINDING, f"{prefix}.{objects_key}", "DiagnosticReport target requires a payload commitment"))
        elif "payload_binding" in members[0]:
            issues.append(_issue(errors.PAYLOAD_BINDING, f"{prefix}.{objects_key}", f"{role} object must be referenced rather than payload-committed in the base HIE profile"))

    subject = core.get("subject_context", {}) if isinstance(core, dict) else {}
    subject_token = subject.get("subject_ref_token") if isinstance(subject, dict) else None
    target = roles.get("target", [])
    if target and target[0].get("subject_ref_token") != subject_token:
        issues.append(_issue(errors.SUBJECT_CONSISTENCY, f"{prefix}.{objects_key}", "Target subject token must match the envelope subject token"))

    consent = core.get("consent_binding") if envelope else core.get("policy_context", {}).get("consent_binding")
    policy = core.get("policy_binding") if envelope else core.get("policy_context", {}).get("policy_binding")
    if roles.get("consent") and isinstance(consent, dict):
        if roles["consent"][0].get("object_ref_token") != consent.get("consent_ref_token"):
            issues.append(_issue(errors.SCHEMA_VALUE, f"{prefix}.{objects_key}", "Consent object reference differs from consent binding"))
        if roles["consent"][0].get("resource_version_token") != consent.get("consent_version"):
            issues.append(_issue(errors.SCHEMA_VALUE, f"{prefix}.{objects_key}", "Consent object version differs from consent binding"))
    if roles.get("policy") and isinstance(policy, dict):
        if roles["policy"][0].get("object_ref_token") != policy.get("policy_ref_token"):
            issues.append(_issue(errors.SCHEMA_VALUE, f"{prefix}.{objects_key}", "Policy object reference differs from policy binding"))
        if roles["policy"][0].get("resource_version_token") != policy.get("policy_version"):
            issues.append(_issue(errors.SCHEMA_VALUE, f"{prefix}.{objects_key}", "Policy object version differs from policy binding"))

    facts = core.get("event_facts", {}) if isinstance(core, dict) else {}
    if isinstance(facts, dict):
        if facts.get("recipient_ref_token") != "urn:te:org-token:hospital-b":
            issues.append(_issue(errors.SCHEMA_VALUE, f"{prefix}.event_facts.recipient_ref_token", "Frozen hero case recipient must be Hospital B"))
    if core.get("purpose_code") != "treatment":
        issues.append(_issue(errors.SCHEMA_VALUE, f"{prefix}.purpose_code", "Frozen hero case requires treatment purpose"))
    return issues


def _validate_hie(schema_name: str, instance: Any, *, envelope: bool) -> ValidationResult:
    if not isinstance(instance, dict):
        return ValidationResult(False, (_issue(errors.SCHEMA_VALUE, "$", "Object must be a JSON object", "admission"),))
    issues = _leakage_issues(instance)
    if issues:
        return ValidationResult(False, tuple(issues))
    issues = _timestamp_issues(instance, normalised=envelope)
    if issues:
        return ValidationResult(False, tuple(issues))
    structural = validate_structure(schema_name, instance)
    if structural:
        return ValidationResult(False, tuple(structural))
    semantic = _semantic_issues(instance, envelope=envelope)
    semantic.extend(_extra_hie_issues(instance, envelope=envelope))
    if semantic:
        return ValidationResult(False, tuple(semantic))
    return ValidationResult(True, ())


def validate_hie_disclosure_event(instance: Any) -> ValidationResult:
    return _validate_hie("hie_disclosure_event", instance, envelope=False)


def validate_hie_envelope(instance: Any) -> ValidationResult:
    return _validate_hie("hie_trust_evidence_envelope", instance, envelope=True)
