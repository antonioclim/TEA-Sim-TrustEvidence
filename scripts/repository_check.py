#!/usr/bin/env python3
"""Repository identity and hygiene check for the v2.2.0 final release."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".hypothesis",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    "build",
    "dist",
    "htmlcov",
    "results_local",
    "local_outputs",
    "node_modules",
}
REQUIRED = {
    "pyproject.toml",
    "README.md",
    "LICENSE",
    "CITATION.cff",
    ".zenodo.json",
    "FILE_MANIFEST.tsv",
    "SHA256SUMS.txt",
    "RELEASE_METADATA.json",
    "RELEASE_NOTES_v2.2.0.md",
    "docs/PUBLIC_RELEASE_SCOPE.md",
    "docs/DEPLOYABILITY_AND_COMPONENTS.md",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def ignored(rel: Path) -> bool:
    return (
        any(part in IGNORED_DIRS or part.endswith(".egg-info") for part in rel.parts)
        or rel.suffix in FORBIDDEN_SUFFIXES
        or rel.name in {".DS_Store", "Thumbs.db", ".coverage"}
    )


def main() -> int:
    missing = sorted(path for path in REQUIRED if not (ROOT / path).is_file())
    if missing:
        raise SystemExit("Missing required files: " + ", ".join(missing))

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    if project.get("version") != "2.2.0":
        raise SystemExit("pyproject.toml does not declare version 2.2.0")

    release = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    expected = {
        "release_state": "final-release",
        "software_version": "2.2.0",
        "package_version": "2.2.0",
        "git_tag": "v2.2.0",
        "doi": "10.5281/zenodo.21533962",
        "canonical_asset_name": "TEA-Sim-TrustEvidence-v2.2.0.zip",
        "canonical_archive_root": "TEA-Sim-TrustEvidence-v2.2.0",
        "canonical_checksum_name": "TEA-Sim-TrustEvidence-v2.2.0.sha256",
        "publication_authorised": True,
    }
    for key, value in expected.items():
        if release.get(key) != value:
            raise SystemExit(f"RELEASE_METADATA.json {key} mismatch")

    distributed: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if ignored(rel):
            continue
        distributed.append(path)

    print(
        "REPOSITORY-CHECK: PASS "
        f"({len(distributed)} distributed files; DOI 10.5281/zenodo.21533962)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
