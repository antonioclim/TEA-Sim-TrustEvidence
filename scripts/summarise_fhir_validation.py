#!/usr/bin/env python3
"""Summarise official FHIR Validator OperationOutcome files.

Positive examples must contain no fatal or error issues. Negative examples
must not merely fail for an arbitrary reason: each declared negative fixture
has an expected failure family that must be visible in the validator output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_NEGATIVE_FAMILIES = {
    "AuditEvent-privacy-disclosure-missing-recipient.operationoutcome.json": (
        "required BALP recipient agent",
        ("recipient", "minimum required = 2"),
    ),
    "Bundle-portable-evidence-with-clinical-payload.operationoutcome.json": (
        "Observation excluded from the portable evidence Bundle profile",
        ("observation",),
    ),
}


def read_outcome(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if value.get("resourceType") != "OperationOutcome":
        raise ValueError(f"{path} is not an OperationOutcome")
    counts = {"fatal": 0, "error": 0, "warning": 0, "information": 0, "success": 0}
    issues: list[dict[str, str]] = []
    for issue in value.get("issue", []):
        severity = str(issue.get("severity", "information"))
        counts[severity] = counts.get(severity, 0) + 1
        details = issue.get("details") if isinstance(issue.get("details"), dict) else {}
        issues.append(
            {
                "severity": severity,
                "code": str(issue.get("code", "")),
                "details": str(details.get("text", "")),
                "diagnostics": str(issue.get("diagnostics", "")),
                "expression": " | ".join(map(str, issue.get("expression", []))),
                "location": " | ".join(map(str, issue.get("location", []))),
            }
        )
    return {"file": path.name, "counts": counts, "issues": issues}


def expected_negative_observed(item: dict[str, Any]) -> tuple[bool, str]:
    family = EXPECTED_NEGATIVE_FAMILIES.get(item["file"])
    if family is None:
        return False, "no expected failure family registered"
    description, terms = family
    error_text = " ".join(
        " ".join(
            [
                issue.get("details", ""),
                issue.get("diagnostics", ""),
                issue.get("expression", ""),
                issue.get("location", ""),
            ]
        ).lower()
        for issue in item["issues"]
        if issue.get("severity") in {"fatal", "error"}
    )
    observed = any(term.lower() in error_text for term in terms)
    return observed, description


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive-dir", type=Path, required=True)
    parser.add_argument("--negative-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    positive = [read_outcome(path) for path in sorted(args.positive_dir.glob("*.json"))]
    negative = [read_outcome(path) for path in sorted(args.negative_dir.glob("*.json"))]
    failures: list[str] = []
    if not positive:
        failures.append("no positive validator outputs")
    if not negative:
        failures.append("no negative validator outputs")
    if set(EXPECTED_NEGATIVE_FAMILIES) != {item["file"] for item in negative}:
        failures.append("negative corpus differs from the registered expected-failure set")

    for item in positive:
        if item["counts"].get("fatal", 0) or item["counts"].get("error", 0):
            failures.append(f"positive has errors: {item['file']}")

    for item in negative:
        rejected = bool(item["counts"].get("fatal", 0) or item["counts"].get("error", 0))
        observed, description = expected_negative_observed(item)
        item["expected_failure_family"] = description
        item["expected_failure_observed"] = observed
        if not rejected:
            failures.append(f"negative was accepted: {item['file']}")
        elif not observed:
            failures.append(f"negative failed for an unintended reason: {item['file']}")

    report = {
        "status": "FAIL" if failures else "PASS",
        "positive_count": len(positive),
        "negative_count": len(negative),
        "positive": positive,
        "negative": negative,
        "failures": failures,
        "claim_boundary": (
            "validator results apply only to the exact resources, packages, "
            "terminology service and tool versions recorded by the C3 workflow"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if failures:
        raise SystemExit("FHIR-VALIDATION-SUMMARY: FAIL\n" + "\n".join(failures))
    print(
        f"FHIR-VALIDATION-SUMMARY: PASS ({len(positive)} positive, "
        f"{len(negative)} intended negative rejections)"
    )


if __name__ == "__main__":
    main()
