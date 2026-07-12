#!/usr/bin/env python3
"""Repository identity and hygiene check that works in ZIPs and ordinary Git clones."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {'.git','.venv','venv','__pycache__','.pytest_cache','.hypothesis','.mypy_cache','.ruff_cache','.tox','.nox','build','dist','htmlcov','results_local','local_outputs','node_modules'}
REQUIRED = {'pyproject.toml','README.md','LICENSE','CITATION.cff','.zenodo.json','FILE_MANIFEST.tsv','SHA256SUMS.txt','RELEASE_METADATA.json'}
FORBIDDEN_SUFFIXES = {'.pyc','.pyo'}


def ignored(rel: Path) -> bool:
    return any(part in IGNORED_DIRS or part.endswith('.egg-info') for part in rel.parts) or rel.suffix in FORBIDDEN_SUFFIXES or rel.name in {'.DS_Store','Thumbs.db','.coverage'}

missing = sorted(p for p in REQUIRED if not (ROOT/p).is_file())
if missing:
    raise SystemExit('Missing required files: ' + ', '.join(missing))
pyproject = (ROOT/'pyproject.toml').read_text(encoding='utf-8')
if not re.search(r'^version\s*=\s*["\']2\.1\.0["\']', pyproject, re.M):
    raise SystemExit('pyproject.toml does not declare version 2.1.0')
release_path = ROOT/'RELEASE_METADATA.json'
release = json.loads(release_path.read_text(encoding='utf-8'))
expected = {
    'software_version': '2.1.0',
    'git_tag': 'v2.1.0',
    'doi': '10.5281/zenodo.21318387',
    'canonical_asset_name': 'TEA-Sim-TrustEvidence-v2.1.0.zip',
    'canonical_archive_root': 'TEA-Sim-TrustEvidence-v2.1.0',
    'canonical_checksum_name': 'TEA-Sim-TrustEvidence-v2.1.0.sha256',
}
for key, value in expected.items():
    if release.get(key) != value:
        raise SystemExit(f'RELEASE_METADATA.json {key} mismatch')
for p in ROOT.rglob('*'):
    if not p.is_file():
        continue
    rel = p.relative_to(ROOT)
    if ignored(rel):
        continue
    if rel.suffix in FORBIDDEN_SUFFIXES:
        raise SystemExit(f'Compiled residue: {rel.as_posix()}')
print(f'REPOSITORY-CHECK: PASS ({sum(1 for p in ROOT.rglob("*") if p.is_file() and not ignored(p.relative_to(ROOT)))} distributed files; root name independent)')
