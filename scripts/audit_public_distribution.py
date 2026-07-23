#!/usr/bin/env python3
"""Audit the curated public distribution for residue and credential patterns."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from release_common import (
    CHECKSUM_PATH,
    MANIFEST_PATH,
    public_excluded,
    public_release_files,
    relative,
)

TEXT_SUFFIXES = {
    "",
    ".md",
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
    ".cff",
    ".ini",
    ".fsh",
    ".py",
    ".sh",
    ".xml",
    ".html",
    ".css",
}
FORBIDDEN_TEXT = {
    "264354984": "submission identifier",
    "Journal of Computer Information Systems": "venue name",
    "A revise decision has been made": "editorial email residue",
    "Reviewer: 1": "reviewer email residue",
}
SECRET_PATTERNS = {
    "GitHub classic token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "PEM private key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "local model path": re.compile(r"(?:/mnt/data/|/home/oai/|C:\\Users\\)", re.I),
}
FIXTURE_DIR = "data_examples/hie_disclosure/private_test_material"
FIXTURE_ALLOWED = {
    f"{FIXTURE_DIR}/README.md",
    f"{FIXTURE_DIR}/payload_commitment_nonce.hex",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    scanned_text_files = 0
    files = public_release_files(exclude={MANIFEST_PATH, CHECKSUM_PATH})
    rels = {relative(path) for path in files}

    for rel in sorted(rels):
        if public_excluded(rel):
            errors.append(f"public exclusion failed: {rel}")
        if rel.startswith(FIXTURE_DIR + "/") and rel not in FIXTURE_ALLOWED:
            errors.append(f"undeclared test-private fixture: {rel}")
        lower_name = Path(rel).name.lower()
        if lower_name.endswith((".eml", ".docx")):
            errors.append(f"submission document in public set: {rel}")
        if any(
            token in lower_name
            for token in ("response_to_review", "reviewer_response", "submission.pdf")
        ):
            errors.append(f"submission residue filename: {rel}")

    if not FIXTURE_ALLOWED.issubset(rels):
        errors.append("declared TEST-ONLY fixture boundary is incomplete")

    for path in files:
        rel = relative(path)
        if rel == "scripts/audit_public_distribution.py":
            continue
        if path.stat().st_size > 5_000_000 or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scanned_text_files += 1
        for token, label in FORBIDDEN_TEXT.items():
            if token.lower() in text.lower():
                errors.append(f"{label}: {rel}")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label}: {rel}")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "distribution_identity": "identified-software-distribution",
        "public_files": len(files) + 2,
        "scanned_text_files": scanned_text_files,
        "excluded_prefixes_enforced": ["docs/route_c/"],
        "test_fixture_allowlist": sorted(FIXTURE_ALLOWED),
        "errors": errors,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if errors:
        print("PUBLIC-DISTRIBUTION-AUDIT: FAIL")
        print("\n".join(errors))
        return 1
    print(
        "PUBLIC-DISTRIBUTION-AUDIT: PASS "
        f"({len(files) + 2} public files; {scanned_text_files} source text files scanned; "
        "identified distribution)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
