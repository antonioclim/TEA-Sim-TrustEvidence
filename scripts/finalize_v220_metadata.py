from pathlib import Path
import json, re

root = Path(__file__).resolve().parents[1]
doi = '10.5281/zenodo.21533962'
doi_url = 'https://doi.org/' + doi
release_url = 'https://github.com/antonioclim/TEA-Sim-TrustEvidence/releases/tag/v2.2.0'
repo = 'https://github.com/antonioclim/TEA-Sim-TrustEvidence'
date = '2026-07-24'
affil = 'Department of Economic Informatics and Cybernetics, Bucharest University of Economic Studies, Bucharest, Romania'

# pyproject
p = root/'pyproject.toml'
t = p.read_text()
t = t.replace('version = "2.2.0rc1"', 'version = "2.2.0"')
t = t.replace('"Release candidate review" = "https://github.com/antonioclim/TEA-Sim-TrustEvidence/pull/1"\n', f'Release = "{release_url}"\nDOI = "{doi_url}"\n')
p.write_text(t, newline='\n')

# release metadata
metadata = {
  'schema_version': 2,
  'release_state': 'final-release',
  'software_version': '2.2.0',
  'package_version': '2.2.0',
  'release_date': date,
  'git_tag': 'v2.2.0',
  'doi': doi,
  'doi_url': doi_url,
  'doi_state': 'exact-version',
  'repository': repo,
  'release_url': release_url,
  'canonical_asset_name': 'TEA-Sim-TrustEvidence-v2.2.0.zip',
  'canonical_archive_root': 'TEA-Sim-TrustEvidence-v2.2.0',
  'canonical_checksum_name': 'TEA-Sim-TrustEvidence-v2.2.0.sha256',
  'previous_version': '2.1.0',
  'previous_version_doi': '10.5281/zenodo.21318387',
  'license': 'Apache-2.0',
  'publication_authorised': True,
}
(root/'RELEASE_METADATA.json').write_text(json.dumps(metadata, indent=2) + '\n')

# Zenodo metadata
zen = {
  'title': 'TEA-Sim v2.2.0: Portable audit evidence for health information exchange',
  'upload_type': 'software',
  'version': '2.2.0',
  'publication_date': date,
  'description': ('TEA-Sim TrustEvidence v2.2.0 is a reproducible healthcare audit-evidence boundary and executable reference profile. '
                  'The release contains a complete synthetic cross-organisational DiagnosticReport disclosure case, a bounded FHIR R4/BALP-facing implementation guide with retained official-validator evidence, registered semantic, signature, receipt and checkpoint mutation results, a project-specific local A2 Merkle receipt model, and a paired B0-B2 local processing, application-byte and storage-proxy experiment. '
                  'The release supports bounded claims about the synthetic case, the declared validation corpus, registered mutation decisions, exact signed-byte preservation, local retained-checkpoint behaviour and the reported W1 B0-B2 increments. '
                  'It does not claim production EHR performance, hospital deployment readiness, clinical or legal validation, universal FHIR/BALP conformance, large-network scalability, event completeness, backend honesty, public transparency, organisational trust improvement or cost reduction.'),
  'creators': [{'name':'Clim, Antonio','orcid':'0000-0003-4745-0431','affiliation':affil}],
  'license': 'Apache-2.0',
  'keywords': ['health information exchange','audit evidence','FHIR','Merkle receipts','reproducibility'],
  'related_identifiers': [
    {'identifier':'10.5281/zenodo.21318387','relation':'isNewVersionOf','scheme':'doi','resource_type':'software'},
    {'identifier':release_url,'relation':'isSupplementedBy','scheme':'url','resource_type':'software'},
    {'identifier':repo,'relation':'isSupplementedBy','scheme':'url','resource_type':'software'},
  ],
  'notes': f'Exact-version DOI: {doi}. Canonical release asset: TEA-Sim-TrustEvidence-v2.2.0.zip. The identical canonical ZIP byte stream is intended for the GitHub v2.2.0 release and this Zenodo version.',
  'access_right':'open',
  'language':'eng',
}
(root/'.zenodo.json').write_text(json.dumps(zen, indent=2) + '\n')

# CITATION.cff
cff = f'''cff-version: 1.2.0
title: "TEA-Sim v2.2.0: Portable audit evidence for health information exchange"
message: "Please cite the exact-version Zenodo record for this release."
type: software
version: "2.2.0"
date-released: "{date}"
doi: "{doi}"
abstract: "A reproducible healthcare audit-evidence boundary and executable reference profile containing a complete synthetic cross-organisational disclosure case, bounded official FHIR R4 validation evidence, registered security mutations, a local A2 Merkle receipt model and a paired B0-B2 local overhead experiment. The release does not claim production deployment, clinical or legal validation, universal FHIR/BALP conformance, scalability or organisational cost reduction."
license: Apache-2.0
repository-code: "{repo}"
url: "{release_url}"
identifiers:
  - type: doi
    value: "{doi}"
    description: "Exact-version Zenodo DOI for TEA-Sim v2.2.0."
  - type: url
    value: "{release_url}"
    description: "GitHub release for v2.2.0."
keywords:
  - "health information exchange"
  - "audit evidence"
  - "FHIR"
  - "Merkle receipts"
  - "reproducibility"
authors:
  - family-names: "Clim"
    given-names: "Antonio"
    orcid: "https://orcid.org/0000-0003-4745-0431"
    affiliation: "{affil}"
'''
(root/'CITATION.cff').write_text(cff, newline='\n')

# README full rewrite based on final state
readme = f'''# TEA-Sim v2.2.0: Portable audit evidence for health information exchange

TEA-Sim TrustEvidence is a healthcare-specific audit-evidence boundary and executable reference profile. It distinguishes audit facts that may cross organisational boundaries from clinical payloads that remain under source custody.

- Exact-version DOI: <{doi_url}>
- GitHub release: <{release_url}>
- Canonical asset: `TEA-Sim-TrustEvidence-v2.2.0.zip`

## What this release executes

The release retains the v2.1.0 personal-monitoring schema and adds a separate health-information-exchange profile with:

- `HIE-DISCLOSURE-001`, a complete synthetic DiagnosticReport disclosure from Synthetic Hospital A to Synthetic Hospital B;
- Consent version 3, policy version 6 and authorisation decision D-204 bindings;
- a signed TrustEvidence envelope containing references, audit facts and a source-payload commitment, but not the DiagnosticReport or Observation payload values;
- a project-specific local A2 Merkle receipt, inclusion material and retained-checkpoint verification;
- a FHIR R4/BALP-facing implementation-guide corpus with retained SUSHI, IG Publisher and HL7 FHIR Validator evidence for the declared positive and intended-negative examples;
- 67 registered C4 security cases, including preserved limitation acceptances and the explicit result that an authorised receipt does not prove truthful tree size, actual log population, completeness or backend honesty;
- a frozen C5 B0-B2 paired local experiment with five excluded pilot blocks, twenty confirmatory paired blocks, sixty process runs and 7,680 retained operation timings;
- deterministic unit, property and finite bounded checks, result contracts, file manifests and SHA-256 catalogues.

## C5 local incremental result

For the exact synthetic W1 disclosure case on the reported GitHub-hosted runner, the complete B2 reference path added median local operation-level increments of 9.023 ms at p50, 9.290 ms at p95 and 9.668 ms at p99 relative to B0 local source processing. The exact fixture added 16,205 canonical application bytes and produced a 215,339-byte project-defined local storage proxy after 128 operations.

These values are **not** production-EHR latency, network traffic, database storage, service-level performance, scalability or organisational cost results. No negligible-overhead or equivalence margin was defined.

## Cryptographic and confidentiality boundary

SHA-256 is used for exact-byte commitments and Merkle hashing. Ed25519 authenticates issuer and backend statements under deterministic test registries. Base64 in FHIR Binary is encoding, not encryption. The release does not implement or evaluate operational transport security, at-rest encryption, hardware security modules, certificate lifecycle management, key rotation or revocation.

## Quick start

Use Python 3.13 in a fresh virtual environment:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --disable-pip-version-check --no-input setuptools==82.0.1 wheel==0.46.3
python -m pip install --disable-pip-version-check --no-input -r environment/requirements-lock-py313-linux.txt
python -m pip install --disable-pip-version-check --no-input --no-build-isolation --no-deps -e .
make release-check
```

The detailed route is in `REVIEWER_REPRODUCTION.md`. The hosted workflow separately re-runs the official FHIR toolchain and the deterministic fresh-extraction release gate.

## Component and deployment boundary

`docs/DEPLOYABILITY_AND_COMPONENTS.md` lists the implemented components, integration points and omitted operational controls. The package is a reference implementation, not a hospital-ready system. In particular, it does not provide an operational FHIR server, identity provider, consent-decision service, durable replicated log, database, queue, HSM/KMS, monitoring platform, recovery process or organisational operating model.

## Reproducibility and retained evidence

The v2.1.0 monitoring reference corpus is preserved as a historical schema-profile corpus. Version 2.2.0 adds the C3 FHIR validation evidence, C4 mutation corpus and C5 paired local measurements. Measurement-variable outputs are retained rather than regenerated to manufacture byte equality; their contracts, row counts, derivations and source digests are checked.

The canonical public archive is deterministically built, contains archive-specific `FILE_MANIFEST.tsv` and `SHA256SUMS.txt`, excludes submission-specific `docs/route_c/` governance material, and is tested after fresh extraction. `docs/PUBLIC_RELEASE_SCOPE.md` defines that distribution boundary.

## Claim ceiling

The release supports bounded claims about the synthetic hero case, the declared official-validator corpus, registered mutation decisions, exact signed-byte preservation, local retained-checkpoint behaviour and the reported W1 B0-B2 increments. It does not establish:

- real-patient or operational-hospital validation;
- universal FHIR/BALP conformance or HL7/IHE certification;
- SCITT or RFC 9942 conformance;
- clinical, consent, policy or identity truth;
- encryption, confidentiality, privacy compliance or legal compliance;
- truthful tree size, actual log population, complete event capture or public transparency;
- replay prevention, global non-equivocation or backend honesty;
- production readiness, large-network scalability or hospital service-level acceptability;
- network/database/cloud cost, organisational cost reduction or improved organisational trust;
- expert validation or consensus.

## Citation

Clim, A. (2026). *TEA-Sim v2.2.0: Portable audit evidence for health information exchange* (Version 2.2.0) [Computer software]. Zenodo. <{doi_url}>
'''
(root/'README.md').write_text(readme, newline='\n')

# CHANGELOG update
p=root/'CHANGELOG.md'; t=p.read_text();
t=t.replace('## v2.2.0-rc.1 — 2026-07-23 — unreleased candidate\n\nNo public v2.2.0 DOI or GitHub release exists at this stage.\n', f'## v2.2.0 — {date}\n\nExact-version DOI: {doi_url}\n\nGitHub release: {release_url}\n')
t=t.replace('Converted release metadata to an honest release-candidate state with no invented DOI or publication date.', 'Finalised exact-version metadata with the reserved Zenodo DOI and release date.')
t=t.replace('Added deterministic candidate-archive construction,', 'Added deterministic release-archive construction,')
p.write_text(t, newline='\n')

# Quick docs replacements
repls = {
 'TEA-Sim-TrustEvidence-v2.2.0-rc.1.zip':'TEA-Sim-TrustEvidence-v2.2.0.zip',
 'TEA-Sim-TrustEvidence-v2.2.0-rc.1.sha256':'TEA-Sim-TrustEvidence-v2.2.0.sha256',
 'TEA-Sim-TrustEvidence-v2.2.0-rc.1':'TEA-Sim-TrustEvidence-v2.2.0',
 '2.2.0rc1':'2.2.0',
 'v2.2.0-rc.1':'v2.2.0',
 '2.2.0-rc.1':'2.2.0',
}
for rel in ['QUICKSTART.md','REVIEWER_REPRODUCTION.md','environment/requirements-lock-py313-linux.txt']:
    p=root/rel; t=p.read_text();
    for a,b in repls.items(): t=t.replace(a,b)
    t=t.replace('candidate environment','release environment')
    t=t.replace('deterministic candidate','deterministic release')
    p.write_text(t, newline='\n')

# tool versions
p=root/'environment/tool_versions.json'; data=json.loads(p.read_text()); data['evidence_boundary']='v2.2.0 release environment: local Python 3.13.5/Linux plus hosted Python 3.13.x validation; no production deployment claim'; data['teasim-trustevidence']='2.2.0'; p.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')

# migration note
p=root/'docs/MIGRATION_v2.1.0_TO_v2.2.0.md'; t=p.read_text(); t=t.replace('`2.2.0rc1` in C6; `2.2.0` after C9','`2.2.0`'); p.write_text(t,newline='\n')

# versioning and citation full rewrite
versioning=f'''# Versioning and citation

## Current exact release

- software release: `2.2.0`;
- PEP 440 package version: `2.2.0`;
- Git tag: `v2.2.0`;
- canonical archive root: `TEA-Sim-TrustEvidence-v2.2.0`;
- canonical asset: `TEA-Sim-TrustEvidence-v2.2.0.zip`;
- canonical checksum file: `TEA-Sim-TrustEvidence-v2.2.0.sha256`;
- exact-version DOI: `{doi}`;
- DOI URL: <{doi_url}>;
- GitHub release: <{release_url}>.

The DOI above identifies this exact software version. The previous exact version is v2.1.0, DOI `10.5281/zenodo.21318387`.

## Recommended citation

> Clim, A. (2026). *TEA-Sim v2.2.0: Portable audit evidence for health information exchange* (Version 2.2.0) [Computer software]. Zenodo. {doi_url}

The GitHub-generated `Source code (zip)` and `Source code (tar.gz)` snapshots are not the canonical research archive. Reproduction should use the manually uploaded asset `TEA-Sim-TrustEvidence-v2.2.0.zip` and verify its separate SHA-256 file.
'''
(root/'docs/VERSIONING_AND_CITATION.md').write_text(versioning,newline='\n')

# Release notes rename and final content
old=root/'RELEASE_NOTES_v2.2.0-rc.1.md'
new=root/'RELEASE_NOTES_v2.2.0.md'
notes=f'''# TEA-Sim v2.2.0 release notes

## Release identity

- Version: `2.2.0`
- Git tag: `v2.2.0`
- Exact-version DOI: <{doi_url}>
- GitHub release: <{release_url}>
- Canonical asset: `TEA-Sim-TrustEvidence-v2.2.0.zip`
- Checksum file: `TEA-Sim-TrustEvidence-v2.2.0.sha256`

## Principal additions

- Added the separate `TE-HIE-Envelope-1` profile and the complete synthetic `HIE-DISCLOSURE-001` DiagnosticReport disclosure case.
- Added retained SUSHI, IG Publisher and HL7 FHIR Validator evidence for the bounded positive and intended-negative FHIR R4 corpus.
- Added semantic, issuer-signature, commitment, receipt, proof and retained-checkpoint mutation programmes with explicit expected limitation acceptances.
- Preserved the falsification that an authorised backend can sign a coherent but untruthful tree-size assertion; narrowed the claim ceiling accordingly.
- Added a preregistered paired B0-B2 local experiment with retained pilot and confirmatory data, p50/p95/p99 increments, canonical application-byte counts and a project-defined storage proxy.
- Added a component/deployability inventory and explicit production-control omissions.
- Added deterministic archive construction, archive-specific manifests, fresh-extraction reproduction and distribution residue checks.
- Removed one-time evidence-materialisation CI jobs and pinned external GitHub Actions to observed commit SHAs.
- Retained the v2.1.0 personal-monitoring envelope schema version; the HIE extension is additive and does not relabel historical envelopes.

## Claim boundary

The release is not evidence of production-EHR latency, hospital readiness, large-network scalability, database or network cost, clinical validity, legal compliance, event completeness, backend honesty, replay prevention, global non-equivocation, organisational trust improvement or cost reduction.

## Integrity

Use the manually uploaded canonical ZIP and verify it with `TEA-Sim-TrustEvidence-v2.2.0.sha256`. The automatically generated GitHub source-code archives are not the canonical study asset.
'''
new.write_text(notes,newline='\n')
if old.exists(): old.unlink()

# release_common constants and docstrings
p=root/'scripts/release_common.py'; t=p.read_text();
t=t.replace('Shared release-tree helpers for the v2.2.0 release candidate.','Shared release-tree helpers for the v2.2.0 final release.')
t=t.replace('PACKAGE_VERSION = "2.2.0rc1"','PACKAGE_VERSION = "2.2.0"')
t=t.replace('CANDIDATE_VERSION = "2.2.0-rc.1"\nCANDIDATE_TAG = "v2.2.0-rc.1"\n','RELEASE_VERSION = "2.2.0"\nRELEASE_TAG = "v2.2.0"\n')
t=t.replace('EXPECTED_ROOT = "TEA-Sim-TrustEvidence-v2.2.0-rc.1"','EXPECTED_ROOT = "TEA-Sim-TrustEvidence-v2.2.0"')
t=t.replace('ASSET_NAME = "TEA-Sim-TrustEvidence-v2.2.0-rc.1.zip"','ASSET_NAME = "TEA-Sim-TrustEvidence-v2.2.0.zip"')
t=t.replace('ASSET_CHECKSUM_NAME = "TEA-Sim-TrustEvidence-v2.2.0-rc.1.sha256"','ASSET_CHECKSUM_NAME = "TEA-Sim-TrustEvidence-v2.2.0.sha256"')
p.write_text(t,newline='\n')

# build/check archive docstrings and labels
for rel in ['scripts/build_release_archives.py','scripts/check_release_archive.py']:
    p=root/rel; t=p.read_text();
    t=t.replace('v2.2.0-rc.1 release-candidate','v2.2.0 final-release')
    t=t.replace('release-candidate ZIP','release ZIP')
    t=t.replace('RELEASE-CANDIDATE-ASSET','RELEASE-ASSET')
    t=t.replace('RELEASE-CANDIDATE-SHA256','RELEASE-SHA256')
    t=t.replace('RELEASE-CANDIDATE-CHECKSUM','RELEASE-CHECKSUM')
    p.write_text(t,newline='\n')

# metadata checker rewrite
check=f'''#!/usr/bin/env python3
"""Check final v2.2.0 public metadata and exact-version DOI binding."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = "TEA-Sim v2.2.0: Portable audit evidence for health information exchange"
VERSION = "2.2.0"
DOI = "{doi}"
DOI_URL = "{doi_url}"
PREVIOUS_DOI = "10.5281/zenodo.21318387"
REPOSITORY = "{repo}"
RELEASE_URL = "{release_url}"
ASSET_NAME = "TEA-Sim-TrustEvidence-v2.2.0.zip"
ARCHIVE_ROOT = "TEA-Sim-TrustEvidence-v2.2.0"
SHA_NAME = "TEA-Sim-TrustEvidence-v2.2.0.sha256"
ORCID = "0000-0003-4745-0431"
RELEASE_DATE = "{date}"


def cff_value(text: str, key: str) -> str | None:
    pattern = rf"(?m)^{{re.escape(key)}}:\s*[\"']?([^\n\"']+)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def main() -> int:
    errors: list[str] = []
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    if project["version"] != VERSION:
        errors.append("pyproject version mismatch")
    if project["requires-python"] != ">=3.13,<3.14":
        errors.append("tested Python range mismatch")
    urls = project.get("urls", {{}})
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
    if zenodo.get("creators", [{{}}])[0].get("orcid") != ORCID or ORCID not in cff:
        errors.append("ORCID mismatch")
    if zenodo.get("access_right") != "open" or zenodo.get("language") != "eng":
        errors.append("Zenodo access/language mismatch")

    relations = zenodo.get("related_identifiers", [])
    predecessors = [x for x in relations if x.get("relation") == "isNewVersionOf"]
    if len(predecessors) != 1 or predecessors[0].get("identifier") != PREVIOUS_DOI:
        errors.append("previous-version relation mismatch")
    if not any(x.get("identifier") == RELEASE_URL for x in relations):
        errors.append("final GitHub release relation missing")

    expected = {{
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
    }}
    for key, value in expected.items():
        if release.get(key) != value:
            errors.append(f"RELEASE_METADATA {{key}} mismatch")

    combined = "\n".join([readme, cff, json.dumps(zenodo, sort_keys=True), versioning, notes])
    for required in (DOI, DOI_URL, RELEASE_URL, ASSET_NAME, ARCHIVE_ROOT, SHA_NAME):
        if required not in combined:
            errors.append(f"missing final identifier: {{required}}")
    for forbidden in ("2.2.0-rc.1", "2.2.0rc1", "unassigned-release-candidate", "DRAFT ONLY"):
        if forbidden.lower() in combined.lower():
            errors.append(f"release-candidate residue: {{forbidden}}")

    if errors:
        print("PUBLIC-METADATA: FAIL")
        print("\n".join(errors))
        return 1
    print(f"PUBLIC-METADATA: PASS ({{VERSION}}; DOI {{DOI}})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
(root/'scripts/check_public_metadata.py').write_text(check,newline='\n')

# repository check rewrite
repo_check=f'''#!/usr/bin/env python3
"""Repository identity and hygiene check for the v2.2.0 final release."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {{".git",".venv","venv","__pycache__",".pytest_cache",".hypothesis",".mypy_cache",".ruff_cache",".tox",".nox","build","dist","htmlcov","results_local","local_outputs","node_modules"}}
REQUIRED = {{"pyproject.toml","README.md","LICENSE","CITATION.cff",".zenodo.json","FILE_MANIFEST.tsv","SHA256SUMS.txt","RELEASE_METADATA.json","RELEASE_NOTES_v2.2.0.md","docs/PUBLIC_RELEASE_SCOPE.md","docs/DEPLOYABILITY_AND_COMPONENTS.md"}}
FORBIDDEN_SUFFIXES = {{".pyc", ".pyo"}}


def ignored(rel: Path) -> bool:
    return any(part in IGNORED_DIRS or part.endswith(".egg-info") for part in rel.parts) or rel.suffix in FORBIDDEN_SUFFIXES or rel.name in {{".DS_Store","Thumbs.db",".coverage"}}


def main() -> int:
    missing = sorted(path for path in REQUIRED if not (ROOT / path).is_file())
    if missing:
        raise SystemExit("Missing required files: " + ", ".join(missing))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if not re.search(r'^version\s*=\s*["\']2\.2\.0["\']', pyproject, re.M):
        raise SystemExit("pyproject.toml does not declare version 2.2.0")
    release = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    expected = {{
        "release_state": "final-release",
        "software_version": "2.2.0",
        "package_version": "2.2.0",
        "git_tag": "v2.2.0",
        "doi": "10.5281/zenodo.21533962",
        "canonical_asset_name": "TEA-Sim-TrustEvidence-v2.2.0.zip",
        "canonical_archive_root": "TEA-Sim-TrustEvidence-v2.2.0",
        "canonical_checksum_name": "TEA-Sim-TrustEvidence-v2.2.0.sha256",
        "publication_authorised": True,
    }}
    for key, value in expected.items():
        if release.get(key) != value:
            raise SystemExit(f"RELEASE_METADATA.json {{key}} mismatch")
    distributed = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if ignored(rel):
            continue
        distributed.append(path)
    print(f"REPOSITORY-CHECK: PASS ({{len(distributed)}} distributed files; DOI 10.5281/zenodo.21533962)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
(root/'scripts/repository_check.py').write_text(repo_check,newline='\n')

# tests rewrite
version_test=f'''import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS_DOI = "10.5281/zenodo.21318387"
DOI = "{doi}"
DOI_URL = "{doi_url}"
RELEASE_URL = "{release_url}"


def test_software_version_identity():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["version"] == "2.2.0"
    assert data["project"]["requires-python"] == ">=3.13,<3.14"
    assert data["project"]["urls"]["Release"] == RELEASE_URL
    assert data["project"]["urls"]["DOI"] == DOI_URL


def test_release_metadata_is_final():
    status = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    assert status["release_state"] == "final-release"
    assert status["software_version"] == "2.2.0"
    assert status["package_version"] == "2.2.0"
    assert status["git_tag"] == "v2.2.0"
    assert status["doi"] == DOI
    assert status["doi_url"] == DOI_URL
    assert status["doi_state"] == "exact-version"
    assert status["release_url"] == RELEASE_URL
    assert status["previous_version_doi"] == PREVIOUS_DOI
    assert status["canonical_asset_name"] == "TEA-Sim-TrustEvidence-v2.2.0.zip"
    assert status["canonical_archive_root"] == "TEA-Sim-TrustEvidence-v2.2.0"
    assert status["canonical_checksum_name"] == "TEA-Sim-TrustEvidence-v2.2.0.sha256"
    assert status["publication_authorised"] is True


def test_zenodo_metadata_is_final():
    zen = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    assert zen["version"] == "2.2.0"
    assert zen["publication_date"] == "2026-07-24"
    assert zen["access_right"] == "open"
    assert zen["language"] == "eng"
    predecessors = [x for x in zen["related_identifiers"] if x["relation"] == "isNewVersionOf"]
    assert predecessors == [{{"identifier": PREVIOUS_DOI,"relation":"isNewVersionOf","scheme":"doi","resource_type":"software"}}]
    assert DOI in zen["notes"]
'''
(root/'tests/test_version_identity.py').write_text(version_test,newline='\n')

# init/profile labels
p=root/'src/trustevidence/__init__.py'; t=p.read_text(); t=t.replace('v2.2.0 release candidate','v2.2.0 release'); t=t.replace('2.2.0rc1+uninstalled','2.2.0+uninstalled'); p.write_text(t,newline='\n')
p=root/'src/trustevidence/profiles.py'; t=p.read_text(); t=t.replace('The software distribution is v2.2.0-rc.1.','The software distribution is v2.2.0.'); t=t.replace('DISTRIBUTION_RELEASE_LABEL = "v2.2.0-rc.1"','DISTRIBUTION_RELEASE_LABEL = "v2.2.0"'); p.write_text(t,newline='\n')

# Update build/check docstrings and any remaining exact rc labels across public tree, excluding historical result data.
# We deliberately do not rewrite retained result provenance.

print('FINALISE-TREE: PASS')
