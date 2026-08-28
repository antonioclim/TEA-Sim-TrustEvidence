#!/usr/bin/env python3
"""Run non-destructive TEA-Sim reproduction checks and retain a structured report."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]


def run_command(command: Sequence[str], runtime_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPYCACHEPREFIX": str(runtime_dir / "pycache"),
            "HYPOTHESIS_STORAGE_DIRECTORY": str(runtime_dir / "hypothesis"),
        },
        check=False,
    )
    return {
        "command": list(command),
        "exit_code": completed.returncode,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "passed": completed.returncode == 0,
    }


def optional_git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def command_plan(mode: str, output_dir: Path) -> list[list[str]]:
    py = sys.executable
    core = [
        [py, "scripts/check_public_metadata.py"],
        [py, "scripts/repository_check.py"],
        [py, "scripts/make_reproducibility_manifest.py", "--check"],
        [py, "scripts/validate_result_contracts.py"],
        [py, "scripts/verify_sha256sums.py", "SHA256SUMS.txt"],
        [py, "scripts/verify_file_manifest.py", "FILE_MANIFEST.tsv"],
        [py, "experiments/run_hie_hero_case.py", "--check"],
        [py, "scripts/check_c3_retained_evidence.py"],
        [py, "experiments/run_hie_security_mutations.py", "--check"],
        [py, "experiments/run_hie_incremental_overhead.py", "--check"],
    ]
    if mode == "core":
        return core
    return [
        [py, "-m", "compileall", "-q", "src", "tests", "property_tests", "experiments", "scripts", "bounded_model"],
        [py, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
        [py, "-m", "pytest", "property_tests", "-q", "-p", "no:cacheprovider"],
        [py, "bounded_model/bounded_model_check.py", "--output-dir", str(output_dir / "bounded_model")],
        *core,
        [py, "experiments/run_cmpb_curation_pipeline.py", "--quick"],
        [py, "scripts/compare_reference_outputs.py"],
    ]


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Independent reproduction execution report",
        "",
        f"- Overall decision: **{report['overall_decision']}**",
        f"- Mode: `{report['mode']}`",
        f"- Started UTC: `{report['started_utc']}`",
        f"- Completed UTC: `{report['completed_utc']}`",
        f"- Repository commit: `{report.get('git_commit') or 'not available'}`",
        f"- Release version: `{report['release_metadata'].get('software_version', 'unknown')}`",
        f"- Python: `{report['environment']['python_version']}`",
        f"- Platform: `{report['environment']['platform']}`",
        "",
        "## Commands",
        "",
    ]
    for index, result in enumerate(report["commands"], start=1):
        status = "PASS" if result["passed"] else "FAIL"
        command = " ".join(result["command"])
        lines.extend(
            [
                f"### {index}. {status}",
                "",
                f"`{command}`",
                "",
                f"- Exit code: `{result['exit_code']}`",
                f"- Elapsed seconds: `{result['elapsed_seconds']}`",
                "",
                "#### Standard output",
                "",
                "```text",
                result["stdout"].rstrip(),
                "```",
                "",
                "#### Standard error",
                "",
                "```text",
                result["stderr"].rstrip(),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "This report establishes only the observed behaviour of the identified software state in the reported environment. It does not establish clinical validity, production readiness, legal compliance, event completeness, backend honesty or global non-equivocation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("core", "full"), default="core")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Report directory. Defaults to results_local/independent_reproduction/<UTC timestamp>.",
    )
    args = parser.parse_args()

    required = (ROOT / "pyproject.toml", ROOT / "RELEASE_METADATA.json")
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        parser.error(f"not a TEA-Sim repository root; missing: {', '.join(missing)}")

    started = datetime.now(timezone.utc)
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = ROOT / "results_local" / "independent_reproduction" / started.strftime("%Y%m%dT%H%M%SZ")
    elif not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=False)

    release_metadata = json.loads((ROOT / "RELEASE_METADATA.json").read_text(encoding="utf-8"))
    runtime_dir = output_dir / "runtime"
    results = [run_command(command, runtime_dir) for command in command_plan(args.mode, output_dir)]
    completed = datetime.now(timezone.utc)

    report: dict[str, Any] = {
        "schema_version": 1,
        "report_type": "independent-reproduction-execution",
        "mode": args.mode,
        "started_utc": started.isoformat(),
        "completed_utc": completed.isoformat(),
        "overall_decision": "PASS" if all(item["passed"] for item in results) else "FAIL",
        "git_commit": optional_git_value("rev-parse", "HEAD"),
        "git_describe": optional_git_value("describe", "--tags", "--always", "--dirty"),
        "release_metadata": release_metadata,
        "environment": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "commands": results,
    }

    json_path = output_dir / "independent_reproduction_report.json"
    md_path = output_dir / "independent_reproduction_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")

    print(f"INDEPENDENT-REPRODUCTION: {report['overall_decision']}")
    print(json_path.relative_to(ROOT))
    print(md_path.relative_to(ROOT))
    return 0 if report["overall_decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
