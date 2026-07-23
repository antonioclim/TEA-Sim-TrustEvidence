"""Schema loading and Draft 2020-12 structural validation."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from . import errors

SCHEMA_FILES = {
    "monitoring_event": "monitoring_event.schema.json",
    "trust_evidence_envelope": "trust_evidence_envelope.schema.json",
    "curation_result": "curation_result.schema.json",
    "hie_disclosure_event": "hie_disclosure_event.schema.json",
    "hie_trust_evidence_envelope": "hie_trust_evidence_envelope.schema.json",
}


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    try:
        filename = SCHEMA_FILES[name]
    except KeyError as exc:
        raise KeyError(f"Unknown schema name: {name}") from exc
    resource = files("trustevidence.schemas").joinpath(filename)
    with resource.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    return schema


@lru_cache(maxsize=None)
def _validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(load_schema(name), format_checker=FormatChecker())


def _path(error: Any) -> str:
    parts = [str(p) for p in error.absolute_path]
    return "$" + ("." + ".".join(parts) if parts else "")


def _classify(error: Any) -> str:
    path = _path(error)
    if error.validator == "required":
        return errors.SCHEMA_REQUIRED
    if error.validator in {"additionalProperties", "unevaluatedProperties"}:
        return errors.SCHEMA_ADDITIONAL
    if error.validator in {"oneOf", "anyOf"}:
        return errors.SCHEMA_BRANCH
    if error.validator in {"format", "pattern"} and any(k in path for k in ("_at", "window_", "period", "started", "ended")):
        return errors.TIMESTAMP_FORMAT
    if "consent_state" in path or "previous_state" in path or "new_state" in path:
        return errors.CONSENT_STATE
    if "sample_count" in path or "missingness_count" in path:
        return errors.AGGREGATION_COUNT
    return errors.SCHEMA_VALUE


def validate_structure(name: str, instance: Any) -> list[errors.ValidationIssue]:
    structural = sorted(
        _validator(name).iter_errors(instance),
        key=lambda e: (len(e.absolute_path), list(map(str, e.absolute_path)), e.message),
    )
    return [
        errors.ValidationIssue(
            code=_classify(error),
            path=_path(error),
            message=error.message,
            layer="json-schema-2020-12",
        )
        for error in structural
    ]
