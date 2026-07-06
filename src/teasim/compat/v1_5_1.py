from __future__ import annotations
import shutil
import subprocess
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def run_v1_5_1(output_dir: Path) -> int:
    """Regenerate the archived v1.5.1 outputs in an isolated copy.

    The shim copies ``legacy/TEA-Sim-v1.5.1`` to ``output_dir`` and runs the
    archived ``run_all.sh`` from that copy. It deliberately does not change the
    v2 TrustEvidence implementation. A successful run should reproduce the v1
    canonical tables, figures and checksum manifest under ``output_dir``.
    """
    root = repo_root()
    source = root / "legacy" / "TEA-Sim-v1.5.1"
    if not source.exists():
        raise FileNotFoundError(f"legacy v1.5.1 tree not found: {source}")
    output_dir = output_dir.resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(source, output_dir)
    script = output_dir / "run_all.sh"
    if not script.exists():
        raise FileNotFoundError(f"run_all.sh not found in copied v1 tree: {script}")
    proc = subprocess.run(["bash", str(script)], cwd=output_dir, text=True)
    return int(proc.returncode)
