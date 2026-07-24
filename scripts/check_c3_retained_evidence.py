#!/usr/bin/env python3
"""Verify the retained Route C C3 evidence without network access."""

from __future__ import annotations

import json
import re
import tarfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data_examples" / "hie_disclosure"
FHIR = ROOT / "standards" / "fhir_ig"
VALIDATION = FHIR / "validation"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return value


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []
    required = [
        CASE / "case_manifest.json",
        CASE / "hie_disclosure_event.json",
        CASE / "signed_envelope_with_receipt.json",
        CASE / "signed_envelope_with_receipt.canonical.json",
        CASE / "verification_report.json",
        CASE / "source" / "source_clinical_bundle.json",
        FHIR / "input" / "resources" / "Bundle-portable-evidence-bundle-hie-001.json",
        FHIR / "input" / "resources" / "Binary-trustevidence-envelope-hie-001.json",
        VALIDATION / "semantic_validation.json",
        VALIDATION / "ig_publisher_summary.json",
        VALIDATION / "validator_summary.json",
        VALIDATION / "ig-publisher-qa.json",
        VALIDATION / "ig-publisher-qa.txt",
        VALIDATION / "ig-publisher.log",
        VALIDATION / "sushi.log",
        VALIDATION / "tool_versions.txt",
        VALIDATION / "tool_sha256.txt",
        VALIDATION / "validator_status.tsv",
        VALIDATION / "org.trustevidence.hie-0.1.0.tgz",
    ]
    for path in required:
        require(
            path.is_file() and path.stat().st_size > 0,
            f"missing or empty: {path.relative_to(ROOT)}",
            failures,
        )

    if failures:
        raise SystemExit("C3-RETAINED-EVIDENCE: FAIL\n" + "\n".join(failures))

    case = load_json(CASE / "case_manifest.json")
    semantic = load_json(VALIDATION / "semantic_validation.json")
    publisher = load_json(VALIDATION / "ig_publisher_summary.json")
    validator = load_json(VALIDATION / "validator_summary.json")
    qa = load_json(VALIDATION / "ig-publisher-qa.json")
    portable = load_json(
        FHIR / "input" / "resources" / "Bundle-portable-evidence-bundle-hie-001.json"
    )

    require(case.get("case_id") == "HIE-DISCLOSURE-001", "unexpected case identifier", failures)
    require(case.get("data_status") == "synthetic", "hero case is not labelled synthetic", failures)
    require(case.get("authorisation_decision") == "D-204", "authorisation decision drift", failures)
    require(case.get("consent_version") == "3", "Consent version drift", failures)
    require(case.get("policy_version") == "6", "policy version drift", failures)
    require(
        case.get("clinical_payload_in_portable_bundle") is False,
        "case manifest claims portable clinical payload",
        failures,
    )

    require(semantic.get("status") == "PASS", "semantic/privacy report is not PASS", failures)
    require(semantic.get("event_schema_accepted") is True, "HIE input schema was not accepted", failures)
    require(semantic.get("envelope_schema_accepted") is True, "HIE envelope schema was not accepted", failures)
    require(
        semantic.get("exact_binary_bytes_preserved") is True,
        "FHIR Binary does not preserve exact envelope bytes",
        failures,
    )
    require(
        not semantic.get("forbidden_portable_resource_types"),
        "forbidden resource type in portable bundle",
        failures,
    )
    require(
        not semantic.get("forbidden_clinical_value_paths"),
        "forbidden clinical value path in portable bundle",
        failures,
    )
    require(
        not semantic.get("unresolved_local_source_reference_paths"),
        "unresolved local source reference remains",
        failures,
    )
    require(
        semantic.get("canonical_envelope_sha256") == case.get("canonical_envelope_sha256"),
        "canonical envelope digest drift",
        failures,
    )

    require(publisher.get("status") == "PASS", "IG Publisher summary is not PASS", failures)
    require(publisher.get("qa_errors") == 0, "IG Publisher QA contains errors", failures)
    require(publisher.get("log_errors") == 0, "IG Publisher log contains errors", failures)
    require(publisher.get("broken_links") == 0, "IG Publisher reports broken links", failures)
    require(
        publisher.get("suppressed_warnings") == 0,
        "IG Publisher warnings were suppressed",
        failures,
    )
    require(
        publisher.get("suppressed_hints") == 0,
        "IG Publisher hints were suppressed",
        failures,
    )
    require(int(qa.get("errs", -1)) == 0, "retained IG Publisher qa.json contains errors", failures)

    require(validator.get("status") == "PASS", "FHIR Validator summary is not PASS", failures)
    require(validator.get("positive_count") == 4, "positive validator corpus count drift", failures)
    require(validator.get("negative_count") == 2, "negative validator corpus count drift", failures)
    for item in validator.get("positive", []):
        counts = item.get("counts", {})
        require(
            not counts.get("fatal") and not counts.get("error"),
            f"positive validator errors: {item.get('file')}",
            failures,
        )
    for item in validator.get("negative", []):
        counts = item.get("counts", {})
        require(
            bool(counts.get("fatal") or counts.get("error")),
            f"negative accepted: {item.get('file')}",
            failures,
        )
        require(
            item.get("expected_failure_observed") is True,
            f"unintended negative failure: {item.get('file')}",
            failures,
        )

    resource_types = [
        entry.get("resource", {}).get("resourceType") for entry in portable.get("entry", [])
    ]
    require("Observation" not in resource_types, "portable bundle contains Observation", failures)
    require(
        "DiagnosticReport" not in resource_types,
        "portable bundle contains DiagnosticReport",
        failures,
    )
    require(resource_types.count("AuditEvent") == 2, "portable bundle AuditEvent count drift", failures)

    tool_versions = (VALIDATION / "tool_versions.txt").read_text(encoding="utf-8")
    for token in (
        "python=Python 3.13",
        "java=openjdk version \"17",
        "sushi=SUSHI v3.20.0",
        "terminology_server=https://tx.fhir.org/r4",
        "validator=FHIR Validation tool Version",
    ):
        require(token in tool_versions, f"tool-version record lacks: {token}", failures)
    checksum_lines = [
        line
        for line in (VALIDATION / "tool_sha256.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    require(len(checksum_lines) == 2, "official-tool checksum count drift", failures)
    for line in checksum_lines:
        require(
            bool(re.fullmatch(r"[0-9a-f]{64}  .+", line)),
            "malformed official-tool checksum line",
            failures,
        )

    status_lines = [
        line
        for line in (VALIDATION / "validator_status.tsv").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    require(len(status_lines) == 6, "validator status row count drift", failures)

    package = VALIDATION / "org.trustevidence.hie-0.1.0.tgz"
    try:
        with tarfile.open(package, "r:gz") as archive:
            names = set(archive.getnames())
        require(
            "package/package.json" in names,
            "retained IG package lacks package/package.json",
            failures,
        )
    except (tarfile.TarError, OSError) as exc:
        failures.append(f"retained IG package is unreadable: {exc}")

    forbidden_relatives = (
        "standards/fhir_ig/output",
        "standards/fhir_ig/temp",
        "standards/fhir_ig/input-cache",
        "standards/fhir_ig/template",
    )
    for relative in forbidden_relatives:
        forbidden_dir = ROOT / relative
        require(
            not forbidden_dir.exists(),
            f"generated site/cache/template retained unexpectedly: {relative}",
            failures,
        )

    manifest = ROOT / "FILE_MANIFEST.tsv"
    if manifest.is_file():
        manifest_paths = {
            line.split("\t", 1)[0]
            for line in manifest.read_text(encoding="utf-8").splitlines()[1:]
            if line.strip()
        }
        for prefix in forbidden_relatives:
            require(
                not any(path == prefix or path.startswith(prefix + "/") for path in manifest_paths),
                f"integrity manifest retains generated path prefix: {prefix}",
                failures,
            )

    if failures:
        raise SystemExit("C3-RETAINED-EVIDENCE: FAIL\n" + "\n".join(failures))
    print(
        "C3-RETAINED-EVIDENCE: PASS "
        f"(4 positive resources, 2 intended negative rejections, "
        f"{publisher.get('qa_warnings')} adjudicated publisher warnings)"
    )


if __name__ == "__main__":
    main()
