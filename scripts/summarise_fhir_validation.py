#!/usr/bin/env python3
"""Summarise official FHIR Validator OperationOutcome files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_outcome(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if value.get("resourceType") != "OperationOutcome":
        raise ValueError(f"{path} is not an OperationOutcome")
    counts = {"fatal": 0, "error": 0, "warning": 0, "information": 0, "success": 0}
    diagnostics: list[dict[str, str]] = []
    for issue in value.get("issue", []):
        severity = str(issue.get("severity", "information"))
        counts[severity] = counts.get(severity, 0) + 1
        diagnostics.append({
            "severity": severity,
            "code": str(issue.get("code", "")),
            "diagnostics": str(issue.get("diagnostics", "")),
            "location": " | ".join(map(str, issue.get("location", []))),
        })
    return {"file": path.name, "counts": counts, "issues": diagnostics}


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
    for item in positive:
        if item["counts"].get("fatal", 0) or item["counts"].get("error", 0):
            failures.append(f"positive has errors: {item['file']}")
    for item in negative:
        if not (item["counts"].get("fatal", 0) or item["counts"].get("error", 0)):
            failures.append(f"negative was accepted: {item['file']}")
    report = {
        "status": "FAIL" if failures else "PASS",
        "positive_count": len(positive),
        "negative_count": len(negative),
        "positive": positive,
        "negative": negative,
        "failures": failures,
        "claim_boundary": "validator results apply only to the exact resources, packages and tool versions recorded by the C3 workflow",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit("FHIR-VALIDATION-SUMMARY: FAIL\n" + "\n".join(failures))
    print(f"FHIR-VALIDATION-SUMMARY: PASS ({len(positive)} positive, {len(negative)} negative)")


if __name__ == "__main__":
    main()
