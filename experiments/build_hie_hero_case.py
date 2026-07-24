#!/usr/bin/env python3
"""Build the deterministic Route C HIE disclosure hero case."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from trustevidence.canonical import canonicalise_te
from trustevidence.crypto import commit_payload
from trustevidence.hie import (
    HIE_COMMITMENT_CONTEXT,
    HIE_ENVELOPE_PROFILE,
    HIE_MINIMISATION_PROFILE,
    HIE_REPRESENTATION_PROFILE,
    HIE_TOKENISATION_PROFILE,
    attach_hie_fixture_receipt,
    build_hie_fixture_envelope,
    verification_report,
    verify_hie_envelope_receipt,
)
from trustevidence.testing import (
    FIXTURE_BACKEND_ID,
    FIXTURE_BACKEND_KEY_ID,
    FIXTURE_LOG_ID,
    fixture_backend_private_key,
    fixture_emitter_private_key,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data_examples" / "hie_disclosure"
FHIR_RESOURCES = ROOT / "standards" / "fhir_ig" / "input" / "resources"

EMITTED_AT = "2026-07-14T09:30:01.000Z"
OCCURRED_AT = "2026-07-14T09:30:00Z"
NONCE = bytes.fromhex("f6c85e7b72aa0dfdf1860c0f20b9e7836c0a1f5c3c9e1b9ea812272f503b126a")


def _dump(value: Any, *, canonical: bool = False) -> bytes:
    if canonical:
        return canonicalise_te(value)
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _security() -> list[dict[str, str]]:
    return [{"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "HTEST"}]


def source_resources() -> dict[str, dict[str, Any]]:
    patient = {
        "resourceType": "Patient",
        "id": "patient-hie-001",
        "meta": {"security": _security()},
        "identifier": [{"system": "urn:te:token-system:hie-fixture-v1", "value": "subject-hie-001"}],
        "active": True,
    }
    org_a = {
        "resourceType": "Organization",
        "id": "hospital-a",
        "meta": {"security": _security()},
        "identifier": [{"system": "urn:te:organisation-token", "value": "hospital-a"}],
        "active": True,
        "name": "Synthetic Hospital A",
    }
    org_b = {
        "resourceType": "Organization",
        "id": "hospital-b",
        "meta": {"security": _security()},
        "identifier": [{"system": "urn:te:organisation-token", "value": "hospital-b"}],
        "active": True,
        "name": "Synthetic Hospital B",
    }
    device = {
        "resourceType": "Device",
        "id": "evidence-service-a",
        "meta": {"security": _security()},
        "identifier": [{"system": "urn:te:service-token", "value": "evidence-service-a"}],
        "status": "active",
        "type": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/device-kind",
                "code": "application",
                "display": "Application",
            }]
        },
        "owner": {"reference": "Organization/hospital-a"},
    }
    authz = {
        "resourceType": "Device",
        "id": "authorisation-service-a",
        "meta": {"security": _security()},
        "identifier": [{"system": "urn:te:service-token", "value": "authorisation-service-a"}],
        "status": "active",
        "type": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/device-kind",
                "code": "application",
                "display": "Application",
            }]
        },
        "owner": {"reference": "Organization/hospital-a"},
    }
    practitioner = {
        "resourceType": "Practitioner",
        "id": "recipient-role-b",
        "meta": {"security": _security()},
        "identifier": [{"system": "urn:te:actor-token", "value": "authorised-reader-b"}],
        "active": True,
    }
    practitioner_role = {
        "resourceType": "PractitionerRole",
        "id": "authorised-reader-b",
        "meta": {"security": _security()},
        "active": True,
        "practitioner": {"reference": "Practitioner/recipient-role-b"},
        "organization": {"reference": "Organization/hospital-b"},
        "code": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/practitioner-role",
                "code": "doctor",
                "display": "Doctor",
            }]
        }],
    }
    consent = {
        "resourceType": "Consent",
        "id": "consent-hie-001",
        "meta": {"versionId": "3", "lastUpdated": "2026-07-14T09:00:00Z", "security": _security()},
        "status": "active",
        "scope": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/consentscope",
                "code": "patient-privacy",
                "display": "Privacy Consent",
            }]
        },
        "category": [{
            "coding": [{
                "system": "http://loinc.org",
                "code": "59284-0",
                "display": "Patient Consent",
            }]
        }],
        "patient": {"reference": "Patient/patient-hie-001"},
        "dateTime": "2026-07-14T09:00:00Z",
        "performer": [{"reference": "Organization/hospital-a"}],
        "organization": [{"reference": "Organization/hospital-a"}],
        "policy": [{"authority": "urn:te:policy-authority:hospital-a", "uri": "urn:te:policy-token:hie-disclosure"}],
        "provision": {
            "type": "permit",
            "period": {"start": "2026-07-14T09:00:00Z", "end": "2026-12-31T23:59:59Z"},
            "actor": [{
                "role": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                        "code": "IRCP",
                        "display": "information recipient",
                    }]
                },
                "reference": {"reference": "Organization/hospital-b"},
            }],
            "action": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                    "code": "disclose",
                    "display": "Disclose",
                }]
            }],
            "purpose": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                "code": "TREAT",
                "display": "treatment",
            }],
            "data": [{
                "meaning": "instance",
                "reference": {"reference": "DiagnosticReport/diagnostic-report-hie-001/_history/2"},
            }],
        },
    }

    observations = {
        "observation-sodium-hie-001": {
            "resourceType": "Observation",
            "id": "observation-sodium-hie-001",
            "meta": {"versionId": "1", "security": _security()},
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                }]
            }],
            "code": {"coding": [{"system": "http://loinc.org", "code": "2951-2", "display": "Sodium [Moles/volume] in Serum or Plasma"}]},
            "subject": {"reference": "Patient/patient-hie-001"},
            "effectiveDateTime": "2026-07-14T08:45:00Z",
            "performer": [{"reference": "Organization/hospital-a"}],
            "valueQuantity": {"value": 140, "unit": "mmol/L", "system": "http://unitsofmeasure.org", "code": "mmol/L"},
        },
        "observation-potassium-hie-001": {
            "resourceType": "Observation",
            "id": "observation-potassium-hie-001",
            "meta": {"versionId": "1", "security": _security()},
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                }]
            }],
            "code": {"coding": [{"system": "http://loinc.org", "code": "2823-3", "display": "Potassium [Moles/volume] in Serum or Plasma"}]},
            "subject": {"reference": "Patient/patient-hie-001"},
            "effectiveDateTime": "2026-07-14T08:45:00Z",
            "performer": [{"reference": "Organization/hospital-a"}],
            "valueQuantity": {"value": 4.2, "unit": "mmol/L", "system": "http://unitsofmeasure.org", "code": "mmol/L"},
        },
        "observation-creatinine-hie-001": {
            "resourceType": "Observation",
            "id": "observation-creatinine-hie-001",
            "meta": {"versionId": "1", "security": _security()},
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                }]
            }],
            "code": {"coding": [{"system": "http://loinc.org", "code": "2160-0", "display": "Creatinine [Mass/volume] in Serum or Plasma"}]},
            "subject": {"reference": "Patient/patient-hie-001"},
            "effectiveDateTime": "2026-07-14T08:45:00Z",
            "performer": [{"reference": "Organization/hospital-a"}],
            "valueQuantity": {"value": 0.9, "unit": "mg/dL", "system": "http://unitsofmeasure.org", "code": "mg/dL"},
        },
    }
    report = {
        "resourceType": "DiagnosticReport",
        "id": "diagnostic-report-hie-001",
        "meta": {"versionId": "2", "lastUpdated": "2026-07-14T09:15:00Z", "security": _security()},
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                "code": "LAB",
                "display": "Laboratory",
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "24323-8",
                "display": "Comprehensive metabolic 2000 panel - Serum or Plasma",
            }]
        },
        "subject": {"reference": "Patient/patient-hie-001"},
        "effectiveDateTime": "2026-07-14T08:45:00Z",
        "issued": "2026-07-14T09:15:00Z",
        "performer": [{"reference": "Organization/hospital-a"}],
        "result": [{"reference": f"Observation/{key}"} for key in observations],
        "conclusion": "Synthetic results within the declared reference ranges.",
    }
    return {
        "patient-hie-001": patient,
        "hospital-a": org_a,
        "hospital-b": org_b,
        "evidence-service-a": device,
        "authorisation-service-a": authz,
        "recipient-role-b": practitioner,
        "authorised-reader-b": practitioner_role,
        "consent-hie-001": consent,
        **observations,
        "diagnostic-report-hie-001": report,
    }


def source_clinical_bundle(resources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ids = [
        "patient-hie-001",
        "hospital-a",
        "observation-sodium-hie-001",
        "observation-potassium-hie-001",
        "observation-creatinine-hie-001",
        "diagnostic-report-hie-001",
    ]
    return {
        "resourceType": "Bundle",
        "id": "source-clinical-bundle-hie-001",
        "meta": {"security": _security()},
        "type": "collection",
        "timestamp": "2026-07-14T09:15:00Z",
        "entry": [{
            "fullUrl": f"https://synthetic-hospital-a.example/fhir/{resources[item]['resourceType']}/{resources[item]['id']}",
            "resource": resources[item],
        } for item in ids],
    }


def policy_bytes() -> bytes:
    return (
        "Synthetic Hospital A cross-organisational disclosure policy\n"
        "version: 6\n"
        "purpose: treatment\n"
        "recipient: Synthetic Hospital B care team\n"
        "clinical payload remains in the authorised FHIR exchange and is not copied into portable audit evidence\n"
    ).encode("utf-8")


def build_event(payload_commitment: str, policy_digest: str) -> dict[str, Any]:
    return {
        "input_version": "1.0.0",
        "source_event_id": "urn:te:event:hie-disclosure-001",
        "event_type": "disclosure-event",
        "occurred_at": OCCURRED_AT,
        "source_boundary": {
            "source_id": "urn:te:emitter:evidence-service-a",
            "source_role_code": "evidence-service",
            "organisation_ref_token": "urn:te:org-token:hospital-a",
            "key_id": "urn:te:key:fixture-emitter-v1",
            "time_source": {
                "source_id": "urn:te:time-source:hie-fixture-clock",
                "precision_ms": 1,
                "max_skew_ms": 1000,
            },
        },
        "subject_context": {
            "status": "pseudonymous",
            "subject_ref_token": "urn:te:subject-token:hie-001",
            "token_system": "urn:te:token-system:hie-fixture-v1",
            "rotation_scope": "episode",
        },
        "actor_context": {
            "actor_ref_token": "urn:te:actor-token:authorised-reader-b",
            "actor_type": "human-role",
            "role_code": "authorised-reader",
            "organisation_ref_token": "urn:te:org-token:hospital-b",
        },
        "object_contexts": [
            {
                "object_ref_token": "urn:te:fhir-token:diagnostic-report-hie-001-v2",
                "object_role": "target",
                "resource_class": "diagnostic-report",
                "resource_version_token": "2",
                "subject_ref_token": "urn:te:subject-token:hie-001",
                "data_category_code": "laboratory-diagnostic-report",
                "payload_binding": {
                    "commitment_profile": "sha256-nonce-v1",
                    "representation_profile": HIE_REPRESENTATION_PROFILE,
                    "commitment_context": HIE_COMMITMENT_CONTEXT,
                    "commitment": payload_commitment,
                },
            },
            {
                "object_ref_token": "urn:te:consent-token:hie-001",
                "object_role": "consent",
                "resource_class": "consent-record",
                "resource_version_token": "3",
                "data_category_code": "authorisation-context",
            },
            {
                "object_ref_token": "urn:te:policy-token:hie-disclosure",
                "object_role": "policy",
                "resource_class": "policy-record",
                "resource_version_token": "6",
                "data_category_code": "authorisation-context",
            },
            {
                "object_ref_token": "urn:te:decision:D-204",
                "object_role": "decision",
                "resource_class": "authorisation-decision-record",
                "resource_version_token": "1",
                "data_category_code": "authorisation-context",
            },
            {
                "object_ref_token": "urn:te:provenance-token:hie-001",
                "object_role": "provenance",
                "resource_class": "provenance-record",
                "resource_version_token": "1",
                "data_category_code": "provenance-context",
            },
        ],
        "purpose_code": "treatment",
        "outcome": {"code": "success", "reason_code": "consent-permit"},
        "policy_context": {
            "consent_binding": {
                "consent_ref_token": "urn:te:consent-token:hie-001",
                "consent_version": "3",
                "consent_state": "active",
            },
            "policy_binding": {
                "policy_ref_token": "urn:te:policy-token:hie-disclosure",
                "policy_version": "6",
                "policy_digest": policy_digest,
                "policy_source_ref_token": "urn:te:policy-source:hospital-a",
            },
        },
        "privacy_profile": {
            "minimisation_profile": HIE_MINIMISATION_PROFILE,
            "tokenisation_profile": HIE_TOKENISATION_PROFILE,
            "retention_class": "bounded-evaluation",
        },
        "event_facts": {
            "disclosure_channel_code": "secure-transfer",
            "recipient_ref_token": "urn:te:org-token:hospital-b",
            "recipient_role_code": "care-team",
        },
    }


def fhir_projection(
    resources: dict[str, dict[str, Any]],
    envelope_bytes: bytes,
    envelope_digest: str,
    policy_digest: str,
) -> dict[str, dict[str, Any]]:
    patient = resources["patient-hie-001"]
    org_a = resources["hospital-a"]
    org_b = resources["hospital-b"]
    device = resources["evidence-service-a"]
    authz = resources["authorisation-service-a"]
    practitioner = resources["recipient-role-b"]
    practitioner_role = resources["authorised-reader-b"]
    consent = resources["consent-hie-001"]

    auth_event = {
        "resourceType": "AuditEvent",
        "id": "authorisation-decision-hie-001",
        "meta": {
            "profile": ["https://profiles.ihe.net/ITI/BALP/StructureDefinition/IHE.BasicAudit.AuthZconsent"],
            "security": _security(),
        },
        "type": {"system": "http://dicom.nema.org/resources/ontology/DCM", "code": "110113", "display": "Security Alert"},
        "subtype": [{"system": "https://profiles.ihe.net/ITI/BALP/CodeSystem/AuthZsubType", "code": "AuthZ-Consent"}],
        "action": "E",
        "recorded": "2026-07-14T09:29:59.000Z",
        "outcome": "0",
        "agent": [
            {
                "type": {"coding": [{"system": "http://dicom.nema.org/resources/ontology/DCM", "code": "110150"}]},
                "who": {"reference": "Device/evidence-service-a"},
                "requestor": False,
                "network": {"address": "198.51.100.10", "type": "2"},
            },
            {
                "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "code": "IRCP"}]},
                "who": {"reference": "PractitionerRole/authorised-reader-b"},
                "requestor": True,
                "purposeOfUse": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "TREAT"}]}],
            },
            {
                "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-RoleClass", "code": "PROV"}]},
                "who": {"reference": "Organization/hospital-a"},
                "requestor": False,
            },
            {
                "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/extra-security-role-type", "code": "authserver"}]},
                "who": {"reference": "Device/authorisation-service-a"},
                "requestor": False,
            },
        ],
        "source": {
            "site": "synthetic-hospital-a.example",
            "observer": {"reference": "Device/authorisation-service-a"},
            "type": [{"system": "http://terminology.hl7.org/CodeSystem/security-source-type", "code": "6", "display": "Security Server"}],
        },
        "entity": [
            {
                "what": {"reference": "Patient/patient-hie-001"},
                "type": {"system": "http://terminology.hl7.org/CodeSystem/audit-entity-type", "code": "1"},
                "role": {"system": "http://terminology.hl7.org/CodeSystem/object-role", "code": "1", "display": "Patient"},
            },
            {
                "what": {"reference": "Consent/consent-hie-001"},
                "type": {"system": "http://hl7.org/fhir/resource-types", "code": "Consent"},
                "detail": [
                    {"type": "authorisation-decision-id", "valueString": "D-204"},
                    {"type": "policy-version", "valueString": "6"},
                    {"type": "policy-digest", "valueString": policy_digest},
                ],
            },
        ],
    }

    disclosure_event = {
        "resourceType": "AuditEvent",
        "id": "privacy-disclosure-source-hie-001",
        "meta": {
            "profile": ["https://profiles.ihe.net/ITI/BALP/StructureDefinition/IHE.BasicAudit.PrivacyDisclosure.Source"],
            "security": _security(),
        },
        "type": {"system": "http://dicom.nema.org/resources/ontology/DCM", "code": "110106", "display": "Export"},
        "subtype": [
            {"system": "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle", "code": "disclose"},
            {"system": "http://hl7.org/fhir/restful-interaction", "code": "read"},
        ],
        "action": "R",
        "recorded": "2026-07-14T09:30:00.000Z",
        "outcome": "0",
        "purposeOfEvent": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "TREAT"}]}],
        "agent": [
            {
                "type": {"coding": [{"system": "http://dicom.nema.org/resources/ontology/DCM", "code": "110153"}]},
                "who": {"reference": "Device/evidence-service-a"},
                "requestor": False,
                "network": {"address": "synthetic-hospital-a.example", "type": "1"},
            },
            {
                "type": {"coding": [{"system": "http://dicom.nema.org/resources/ontology/DCM", "code": "110152"}]},
                "who": {"reference": "Organization/hospital-b"},
                "requestor": False,
                "network": {"address": "https://synthetic-hospital-b.example/fhir", "type": "5"},
            },
            {
                "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "code": "IRCP"}]},
                "who": {"reference": "PractitionerRole/authorised-reader-b"},
                "requestor": True,
                "purposeOfUse": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "TREAT"}]}],
            },
        ],
        "source": {
            "site": "synthetic-hospital-a.example",
            "observer": {"reference": "Device/evidence-service-a"},
            "type": [{"system": "http://terminology.hl7.org/CodeSystem/security-source-type", "code": "4", "display": "Application Server"}],
        },
        "entity": [
            {
                "what": {"reference": "Patient/patient-hie-001"},
                "type": {"system": "http://terminology.hl7.org/CodeSystem/audit-entity-type", "code": "1"},
                "role": {"system": "http://terminology.hl7.org/CodeSystem/object-role", "code": "1", "display": "Patient"},
            },
            {
                "what": {"reference": "DiagnosticReport/diagnostic-report-hie-001/_history/2"},
                "type": {"system": "http://hl7.org/fhir/resource-types", "code": "DiagnosticReport"},
                "role": {"system": "http://terminology.hl7.org/CodeSystem/object-role", "code": "3", "display": "Report"},
            },
        ],
    }

    provenance = {
        "resourceType": "Provenance",
        "id": "evidence-provenance-hie-001",
        "meta": {
            "profile": ["https://example.org/fhir/trustevidence-hie/StructureDefinition/te-evidence-provenance"],
            "security": _security(),
        },
        "target": [
            {"reference": "AuditEvent/authorisation-decision-hie-001"},
            {"reference": "AuditEvent/privacy-disclosure-source-hie-001"},
            {"reference": "Binary/trustevidence-envelope-hie-001"},
        ],
        "occurredPeriod": {"start": "2026-07-14T09:29:59Z", "end": "2026-07-14T09:30:01Z"},
        "recorded": "2026-07-14T09:30:01Z",
        "agent": [{
            "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type", "code": "assembler"}]},
            "who": {"reference": "Device/evidence-service-a"},
            "onBehalfOf": {"reference": "Organization/hospital-a"},
        }],
        "entity": [{
            "role": "source",
            "what": {"reference": "DiagnosticReport/diagnostic-report-hie-001/_history/2"},
        }],
    }

    binary = {
        "resourceType": "Binary",
        "id": "trustevidence-envelope-hie-001",
        "meta": {
            "profile": ["https://example.org/fhir/trustevidence-hie/StructureDefinition/te-portable-evidence-binary"],
            "security": _security(),
        },
        "contentType": "application/vnd.trustevidence+json",
        "securityContext": {"reference": "Patient/patient-hie-001"},
        "data": base64.b64encode(envelope_bytes).decode("ascii"),
    }
    document_reference = {
        "resourceType": "DocumentReference",
        "id": "trustevidence-document-hie-001",
        "meta": {
            "profile": ["https://example.org/fhir/trustevidence-hie/StructureDefinition/te-evidence-document-reference"],
            "security": _security(),
        },
        "masterIdentifier": {"system": "urn:te:evidence-id", "value": "hie-disclosure-001"},
        "status": "current",
        "type": {
            "coding": [{
                "system": "https://example.org/fhir/trustevidence-hie/CodeSystem/te-evidence-type",
                "code": "portable-audit-evidence",
                "display": "Portable audit evidence",
            }]
        },
        "subject": {"reference": "Patient/patient-hie-001"},
        "date": "2026-07-14T09:30:01Z",
        "author": [{"reference": "Device/evidence-service-a"}],
        "custodian": {"reference": "Organization/hospital-a"},
        "content": [{
            "attachment": {
                "contentType": "application/vnd.trustevidence+json",
                "url": "Binary/trustevidence-envelope-hie-001",
                "hash": base64.b64encode(bytes.fromhex(envelope_digest)).decode("ascii"),
                "title": "Signed TrustEvidence envelope with local A2 receipt",
                "creation": "2026-07-14T09:30:01Z",
            }
        }],
        "context": {
            "related": [
                {"reference": "AuditEvent/authorisation-decision-hie-001"},
                {"reference": "AuditEvent/privacy-disclosure-source-hie-001"},
                {"reference": "Provenance/evidence-provenance-hie-001"},
            ]
        },
    }

    portable = {
        "resourceType": "Bundle",
        "id": "portable-evidence-bundle-hie-001",
        "meta": {
            "profile": ["https://example.org/fhir/trustevidence-hie/StructureDefinition/te-portable-evidence-bundle"],
            "security": _security(),
        },
        "identifier": {"system": "urn:te:evidence-bundle", "value": "hie-disclosure-001"},
        "type": "collection",
        "timestamp": "2026-07-14T09:30:01Z",
        "entry": [],
    }
    portable_items = [
        patient, org_a, org_b, device, authz, practitioner, practitioner_role, consent,
        auth_event, disclosure_event, provenance, binary, document_reference,
    ]
    for item in portable_items:
        portable["entry"].append({
            "fullUrl": f"https://example.org/fhir/{item['resourceType']}/{item['id']}",
            "resource": item,
        })

    return {
        "Patient-patient-hie-001.json": patient,
        "Organization-hospital-a.json": org_a,
        "Organization-hospital-b.json": org_b,
        "Device-evidence-service-a.json": device,
        "Device-authorisation-service-a.json": authz,
        "Practitioner-recipient-role-b.json": practitioner,
        "PractitionerRole-authorised-reader-b.json": practitioner_role,
        "Consent-consent-hie-001.json": consent,
        "AuditEvent-authorisation-decision-hie-001.json": auth_event,
        "AuditEvent-privacy-disclosure-source-hie-001.json": disclosure_event,
        "Provenance-evidence-provenance-hie-001.json": provenance,
        "Binary-trustevidence-envelope-hie-001.json": binary,
        "DocumentReference-trustevidence-document-hie-001.json": document_reference,
        "Bundle-portable-evidence-bundle-hie-001.json": portable,
    }


def build_outputs() -> dict[Path, bytes]:
    resources = source_resources()
    clinical_bundle = source_clinical_bundle(resources)
    clinical_bytes = canonicalise_te(clinical_bundle)
    commitment = commit_payload(
        clinical_bytes,
        nonce=NONCE,
        representation_profile=HIE_REPRESENTATION_PROFILE,
        commitment_context=HIE_COMMITMENT_CONTEXT,
    )
    policy_digest = hashlib.sha256(policy_bytes()).hexdigest()
    event = build_event(commitment, policy_digest)
    envelope = build_hie_fixture_envelope(event, emitted_at=EMITTED_AT)
    receipted, checkpoint = attach_hie_fixture_receipt(envelope)
    emitter_keys = {"urn:te:key:fixture-emitter-v1": fixture_emitter_private_key().public_key()}
    receipt_keys = {FIXTURE_BACKEND_KEY_ID: fixture_backend_private_key().public_key()}
    verification = verify_hie_envelope_receipt(
        receipted,
        emitter_keys=emitter_keys,
        receipt_keys=receipt_keys,
        expected_backend_id=FIXTURE_BACKEND_ID,
        expected_log_id=FIXTURE_LOG_ID,
    )
    if not verification.accepted:
        raise RuntimeError(f"Hero-case receipt verification failed: {verification.codes}")

    envelope_bytes = canonicalise_te(receipted)
    envelope_digest = hashlib.sha256(envelope_bytes).hexdigest()
    fhir = fhir_projection(resources, envelope_bytes, envelope_digest, policy_digest)

    outputs: dict[Path, bytes] = {
        DEFAULT_OUTPUT / "source" / "source_clinical_bundle.json": _dump(clinical_bundle),
        DEFAULT_OUTPUT / "source" / "source_clinical_bundle.canonical.json": clinical_bytes,
        DEFAULT_OUTPUT / "source" / "policy_v6.txt": policy_bytes(),
        DEFAULT_OUTPUT / "private_test_material" / "payload_commitment_nonce.hex": (NONCE.hex() + "\n").encode("ascii"),
        DEFAULT_OUTPUT / "hie_disclosure_event.json": _dump(event),
        DEFAULT_OUTPUT / "signed_envelope.json": _dump(envelope),
        DEFAULT_OUTPUT / "signed_envelope_with_receipt.json": _dump(receipted),
        DEFAULT_OUTPUT / "signed_envelope_with_receipt.canonical.json": envelope_bytes,
        DEFAULT_OUTPUT / "verification_report.json": _dump(verification_report(verification)),
        DEFAULT_OUTPUT / "retained_checkpoint.json": _dump({
            "backend_id": checkpoint.backend_id,
            "log_id": checkpoint.log_id,
            "tree_size": checkpoint.tree_size,
            "root_digest": checkpoint.root_digest,
        }),
        DEFAULT_OUTPUT / "case_manifest.json": _dump({
            "case_id": "HIE-DISCLOSURE-001",
            "data_status": "synthetic",
            "source_resource": "DiagnosticReport/diagnostic-report-hie-001/_history/2",
            "consent_version": "3",
            "policy_version": "6",
            "authorisation_decision": "D-204",
            "purpose": "treatment",
            "envelope_profile": HIE_ENVELOPE_PROFILE,
            "payload_commitment": commitment,
            "policy_digest": policy_digest,
            "canonical_envelope_sha256": envelope_digest,
            "clinical_payload_in_portable_bundle": False,
            "claim_boundary": "technical reference case; not an operational patient exchange",
        }),
    }
    for key, resource in resources.items():
        outputs[DEFAULT_OUTPUT / "source" / f"{resource['resourceType']}-{key}.json"] = _dump(resource)
    for filename, resource in fhir.items():
        outputs[FHIR_RESOURCES / filename] = _dump(resource)

    negative_event = json.loads(json.dumps(event))
    negative_event["object_contexts"] = [
        item for item in negative_event["object_contexts"] if item["object_role"] != "decision"
    ]
    outputs[DEFAULT_OUTPUT / "negative" / "hie_event_missing_decision.json"] = _dump(negative_event)
    leakage_event = json.loads(json.dumps(event))
    leakage_event["raw_payload"] = {"sodium": 140}
    outputs[DEFAULT_OUTPUT / "negative" / "hie_event_payload_leakage.json"] = _dump(leakage_event)

    negative_audit = json.loads(json.dumps(fhir["AuditEvent-privacy-disclosure-source-hie-001.json"]))
    negative_audit["id"] = "privacy-disclosure-source-missing-recipient"
    negative_audit["agent"] = negative_audit["agent"][:1]
    outputs[ROOT / "standards" / "fhir_ig" / "negative" / "AuditEvent-privacy-disclosure-missing-recipient.json"] = _dump(negative_audit)

    negative_bundle = json.loads(json.dumps(fhir["Bundle-portable-evidence-bundle-hie-001.json"]))
    negative_bundle["id"] = "portable-evidence-bundle-with-clinical-payload"
    negative_bundle["entry"].append({
        "fullUrl": "https://example.org/fhir/Observation/observation-sodium-hie-001",
        "resource": resources["observation-sodium-hie-001"],
    })
    outputs[ROOT / "standards" / "fhir_ig" / "negative" / "Bundle-portable-evidence-with-clinical-payload.json"] = _dump(negative_bundle)
    return outputs


def write_outputs(outputs: dict[Path, bytes]) -> None:
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def check_outputs(outputs: dict[Path, bytes]) -> None:
    differences: list[str] = []
    for path, expected in outputs.items():
        if not path.exists():
            differences.append(f"missing: {path.relative_to(ROOT)}")
        elif path.read_bytes() != expected:
            differences.append(f"differs: {path.relative_to(ROOT)}")
    if differences:
        raise SystemExit("HIE hero-case retained outputs are not current:\n" + "\n".join(differences))
    print(f"HIE-HERO-CASE: PASS ({len(outputs)} retained files)")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    if args.write:
        write_outputs(outputs)
        print(f"HIE-HERO-CASE: WROTE {len(outputs)} files")
    else:
        check_outputs(outputs)


if __name__ == "__main__":
    main()
