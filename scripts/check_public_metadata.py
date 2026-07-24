#!/usr/bin/env python3
"""Check final v2.2.0 public metadata and exact-version DOI binding."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = "TEA-Sim v2.2.0: Portable audit evidence for health information exchange"
VERSION = "2.2.0"
DOI = "10.5281/zenodo.21533962"
DOI_URL = "https://doi.org/10.5281/zenodo.21533962"
PREVIOUS_DOI = "10.5281/zenodo.21318387"
REPOSITORY = "https://github.com/antonioclim/TEA-Sim-TrustEvidence"
RELEASE_URL = "https://github.com/antonioclim/TEA-Sim-TrustEvidence/releases/tag/v2.2.0"
ASSET_NAME = "TEA-Sim-TrustEvidence-v2.2.0.zip"
ARCHIVE_ROOT = "TEA-Sim-TrustEvidence-v2.2.0"
SHA_NAME = "TEA-Sim-TrustEvidence-v2.2.0.sha256"
ORCID = "0000-0003-4745-0431"
RELEASE_DATE = "2026-07-24"


def cff_value(text: str, key: str) -> str | None:
    """Return a simple top-level scalar from the project's CFF file."""
    prefix = f"{key}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def main() -> int:
    errors: list[str] = []

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    if project["version"] != VERSION:
        errors.append("pyproject version mismatch")
    if project["requires-python"] != ">=3.13,<3.14":
        errors.append("tested Python range mismatch")
    urls = project.get("urls", {})
    if urls.get("Release") != RELEASE_URL or urls.get("DOI") != DOI_URL:
        errors.append("current release URL/DOI mismatch")
    if urls.get("Previous exact release") != "https://doi.org/" + PREVIOUS_DOI:
        errors.append("previous DOI URL mismatch")

    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    release = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    versioning = (ROOT / "docs" / "VERSIONING_AND_CITATION.md").read_text(encoding="utf-8")
    notes = (ROOT / "RELEASE_NOTES_v2.2.0.md").read_text(encoding="utf-8")

    if readme.splitlines()[0].lstrip("# ").strip() != TITLE:
        errors.append("README title mismatch")
    if zenodo.get("title") != TITLE or cff_value(cff, "title") != TITLE:
        errors.append("title mismatch")
    if zenodo.get("version") != VERSION or cff_value(cff, "version") != VERSION:
        errors.append("version mismatch")
    if zenodo.get("publication_date") != RELEASE_DATE or cff_value(cff, "date-released") != RELEASE_DATE:
        errors.append("release date mismatch")
    if cff_value(cff, "doi") != DOI:
        errors.append("CFF DOI mismatch")
    if zenodo.get("creators", [{}])[0].get("orcid") != ORCID or ORCID not in cff:
        errors.append("ORCID mismatch")
    if zenodo.get("access_right") != "open" or zenodo.get("language") != "eng":
        errors.append("Zenodo access/language mismatch")

    relations = zenodo.get("related_identifiers", [])
    predecessors = [item for item in relations if item.get("relation") == "isNewVersionOf"]
    if len(predecessors) != 1 or predecessors[0].get("identifier") != PREVIOUS_DOI:
        errors.append("previous-version relation mismatch")
    if not any(item.get("identifier") == RELEASE_URL for item in relations):
        errors.append("final GitHub release relation missing")

    expected = {
        "schema_version": 2,
        "release_state": "final-release",
        "software_version": VERSION,
        "package_version": VERSION,
        "release_date": RELEASE_DATE,
        "git_tag": "v2.2.0",
        "doi": DOI,
        "doi_url": DOI_URL,
        "doi_state": "exact-version",
        "repository": REPOSITORY,
        "release_url": RELEASE_URL,
        "canonical_asset_name": ASSET_NAME,
        "canonical_archive_root": ARCHIVE_ROOT,
        "canonical_checksum_name": SHA_NAME,
        "previous_version": "2.1.0",
        "previous_version_doi": PREVIOUS_DOI,
        "license": "Apache-2.0",
        "publication_authorised": True,
    }
    for key, value in expected.items():
        if release.get(key) != value:
            errors.append(f"RELEASE_METADATA {key} mismatch")

    combined = "\n".join([readme, cff, json.dumps(zenodo, sort_keys=True), versioning, notes])
    for required in (DOI, DOI_URL, RELEASE_URL, ASSET_NAME, ARCHIVE_ROOT, SHA_NAME):
        if required not in combined:
            errors.append(f"missing final identifier: {required}")
    for forbidden in ("2.2.0-rc.1", "2.2.0rc1", "unassigned-release-candidate", "DRAFT ONLY"):
        if forbidden.lower() in combined.lower():
            errors.append(f"release-candidate residue: {forbidden}")

    if errors:
        print("PUBLIC-METADATA: FAIL")
        print("\n".join(errors))
        return 1

    print(f"PUBLIC-METADATA: PASS ({VERSION}; DOI {DOI})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
