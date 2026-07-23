#!/usr/bin/env python3
"""Rebuild the distributed file manifest and SHA-256 catalogue."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIR_NAMES = {
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
IGNORED_PREFIXES = {
    Path("standards/fhir_ig/output"),
    Path("standards/fhir_ig/temp"),
    Path("standards/fhir_ig/input-cache"),
    Path("standards/fhir_ig/template"),
}
IGNORED_FILE_NAMES = {".DS_Store", "Thumbs.db", ".coverage"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def ignored(relative: Path) -> bool:
    if any(part in IGNORED_DIR_NAMES or part.endswith(".egg-info") for part in relative.parts):
        return True
    if any(relative == prefix or prefix in relative.parents for prefix in IGNORED_PREFIXES):
        return True
    return relative.suffix in IGNORED_SUFFIXES or relative.name in IGNORED_FILE_NAMES


def distributed_files() -> list[Path]:
    return sorted(
        [
            path
            for path in ROOT.rglob("*")
            if path.is_file() and not ignored(path.relative_to(ROOT))
        ],
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def role(relative: str) -> str:
    if relative.startswith("src/"):
        return "source"
    if relative.startswith("tests/") or relative.startswith("property_tests/"):
        return "test"
    if relative.startswith("results_expected/"):
        return "retained_result"
    if relative.startswith("figures/"):
        return "figure"
    if relative.startswith("docs/"):
        return "documentation"
    if relative.startswith("scripts/"):
        return "script"
    return "repository"


def main() -> None:
    files = distributed_files()
    manifest_files = [
        path for path in files if path.name not in {"FILE_MANIFEST.tsv", "SHA256SUMS.txt"}
    ]
    with (ROOT / "FILE_MANIFEST.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["path", "size_bytes", "sha256", "role"],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        for path in manifest_files:
            relative = path.relative_to(ROOT).as_posix()
            writer.writerow(
                {
                    "path": relative,
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "role": role(relative),
                }
            )

    checksum_files = [path for path in distributed_files() if path.name != "SHA256SUMS.txt"]
    (ROOT / "SHA256SUMS.txt").write_text(
        "".join(
            f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}\n"
            for path in checksum_files
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(
        "INTEGRITY-REBUILD: PASS "
        f"({len(manifest_files)} manifest rows; {len(checksum_files)} checksums)"
    )


if __name__ == "__main__":
    main()
