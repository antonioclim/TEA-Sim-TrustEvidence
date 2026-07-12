#!/usr/bin/env python3
"""Check final v2.1.0 title, DOI, release and creator coherence."""

from __future__ import annotations
import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'TEA-Sim v2.1.0: Schema-first curation of personal health monitoring evidence'
DOI = '10.5281/zenodo.21318387'
DOI_URL = 'https://doi.org/10.5281/zenodo.21318387'
PREVIOUS_DOI = '10.5281/zenodo.21226180'
RELEASE_URL = 'https://github.com/antonioclim/TEA-Sim-TrustEvidence/releases/tag/v2.1.0'
RELEASE_DATE = '2026-07-12'
ORCID = '0000-0003-4745-0431'
ASSET_NAME = 'TEA-Sim-TrustEvidence-v2.1.0.zip'
ARCHIVE_ROOT = 'TEA-Sim-TrustEvidence-v2.1.0'
SHA_NAME = 'TEA-Sim-TrustEvidence-v2.1.0.sha256'

def cff_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?([^\n\"']+)", text)
    return match.group(1).strip() if match else None

def main() -> int:
    errors: list[str] = []
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    if project["version"] != "2.1.0": errors.append("pyproject version mismatch")
    if project["requires-python"] != ">=3.13,<3.14": errors.append("tested Python range mismatch")
    if project["name"] != "teasim-trustevidence": errors.append("distribution name mismatch")
    urls = project.get("urls", {})
    if urls.get("Release") != RELEASE_URL: errors.append("pyproject release URL mismatch")
    if urls.get("Archived release") != DOI_URL: errors.append("pyproject DOI URL mismatch")

    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))

    if readme.splitlines()[0].lstrip("# ").strip() != TITLE: errors.append("README title mismatch")
    if zenodo.get("title") != TITLE or cff_value(cff, "title") != TITLE: errors.append("title mismatch")
    if zenodo.get("version") != "2.1.0" or cff_value(cff, "version") != "2.1.0": errors.append("version mismatch")
    if zenodo.get("publication_date") != RELEASE_DATE or cff_value(cff, "date-released") != RELEASE_DATE: errors.append("release date mismatch")
    if zenodo.get("creators", [{}])[0].get("orcid") != ORCID or ORCID not in cff: errors.append("ORCID mismatch")
    if zenodo.get("access_right") != "open" or zenodo.get("language") != "eng": errors.append("Zenodo access/language mismatch")

    relations = zenodo.get("related_identifiers", [])
    predecessor = [x for x in relations if x.get("relation") == "isNewVersionOf"]
    release_links = [x for x in relations if x.get("identifier") == RELEASE_URL]
    if len(predecessor) != 1 or predecessor[0].get("identifier") != PREVIOUS_DOI: errors.append("previous-version relation mismatch")
    if len(release_links) != 1: errors.append("GitHub release relation missing or duplicated")

    expected_release = {
        "software_version": "2.1.0", "release_date": RELEASE_DATE, "git_tag": "v2.1.0",
        "doi": DOI, "doi_url": DOI_URL, "repository": 'https://github.com/antonioclim/TEA-Sim-TrustEvidence',
        "github_release_url": RELEASE_URL, "canonical_asset_name": ASSET_NAME,
        "previous_version_doi": PREVIOUS_DOI, "license": "Apache-2.0",
        "canonical_archive_root": ARCHIVE_ROOT, "canonical_checksum_name": SHA_NAME,
        "doi_state": "exact-version-identifier",
    }
    for key, value in expected_release.items():
        if release.get(key) != value: errors.append(f"RELEASE_METADATA {key} mismatch")

    combined = "\n".join([readme, cff, json.dumps(zenodo, sort_keys=True), changelog,
                              (ROOT / "docs" / "VERSIONING_AND_CITATION.md").read_text(encoding="utf-8")])
    for required in (DOI, DOI_URL, PREVIOUS_DOI, RELEASE_URL, ASSET_NAME, ARCHIVE_ROOT, SHA_NAME):
        if required not in combined: errors.append(f"missing public identifier: {required}")
    forbidden = ["PRE-" + "PUBLICATION", "PRE-" + "DOI", "DO NOT " + "UPLOAD", "no v2.1.0 " + "DOI",
                 "TEA-Sim_v2.1.0_CMPB_" + "GitHub_release_FINAL.zip",
                 "TEA-Sim_v2.1.0_CMPB_" + "Zenodo_deposit_FINAL.zip"]
    for marker in forbidden:
        if marker.lower() in combined.lower(): errors.append(f"stale publication marker: {marker}")
    if (ROOT / ("PRE_" + "PUBLICATION_DO_NOT_UPLOAD.md")).exists(): errors.append("pre-publication barrier file remains")
    if (ROOT / ("PUBLICATION_" + "STATUS.json")).exists(): errors.append("transient publication status file remains")

    if errors:
        print("FAIL")
        print("\n".join(errors))
        return 1
    print(f"PASS: final v2.1.0 metadata coherent (DOI {DOI}; release {RELEASE_URL})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
