#!/usr/bin/env python3
"""Execute RFC 8785 delegation and TE-JCS-1 admission tests."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from copy import deepcopy
from importlib.metadata import version
from pathlib import Path
from typing import Any, Callable

from trustevidence.canonical import (
    CanonicalisationError,
    canonicalise_json_text,
    canonicalise_rfc8785,
    canonicalise_te,
    normalise_timestamp_ms,
    strict_json_loads,
)
from trustevidence.envelope import build_signed_envelope
from trustevidence.hashing import core_digest_hex
from trustevidence.profiles import ENVELOPE_PROFILE
from trustevidence.testing import fixture_emitter_private_key

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results_expected" / "cmpb_reference"
RUN_ID = "cmpb-canonicalisation-001"
ACCESS_EVENT = ROOT / "data_examples" / "personal_monitoring" / "access_event.json"


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def reverse_mapping_order(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: reverse_mapping_order(value[key]) for key in reversed(list(value))}
    if isinstance(value, list):
        return [reverse_mapping_order(item) for item in value]
    return value


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def row(
    case_id: str,
    category: str,
    expected: str,
    observed: str,
    passed: bool,
    *,
    bytes_a: bytes | None = None,
    bytes_b: bytes | None = None,
    error_code: str = "",
    notes: str = "",
) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "case_id": case_id,
        "category": category,
        "expected_relation_or_outcome": expected,
        "observed_relation_or_outcome": observed,
        "passed": str(passed).lower(),
        "sha256_a": digest(bytes_a) if bytes_a is not None else "",
        "sha256_b": digest(bytes_b) if bytes_b is not None else "",
        "canonical_utf8_a": bytes_a.decode("utf-8") if bytes_a is not None else "",
        "canonical_utf8_b": bytes_b.decode("utf-8") if bytes_b is not None else "",
        "error_code": error_code,
        "notes": notes,
    }


def expect_error(case_id: str, category: str, operation: Callable[[], Any], note: str) -> dict[str, Any]:
    try:
        operation()
    except CanonicalisationError as exc:
        return row(
            case_id,
            category,
            "rejected",
            "rejected",
            True,
            error_code="TE-E-CANONICALISATION",
            notes=f"{note}; {exc.detail}",
        )
    return row(case_id, category, "rejected", "accepted", False, notes=note)


def run(output: Path) -> int:
    rows: list[dict[str, Any]] = []

    # RFC 8785 Section 3.2.2 example: exact canonical octets.
    section_object = {
        "numbers": [333333333.33333329, 1e30, 4.50, 2e-3, 1e-27],
        "string": "\u20ac$\u000f\nA'B\"\\\\\"/",
        "literals": [None, True, False],
    }
    expected_section = (
        '{"literals":[null,true,false],"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27],'
        '"string":"€$\\u000f\\nA\'B\\"\\\\\\\\\\"/"}'
    ).encode("utf-8")
    observed_section = canonicalise_rfc8785(section_object)
    rows.append(row(
        "JCS-001", "rfc8785-section-vector", "exact-byte-equality",
        "equal" if observed_section == expected_section else "different",
        observed_section == expected_section,
        bytes_a=expected_section, bytes_b=observed_section,
        notes="RFC 8785 Section 3.2.2 canonical serialisation sample",
    ))

    # Selected RFC 8785 Appendix B IEEE-754 vectors.
    number_vectors = [
        ("0000000000000000", "0", "zero"),
        ("8000000000000000", "0", "minus-zero"),
        ("0000000000000001", "5e-324", "minimum-positive"),
        ("8000000000000001", "-5e-324", "minimum-negative"),
        ("7fefffffffffffff", "1.7976931348623157e+308", "maximum-positive"),
        ("ffefffffffffffff", "-1.7976931348623157e+308", "maximum-negative"),
        ("4340000000000000", "9007199254740992", "two-to-the-53"),
        ("c340000000000000", "-9007199254740992", "minus-two-to-the-53"),
        ("4430000000000000", "295147905179352830000", "approximately-two-to-the-68"),
        ("44b52d02c7e14af5", "9.999999999999997e+22", "below-one-e23"),
        ("44b52d02c7e14af6", "1e+23", "one-e23"),
        ("3eb0c6f7a0b5ed8d", "0.000001", "one-e-minus-six"),
        ("41b3de4355555555", "333333333.3333333", "rounding-sample"),
        ("becbf647612f3696", "-0.0000033333333333333333", "negative-small"),
        ("43143ff3c1cb0959", "1424953923781206.2", "round-to-even"),
    ]
    for index, (bits, expected_text, note) in enumerate(number_vectors, 1):
        value = struct.unpack(">d", bytes.fromhex(bits))[0]
        observed = canonicalise_rfc8785(value)
        expected = expected_text.encode("ascii")
        rows.append(row(
            f"JCS-NUM-{index:02d}", "rfc8785-number-vector", "exact-byte-equality",
            "equal" if observed == expected else "different", observed == expected,
            bytes_a=expected, bytes_b=observed, notes=f"RFC 8785 Appendix B: {note}; bits={bits}",
        ))

    # Representation invariants.
    a = {"z": 3, "a": {"beta": [3, 2, 1], "alpha": True}}
    b = reverse_mapping_order(a)
    ca, cb = canonicalise_te(a), canonicalise_te(b)
    rows.append(row("TEJCS-001", "key-order", "same-bytes-and-digest", "same" if ca == cb else "different", ca == cb, bytes_a=ca, bytes_b=cb, notes="Recursive object-member reordering"))

    wa = canonicalise_json_text('{ "b" : 2, "a" : [1, true, null] }', te_profile=True)
    wb = canonicalise_json_text('{"a":[1,true,null],"b":2}', te_profile=True)
    rows.append(row("TEJCS-002", "whitespace", "same-bytes-and-digest", "same" if wa == wb else "different", wa == wb, bytes_a=wa, bytes_b=wb, notes="Insignificant source whitespace is not emitted"))

    ta = normalise_timestamp_ms("2026-07-01T08:10:00.500+02:00")
    tb = normalise_timestamp_ms("2026-07-01T06:10:00.500Z")
    cta, ctb = canonicalise_te({"t": ta}), canonicalise_te({"t": tb})
    rows.append(row("TEJCS-003", "timestamp-offset", "same-normalised-time", "same" if cta == ctb else "different", cta == ctb, bytes_a=cta, bytes_b=ctb, notes=f"normalised_a={ta}; normalised_b={tb}"))

    whole = normalise_timestamp_ms("2026-07-01T06:10:00Z")
    whole_bytes = canonicalise_te({"t": whole})
    expected_whole = b'{"t":"2026-07-01T06:10:00.000Z"}'
    rows.append(row("TEJCS-004", "timestamp-whole-second", "exact-byte-equality", "equal" if whole_bytes == expected_whole else "different", whole_bytes == expected_whole, bytes_a=expected_whole, bytes_b=whole_bytes, notes="Whole seconds are emitted with explicit millisecond precision"))

    sem_a = canonicalise_te({"role": "authorised-reader", "count": 1})
    sem_b = canonicalise_te({"role": "curation-service", "count": 1})
    rows.append(row("TEJCS-005", "semantic-mutation", "different-bytes-and-digest", "different" if sem_a != sem_b else "same", sem_a != sem_b and digest(sem_a) != digest(sem_b), bytes_a=sem_a, bytes_b=sem_b, notes="A permitted string-field change alters canonical bytes"))

    ns_a = canonicalise_te({"value": 1})
    ns_b = canonicalise_te({"value": "1"})
    rows.append(row("TEJCS-006", "number-string-boundary", "different-bytes-and-digest", "different" if ns_a != ns_b else "same", ns_a != ns_b, bytes_a=ns_a, bytes_b=ns_b, notes="Integer and string representations remain distinct"))

    arr_a = canonicalise_te({"items": ["a", "b"]})
    arr_b = canonicalise_te({"items": ["b", "a"]})
    rows.append(row("TEJCS-007", "array-order", "different-bytes-and-digest", "different" if arr_a != arr_b else "same", arr_a != arr_b, bytes_a=arr_a, bytes_b=arr_b, notes="Array order is semantically retained"))

    composed = canonicalise_rfc8785({"s": "é"})
    decomposed = canonicalise_rfc8785({"s": "e\u0301"})
    rows.append(row("JCS-UNICODE-001", "unicode-preservation", "different-without-normalisation", "different" if composed != decomposed else "same", composed != decomposed, bytes_a=composed, bytes_b=decomposed, notes="JCS preserves supplied Unicode sequences rather than applying NFC"))

    safe_integer = canonicalise_te({"n": 9_007_199_254_740_991})
    rows.append(row("TEJCS-008", "safe-integer-boundary", "accepted", "accepted", bool(safe_integer), bytes_a=safe_integer, notes="Maximum TE-JCS-1 admitted integer"))

    # Strict rejection controls.
    rows.extend([
        expect_error("TEJCS-NEG-001", "duplicate-property", lambda: canonicalise_json_text('{"a":1,"a":2}', te_profile=True), "Duplicate object names are rejected before canonicalisation"),
        expect_error("TEJCS-NEG-002", "nan-token", lambda: canonicalise_json_text('{"x":NaN}', te_profile=True), "Non-JSON NaN token"),
        expect_error("TEJCS-NEG-003", "infinity-token", lambda: canonicalise_json_text('{"x":Infinity}', te_profile=True), "Non-JSON Infinity token"),
        expect_error("TEJCS-NEG-004", "floating-point-profile", lambda: canonicalise_te({"x": 0.1}), "TE-JCS-1 excludes floating-point values even though base JCS serialises them"),
        expect_error("TEJCS-NEG-005", "unsafe-integer", lambda: canonicalise_te({"x": 9_007_199_254_740_992}), "Integer exceeds the TE-JCS-1 I-JSON-safe domain"),
        expect_error("TEJCS-NEG-006", "lone-surrogate", lambda: canonicalise_te({"x": "\ud800"}), "Lone Unicode surrogate"),
        expect_error("TEJCS-NEG-007", "sub-millisecond-time", lambda: normalise_timestamp_ms("2026-07-01T06:10:00.000001Z"), "Precision finer than milliseconds is rejected rather than rounded"),
        expect_error("TEJCS-NEG-008", "naive-time", lambda: normalise_timestamp_ms("2026-07-01T06:10:00.000"), "Timestamp without UTC marker or numeric offset"),
        expect_error("TEJCS-NEG-009", "excess-zero-fraction", lambda: normalise_timestamp_ms("2026-07-01T06:10:00.0000Z"), "A fourth fractional digit is rejected even when it is zero"),
    ])

    # Full evidence-core determinism under source dictionary reordering.
    event = json.loads(ACCESS_EVENT.read_text(encoding="utf-8"))
    reordered = reverse_mapping_order(deepcopy(event))
    env_a, d_a = build_signed_envelope(event, emitted_at="2026-07-01T06:10:00.500Z", private_key=fixture_emitter_private_key())
    env_b, d_b = build_signed_envelope(reordered, emitted_at="2026-07-01T06:10:00.500Z", private_key=fixture_emitter_private_key())
    core_a = canonicalise_te(env_a["evidence_core"])
    core_b = canonicalise_te(env_b["evidence_core"])
    deterministic = core_a == core_b and d_a == d_b and core_digest_hex(env_a["evidence_core"], envelope_profile=ENVELOPE_PROFILE) == d_a
    rows.append(row("TEJCS-009", "full-core-determinism", "same-core-signature-and-digest", "same" if deterministic else "different", deterministic, bytes_a=core_a, bytes_b=core_b, notes="Identical admitted event semantics with reversed dictionary insertion order"))

    rows.sort(key=lambda item: item["case_id"])
    write_csv(output / "canonicalisation_determinism.csv", rows)
    manifest = {
        "run_id": RUN_ID,
        "software_version": "2.1.0",
        "canonicalisation_profile": "TE-JCS-1",
        "delegated_rfc8785_package_version": version("rfc8785"),
        "case_count": len(rows),
        "passed_count": sum(item["passed"] == "true" for item in rows),
        "failed_count": sum(item["passed"] != "true" for item in rows),
        "rfc_number_vectors": len(number_vectors),
        "claim_boundary": "deterministic canonical octets for the admitted TE-JCS-1 domain; no cross-language result beyond the executed vectors",
    }
    dump_json(output / "canonicalisation_test_run.json", manifest)
    return 0 if manifest["failed_count"] == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return run(args.output_dir.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
