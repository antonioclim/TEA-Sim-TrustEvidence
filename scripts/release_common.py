"""Shared release-tree helpers."""

from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ROOT = "TEA-Sim-TrustEvidence-v2.1.0"
MANIFEST_PATH = "FILE_MANIFEST.tsv"
CHECKSUM_PATH = "SHA256SUMS.txt"
RUNTIME_DIRS = {
    ".git", ".venv", "venv", "results_local", "local_outputs", "__pycache__",
    ".pytest_cache", ".hypothesis", ".mypy_cache", ".ruff_cache", ".tox",
    ".nox", "build", "dist", "htmlcov", "node_modules",
}
RUNTIME_FILES = {".DS_Store", "Thumbs.db", ".coverage"}
RUNTIME_SUFFIXES = {".pyc", ".pyo"}


def is_safe_relative(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts and "\\" not in value


def is_runtime_path(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return (
        any(part in RUNTIME_DIRS or part.endswith(".egg-info") for part in rel.parts)
        or path.name in RUNTIME_FILES
        or path.suffix in RUNTIME_SUFFIXES
    )


def release_files(*, exclude: set[str] | None = None) -> list[Path]:
    excluded = exclude or set()
    return [
        path for path in sorted(ROOT.rglob("*"))
        if path.is_file() and not is_runtime_path(path)
        and path.relative_to(ROOT).as_posix() not in excluded
    ]


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        "cmpb_method": "public method specification",
        "data_examples": "synthetic monitoring example",
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
    if rel.endswith("schema_validation_summary.csv") or rel.endswith("field_deletion_results.csv") or rel.endswith("competency_question_results.csv"):
        return "experiments/run_schema_validation.py"
    if rel.endswith("canonicalisation_determinism.csv") or rel.endswith("canonicalisation_test_run.json"):
        return "experiments/run_canonicalisation_tests.py"
    if rel.endswith("mutation_test_results.csv") or rel.endswith("mutation_test_run.json"):
        return "experiments/run_mutation_tests.py"
    if rel.endswith("workload_passage_summary.csv") or rel.endswith("receipt_size_summary.csv") or rel.endswith("timing_samples.csv") or rel.endswith("workload_events.jsonl") or rel.endswith("hardware_profile.json") or rel.endswith("run_metadata.json"):
        return "experiments/run_workload_passage.py"
    if rel.endswith("property_test_summary.csv") or rel.endswith("property_test_run.json"):
        return "experiments/run_property_checks.py"
    if rel.endswith("bounded_model_summary.csv") or rel.endswith("bounded_model_summary.json") or rel.endswith("bounded_model_observations.csv"):
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
    if rel.startswith("results_expected/cmpb_reference/raw_runs/timing_samples.csv") or rel.endswith("workload_passage_summary.csv") or rel.endswith("hardware_profile.json") or rel.endswith("run_metadata.json"):
        return "measurement-variable"
    if rel.startswith("figures/outputs/"):
        return "frozen-reference-derived"
    if rel.startswith("results_expected/") or rel.startswith("data_examples/") or rel.startswith("figures/sources/"):
        return "byte-deterministic"
    return "source-controlled"
