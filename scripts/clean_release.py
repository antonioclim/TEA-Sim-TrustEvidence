#!/usr/bin/env python3
"""Remove generated runtime/build residue without touching retained evidence."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".hypothesis",
    ".mypy_cache",
    ".ruff_cache",
    ".nox",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
}
GENERATED_PATHS = (
    "standards/fhir_ig/output",
    "standards/fhir_ig/temp",
    "standards/fhir_ig/input-cache",
    "standards/fhir_ig/template",
)
FILE_SUFFIXES = {".pyc", ".pyo"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-only", action="store_true")
    parser.add_argument("--include-local-results", action="store_true")
    args = parser.parse_args()
    removed: list[str] = []

    for relative in GENERATED_PATHS:
        path = ROOT / relative
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
            removed.append(relative)

    for path in sorted(ROOT.rglob("*"), reverse=True):
        relative = path.relative_to(ROOT).as_posix()
        if path.is_dir() and (path.name in DIR_NAMES or path.name.endswith(".egg-info")):
            shutil.rmtree(path, ignore_errors=True)
            removed.append(relative)
        elif path.is_file() and path.suffix in FILE_SUFFIXES:
            path.unlink(missing_ok=True)
            removed.append(relative)

    if args.include_local_results:
        for relative in ("results_local", "local_outputs", "figures/local_outputs"):
            path = ROOT / relative
            if path.exists():
                shutil.rmtree(path)
                removed.append(relative)

    print(f"REMOVED: {len(removed)} runtime/build paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
