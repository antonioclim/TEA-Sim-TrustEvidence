"""Shared release-tree helpers for the v2.2.0 final release."""

from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
TARGET_VERSION = "2.2.0"
PACKAGE_VERSION = "2.2.0"
RELEASE_VERSION = "2.2.0"
RELEASE_TAG = "v2.2.0"
EXPECTED_ROOT = "TEA-Sim-TrustEvidence-v2.2.0"
ASSET_NAME = "TEA-Sim-TrustEvidence-v2.2.0.zip"
ASSET_CHECKSUM_NAME = "TEA-Sim-TrustEvidence-v2.2.0.sha256"
MANIFEST_PATH = "FILE_MANIFEST.tsv"
CHECKSUM_PATH = "SHA256SUMS.txt"

RUNTIME_DIRS = {
    ".git",
    ".venv",
    "venv",
    "results_local",
    "local_outputs",
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
    "node_modules",
}
RUNTIME_FILES = {".DS_Store", "Thumbs.db", ".coverage"}
RUNTIME_SUFFIXES = {".pyc", ".pyo"}

# Route-C governance records and the temporary source-snapshot workflow are
# retained in the development branch but are not part of the identified public
# software distribution supplied to GitHub/Zenodo.
PUBLIC_EXCLUDED_PREFIXES = (PurePosixPath("docs/route_c"),)
PUBLIC_EXCLUDED_PATHS: set[str] = set()


def is_safe_relative(value: str) -> bool:
    """Return True only for safe POSIX-style paths inside an archive root."""

    path = PurePosixPath(value)
    return (
        bool(value)
        and not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
    )


def is_runtime_path(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return (
        any(part in RUNTIME_DIRS or part.endswith(".egg-info") for part in rel.parts)
        or path.name in RUNTIME_FILES
        or path.suffix in RUNTIME_SUFFIXES
    )


def release_files(*, exclude: set[str] | None = None) -> list[Path]:
    """Return all distributed branch files, excluding runtime residue."""

    excluded = exclude or set()
    return [
        path
        for path in sorted(ROOT.rglob("*"))
        if path.is_file()
        and not is_runtime_path(path)
        and path.relative_to(ROOT).as_posix() not in excluded
    ]


def public_excluded(relative_path: str) -> bool:
    """Return whether a branch file is excluded from the public release ZIP."""

    if relative_path in PUBLIC_EXCLUDED_PATHS:
        return True
    posix = PurePosixPath(relative_path)
    return any(posix == prefix or prefix in posix.parents for prefix in PUBLIC_EXCLUDED_PREFIXES)


def public_release_files(*, exclude: set[str] | None = None) -> list[Path]:
    """Return the curated identified public software-distribution files."""

    return [
        path
        for path in release_files(exclude=exclude)
        if not public_excluded(path.relative_to(ROOT).as_posix())
    ]


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def media_type(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def role_for(rel: str) -> str:
    top = rel.split("/", 1)[0]
    mapping = {
        "src": "reference implementation",
        "tests": "unit and regression test",
        "property_tests": "property-based test",
        "bounded_model": "finite bounded executable check",
        "experiments": "experiment driver",
        "results_expected": "retained reference evidence",
        "figures": "figure source, generator or output",
        "tables": "table source, generator or output",
        "cmpb_method": "public method specification",
        "data_examples": "synthetic example",
        "data_sources": "data-source provenance",
        "workloads": "workload descriptor",
        "standards": "standards-facing mapping",
        "schemas": "result contract",
        "scripts": "release and reproducibility utility",
        "docs": "public documentation",
        "environment": "environment disclosure",
    }
    return mapping.get(top, "repository metadata")


def generator_for(rel: str) -> str:
    if rel == "results_expected/cmpb_reference/reproducibility_manifest.csv":
        return "scripts/make_reproducibility_manifest.py"
    if rel.startswith("results_expected/cmpb_reference/c4_hie_security/"):
        return "experiments/run_hie_security_mutations.py"
    if rel.startswith("results_expected/cmpb_reference/c5_hie_overhead/"):
        return "experiments/run_hie_incremental_overhead.py"
    if rel.startswith("schemas/results/"):
        return "source-controlled result contract"
    if rel.startswith("figures/outputs/"):
        return "figures/scripts/generate_cmpb_figures.py"
    if rel.endswith(
        (
            "schema_validation_summary.csv",
            "field_deletion_results.csv",
            "competency_question_results.csv",
        )
    ):
        return "experiments/run_schema_validation.py"
    if rel.endswith(("canonicalisation_determinism.csv", "canonicalisation_test_run.json")):
        return "experiments/run_canonicalisation_tests.py"
    if rel.endswith(("mutation_test_results.csv", "mutation_test_run.json")):
        return "experiments/run_mutation_tests.py"
    if rel.endswith(
        (
            "workload_passage_summary.csv",
            "receipt_size_summary.csv",
            "timing_samples.csv",
            "workload_events.jsonl",
            "hardware_profile.json",
            "run_metadata.json",
        )
    ):
        return "experiments/run_workload_passage.py"
    if rel.endswith(("property_test_summary.csv", "property_test_run.json")):
        return "experiments/run_property_checks.py"
    if rel.endswith(
        (
            "bounded_model_summary.csv",
            "bounded_model_summary.json",
            "bounded_model_observations.csv",
        )
    ):
        return "bounded_model/bounded_model_check.py"
    return "source-controlled"


def sources_for(rel: str) -> str:
    if rel == "results_expected/cmpb_reference/reproducibility_manifest.csv":
        return "all retained result files except this manifest"
    if rel.startswith("results_expected/cmpb_reference/c4_hie_security/"):
        return "retained HIE hero case; Route C security protocol; local A2 verifier"
    if rel.startswith("results_expected/cmpb_reference/c5_hie_overhead/"):
        return "retained HIE hero case; C5 execution plan; B0-B2 experiment driver"
    if rel.startswith("schemas/results/"):
        return "retained result CSV structures"
    if rel.startswith("figures/outputs/"):
        return "figures/sources/*; results_expected/cmpb_reference/*"
    if rel.startswith("results_expected/cmpb_reference/raw_runs/"):
        return "synthetic data_examples; integrated workload protocol"
    if rel.startswith("results_expected/cmpb_reference/"):
        return "source code; synthetic fixtures; declared protocol"
    return ""


def reproducibility_class_for(rel: str) -> str:
    if rel == "results_expected/cmpb_reference/reproducibility_manifest.csv":
        return "byte-deterministic"
    if rel.startswith("schemas/results/"):
        return "source-controlled"
    if rel.startswith("results_expected/cmpb_reference/c5_hie_overhead/"):
        return "measurement-variable"
    if rel.startswith("results_expected/cmpb_reference/raw_runs/timing_samples.csv") or rel.endswith(
        ("workload_passage_summary.csv", "hardware_profile.json", "run_metadata.json")
    ):
        return "measurement-variable"
    if rel.startswith("figures/outputs/"):
        return "frozen-reference-derived"
    if rel.startswith(("results_expected/", "data_examples/", "figures/sources/")):
        return "byte-deterministic"
    return "source-controlled"
