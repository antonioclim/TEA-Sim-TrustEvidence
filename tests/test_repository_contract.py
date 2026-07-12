from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str, *args: str):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], cwd=ROOT, text=True, capture_output=True, check=False)


def test_public_metadata_and_repository_identity():
    for script in ("check_public_metadata.py", "repository_check.py"):
        result = run(script)
        assert result.returncode == 0, result.stdout + result.stderr


def test_manifest_and_checksum_contracts():
    manifest = run("verify_file_manifest.py", "FILE_MANIFEST.tsv")
    checksums = run("verify_sha256sums.py", "SHA256SUMS.txt")
    assert manifest.returncode == 0, manifest.stdout + manifest.stderr
    assert checksums.returncode == 0, checksums.stdout + checksums.stderr


def test_release_file_filter_excludes_repository_and_runtime_state():
    import importlib.util
    spec = importlib.util.spec_from_file_location("release_common_contract", ROOT / "scripts" / "release_common.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert {".git", ".venv", "results_local", "local_outputs", "__pycache__"} <= module.RUNTIME_DIRS
    assert ".coverage" in module.RUNTIME_FILES
    assert all(".git" not in path.relative_to(ROOT).parts for path in module.release_files())
    assert all(".venv" not in path.relative_to(ROOT).parts for path in module.release_files())
