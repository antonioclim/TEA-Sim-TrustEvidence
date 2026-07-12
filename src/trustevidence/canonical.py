"""TE-JCS-1 canonicalisation and strict JSON admission.

RFC 8785 serialisation is delegated to the ``rfc8785`` package.  TE-JCS-1
adds a narrower evidence-object domain: no floating-point values, no unsafe
integers, no duplicate object names and no lone Unicode surrogates.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import rfc8785

SAFE_INTEGER_MAX = 9_007_199_254_740_991
_TIMESTAMP_INPUT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})$")


class CanonicalisationError(ValueError):
    def __init__(self, message: str, *, path: str = "$") -> None:
        super().__init__(f"{message} at {path}")
        self.path = path
        self.detail = message


def _check_string(value: str, path: str) -> None:
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise CanonicalisationError("Lone Unicode surrogate is not admitted", path=path)


def ensure_te_jcs_admissible(value: Any, *, path: str = "$") -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) > SAFE_INTEGER_MAX:
            raise CanonicalisationError("Integer exceeds the I-JSON safe range", path=path)
        return
    if isinstance(value, float):
        raise CanonicalisationError("Floating-point values are outside TE-JCS-1", path=path)
    if isinstance(value, str):
        _check_string(value, path)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            ensure_te_jcs_admissible(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalisationError("JSON object names must be strings", path=path)
            _check_string(key, f"{path}.<name>")
            child = f"{path}.{key}" if path != "$" else f"$.{key}"
            ensure_te_jcs_admissible(item, path=child)
        return
    raise CanonicalisationError(f"Unsupported Python value type: {type(value).__name__}", path=path)


def canonicalise_rfc8785(value: Any) -> bytes:
    try:
        return rfc8785.dumps(value)
    except (rfc8785.CanonicalizationError, UnicodeError, TypeError, ValueError) as exc:
        raise CanonicalisationError(str(exc)) from exc


def canonicalise_te(value: Any) -> bytes:
    ensure_te_jcs_admissible(value)
    return canonicalise_rfc8785(value)


def strict_json_loads(text: str) -> Any:
    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise CanonicalisationError(f"Duplicate JSON property name: {key!r}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise CanonicalisationError(f"Non-JSON numeric constant: {value}")

    try:
        return json.loads(text, object_pairs_hook=pairs_hook, parse_constant=reject_constant)
    except CanonicalisationError:
        raise
    except (json.JSONDecodeError, UnicodeError, ValueError) as exc:
        raise CanonicalisationError(str(exc)) from exc


def canonicalise_json_text(text: str, *, te_profile: bool = False) -> bytes:
    value = strict_json_loads(text)
    return canonicalise_te(value) if te_profile else canonicalise_rfc8785(value)


def normalise_timestamp_ms(value: str) -> str:
    """Convert an offset timestamp to UTC with exact millisecond precision.

    Whole seconds and 1--3 fractional digits are admitted.  Precision finer
    than milliseconds is rejected rather than silently rounded or truncated.
    """

    if not isinstance(value, str):
        raise CanonicalisationError("Timestamp must be a string")
    if not _TIMESTAMP_INPUT.fullmatch(value):
        raise CanonicalisationError("Timestamp must use seconds, at most millisecond precision, and Z or a numeric offset")
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise CanonicalisationError(f"Invalid RFC 3339 timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise CanonicalisationError("Timestamp requires Z or a numeric offset")
    if parsed.microsecond % 1000:
        raise CanonicalisationError("Sub-millisecond timestamp precision is not admitted")
    parsed = parsed.astimezone(timezone.utc)
    milliseconds = parsed.microsecond // 1000
    return parsed.strftime("%Y-%m-%dT%H:%M:%S.") + f"{milliseconds:03d}Z"


def unsigned_core(core: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(core)
    result.pop("emitter_signature", None)
    return result


def unsigned_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(receipt)
    result.pop("receipt_signature", None)
    return result
