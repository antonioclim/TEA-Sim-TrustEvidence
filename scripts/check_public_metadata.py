#!/usr/bin/env python3
"""Check v2.2.0-rc.1 metadata without inventing a DOI or publication."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = "TEA-Sim v2.2.0-rc.1: Portable audit evidence for health information exchange"
PACKAGE_VERSION = "2.2.0rc1"
CANDIDATE_VERSION = "2.2.0-rc.1"
TARGET_VERSION = "2.2.0"
PREVIOUS_DOI = "10.5281/zenodo.21318387"
REPOSITORY = "https://github.com/antonioclim/TEA-Sim-TrustEvidence"
REVIEW_URL = REPOSITORY + "/pull/1"
ASSET_NAME = "TEA-Sim-TrustEvidence-v2.2.0-rc.1.zip"
ARCHIVE_ROOT = "TEA-Sim-TrustEvidence-v2.2.0-rc.1"
SHA_NAME = "TEA-Sim-TrustEvidence-v2.2.0-rc.1.sha256"
ORCID = "0000-0003-4745-0431"


def cff_value(text: str, key: str) -> str | None:
    """Extract a simple top-level scalar from the controlled CFF file."""

    pattern = rf"(?m)^{re.escape(key)}:\s*[\"']?([^\n\"']+)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def main() -> int:
    errors: list[str] = []

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    if project["version"] != PACKAGE_VERSION:
        errors.append("pyproject version mismatch")
    if project["requires-python"] != ">=3.13,<3.14":
        errors.append("tested Python range mismatch")
    if project["name"] != "teasim-trustevidence":
        errors.append("distribution name mismatch")
    urls = project.get("urls", {})
    if urls.get("Release candidate review") != REVIEW_URL:
        errors.append("candidate review URL mismatch")
    if urls.get("Previous exact release") != "https://doi.org/" + PREVIOUS_DOI:
        errors.append("previous DOI URL mismatch")
    if "Release" in urls or "Archived release" in urls:
        errors.append("candidate metadata falsely exposes a current public release")

    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    release = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    versioning = (ROOT / "docs" / "VERSIONING_AND_CITATION.md").read_text(encoding="utf-8")
    notes = (ROOT / "RELEASE_NOTES_v2.2.0-rc.1.md").read_text(encoding="utf-8")

    if readme.splitlines()[0].lstrip("# ").strip() != TITLE:
        errors.append("README title mismatch")
    if zenodo.get("title") != TITLE or cff_value(cff, "title") != TITLE:
        errors.append("title mismatch")
    if (
        zenodo.get("version") != CANDIDATE_VERSION
        or cff_value(cff, "version") != CANDIDATE_VERSION
    ):
        errors.append("candidate version mismatch")
    if "publication_date" in zenodo or cff_value(cff, "date-released") is not None:
        errors.append("unreleased candidate contains a release/publication date")
    if zenodo.get("creators", [{}])[0].get("orcid") != ORCID or ORCID not in cff:
        errors.append("ORCID mismatch")
    if zenodo.get("access_right") != "open" or zenodo.get("language") != "eng":
        errors.append("Zenodo access/language mismatch")

    relations = zenodo.get("related_identifiers", [])
    predecessors = [x for x in relations if x.get("relation") == "isNewVersionOf"]
    if len(predecessors) != 1 or predecessors[0].get("identifier") != PREVIOUS_DOI:
        errors.append("previous-version relation mismatch")
    repository_links = [x for x in relations if x.get("identifier") == REPOSITORY]
    if len(repository_links) != 1:
        errors.append("repository relation missing or duplicated")

    expected = {
        "schema_version": 2,
        "release_state": "release-candidate",
        "software_version": TARGET_VERSION,
        "package_version": PACKAGE_VERSION,
        "candidate_version": CANDIDATE_VERSION,
        "git_tag": "v2.2.0-rc.1",
        "final_git_tag": "v2.2.0",
        "doi": None,
        "doi_url": None,
        "doi_state": "unassigned-release-candidate",
        "repository": REPOSITORY,
        "candidate_review_url": REVIEW_URL,
        "canonical_asset_name": ASSET_NAME,
        "canonical_archive_root": ARCHIVE_ROOT,
        "canonical_checksum_name": SHA_NAME,
        "previous_version": "2.1.0",
        "previous_version_doi": PREVIOUS_DOI,
        "license": "Apache-2.0",
        "publication_authorised": False,
    }
    for key, value in expected.items():
        if release.get(key) != value:
            errors.append(f"RELEASE_METADATA {key} mismatch")

    combined = "\n".join(
        [readme, cff, json.dumps(zenodo, sort_keys=True), versioning, notes]
    )
    for required in (
        PREVIOUS_DOI,
        REVIEW_URL,
        ASSET_NAME,
        ARCHIVE_ROOT,
        SHA_NAME,
        CANDIDATE_VERSION,
    ):
        if required not in combined:
            errors.append(f"missing candidate identifier: {required}")

    # The previous release DOI is expected; a new/current DOI is not. These
    # controlled phrases catch accidental promotion of the candidate.
    forbidden = (
        "Current version DOI:",
        '"publication_authorised": true',
        "DOI assigned to v2.2.0-rc.1",
    )
    for marker in forbidden:
        if marker.lower() in combined.lower():
            errors.append(f"false release marker: {marker}")

    if errors:
        print("PUBLIC-METADATA: FAIL")
        print("\n".join(errors))
        return 1
    print(
        "PUBLIC-METADATA: PASS "
        f"({CANDIDATE_VERSION}; DOI unassigned; previous DOI {PREVIOUS_DOI})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
