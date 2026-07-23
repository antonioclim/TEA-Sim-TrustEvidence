#!/usr/bin/env python3
"""Execute the Route C HIE hero case with validation-admissible fixtures.

The v2.1 personal-monitoring profile deliberately excludes Python floating-
point values from TE-JCS-1. Route C therefore uses clinically plausible
integer-valued synthetic laboratory results for deterministic commitment
bytes. The wrapper also keeps source clinical resources under source custody:
FHIR audit artefacts carry a versioned identifier rather than an unresolved
relative reference, while the exact signed TrustEvidence bytes use the
standard ``application/json`` media type.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments import build_hie_hero_case as implementation  # noqa: E402

DEFAULT_OUTPUT = implementation.DEFAULT_OUTPUT
FHIR_RESOURCES = implementation.FHIR_RESOURCES
HIE_COMMITMENT_CONTEXT = implementation.HIE_COMMITMENT_CONTEXT
HIE_REPRESENTATION_PROFILE = implementation.HIE_REPRESENTATION_PROFILE
NONCE = implementation.NONCE

_SOURCE_REFERENCE = "DiagnosticReport/diagnostic-report-hie-001/_history/2"
_SOURCE_IDENTIFIER_SYSTEM = (
    "https://example.org/fhir/trustevidence-hie/identifier/source-resource"
)

_original_source_resources = implementation.source_resources
_original_fhir_projection = implementation.fhir_projection


def _narrative(label: str) -> dict[str, str]:
    """Return a minimal, payload-free generated narrative."""

    safe = (
        label.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return {
        "status": "generated",
        "div": f'<div xmlns="http://www.w3.org/1999/xhtml">{safe}</div>',
    }


def _source_identifier_reference() -> dict[str, Any]:
    return {
        "type": "DiagnosticReport",
        "identifier": {
            "system": _SOURCE_IDENTIFIER_SYSTEM,
            "value": _SOURCE_REFERENCE,
        },
        "display": "Synthetic DiagnosticReport version 2 retained by Hospital A",
    }


def _replace_source_reference(value: Any) -> None:
    """Replace unresolved local source-resource links with identifier references."""

    if isinstance(value, dict):
        if value.get("reference") == _SOURCE_REFERENCE:
            value.clear()
            value.update(_source_identifier_reference())
            return
        for child in value.values():
            _replace_source_reference(child)
    elif isinstance(value, list):
        for child in value:
            _replace_source_reference(child)


def _replace_media_type(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if key == "contentType" and child == "application/vnd.trustevidence+json":
                value[key] = "application/json"
            else:
                _replace_media_type(child)
    elif isinstance(value, list):
        for child in value:
            _replace_media_type(child)


def _add_payload_free_narratives(value: Any) -> None:
    """Add concise narratives without copying clinical values into portable data."""

    if isinstance(value, dict):
        resource_type = value.get("resourceType")
        if isinstance(resource_type, str) and resource_type not in {"Binary", "Bundle"}:
            value.setdefault("text", _narrative(f"Synthetic {resource_type} reference artefact."))
        for child in value.values():
            _add_payload_free_narratives(child)
    elif isinstance(value, list):
        for child in value:
            _add_payload_free_narratives(child)


def source_resources() -> dict[str, dict[str, Any]]:
    resources = _original_source_resources()
    resources["observation-potassium-hie-001"]["valueQuantity"]["value"] = 4
    resources["observation-creatinine-hie-001"]["valueQuantity"]["value"] = 1

    # Device.type is optional in FHIR R4. The former device-kind coding used a
    # non-existent canonical CodeSystem and therefore produced official
    # validator errors. Identifiers and ownership retain the needed semantics.
    for resource_id in ("evidence-service-a", "authorisation-service-a"):
        resources[resource_id].pop("type", None)

    _replace_source_reference(resources)
    _add_payload_free_narratives(resources)
    return resources


def fhir_projection(
    resources: dict[str, dict[str, Any]],
    envelope_bytes: bytes,
    envelope_digest: str,
    policy_digest: str,
) -> dict[str, dict[str, Any]]:
    projection = _original_fhir_projection(
        resources,
        envelope_bytes,
        envelope_digest,
        policy_digest,
    )
    _replace_source_reference(projection)
    _replace_media_type(projection)
    _add_payload_free_narratives(projection)
    return projection


implementation.source_resources = source_resources
implementation.fhir_projection = fhir_projection
build_outputs = implementation.build_outputs
write_outputs = implementation.write_outputs
check_outputs = implementation.check_outputs


def main() -> None:
    implementation.main()


if __name__ == "__main__":
    main()
