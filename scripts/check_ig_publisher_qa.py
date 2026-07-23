#!/usr/bin/env python3
"""Create a machine-readable gate report from IG Publisher QA output."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SUMMARY = re.compile(
    r"Errors:\s*(?P<errors>\d+),\s*Warnings:\s*(?P<warnings>\d+),\s*"
    r"Info:\s*(?P<info>\d+),\s*Broken Links:\s*(?P<broken>\d+)"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qa", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    qa: dict[str, Any] = json.loads(args.qa.read_text(encoding="utf-8"))
    log_text = args.log.read_text(encoding="utf-8", errors="replace")
    matches = list(SUMMARY.finditer(log_text))
    if not matches:
        raise SystemExit("IG-PUBLISHER-QA: FAIL — final summary was not found")
    final = matches[-1].groupdict()

    report = {
        "status": "PASS",
        "publisher_tool": qa.get("tool"),
        "fhir_version": qa.get("version"),
        "package_id": qa.get("package-id"),
        "ig_version": qa.get("ig-ver"),
        "qa_errors": int(qa.get("errs", -1)),
        "qa_warnings": int(qa.get("warnings", -1)),
        "qa_hints": int(qa.get("hints", -1)),
        "log_errors": int(final["errors"]),
        "log_warnings": int(final["warnings"]),
        "log_information": int(final["info"]),
        "broken_links": int(final["broken"]),
        "suppressed_warnings": int(qa.get("suppressed-warnings", 0)),
        "suppressed_hints": int(qa.get("suppressed-hints", 0)),
        "claim_boundary": (
            "IG Publisher findings apply only to the exact C3 guide source, "
            "dependency set and tool digest recorded by the workflow"
        ),
    }
    failures: list[str] = []
    if report["qa_errors"] != 0:
        failures.append(f"qa errors={report['qa_errors']}")
    if report["log_errors"] != 0:
        failures.append(f"log errors={report['log_errors']}")
    if report["broken_links"] != 0:
        failures.append(f"broken links={report['broken_links']}")
    if report["suppressed_warnings"] != 0 or report["suppressed_hints"] != 0:
        failures.append("suppressed issues are non-zero")
    if failures:
        report["status"] = "FAIL"
        report["failures"] = failures

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if failures:
        raise SystemExit("IG-PUBLISHER-QA: FAIL — " + "; ".join(failures))
    print(
        "IG-PUBLISHER-QA: PASS "
        f"({report['qa_warnings']} warnings, {report['qa_hints']} information, "
        "0 broken links, 0 suppressed issues)"
    )


if __name__ == "__main__":
    main()
