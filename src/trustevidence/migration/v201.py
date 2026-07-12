"""Conservative v2.0.1-to-v2.1 event translation.

This adapter never relabels a historical object.  It accepts a caller-
provided mapping only when the complete v2.1 monitoring-event structure is
present and validates it under the current profile.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from ..validators import validate_monitoring_event


class MigrationError(ValueError):
    """Raised when a historical object lacks required v2.1 semantics."""


@dataclass(frozen=True, slots=True)
class V201Inspection:
    recognised: bool
    likely_version: str
    missing_v21_semantics: tuple[str, ...]


def inspect_v201_object(value: dict[str, Any]) -> V201Inspection:
    recognised = isinstance(value, dict) and any(
        key in value for key in ("evidence_version", "trust_evidence", "event_type", "payload_hash")
    )
    required = (
        "source_event_id", "event_type", "occurred_at", "source_boundary",
        "subject_context", "object_contexts", "purpose_code", "outcome",
        "privacy_profile", "event_facts",
    )
    missing = tuple(key for key in required if key not in value)
    return V201Inspection(recognised, "v2.0.1-or-earlier" if recognised else "unknown", missing)


def migrate_v201_event(value: dict[str, Any], *, completed_mapping: dict[str, Any] | None = None) -> dict[str, Any]:
    candidate = deepcopy(completed_mapping if completed_mapping is not None else value)
    result = validate_monitoring_event(candidate)
    if not result.accepted:
        detail = "; ".join(f"{issue.code} at {issue.path}" for issue in result.issues[:4])
        raise MigrationError(
            "Historical object cannot be silently relabelled; provide all v2.1 semantic facts. " + detail
        )
    return candidate
