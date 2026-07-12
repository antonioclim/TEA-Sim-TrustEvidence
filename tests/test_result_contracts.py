from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_retained_csv_results_satisfy_public_contracts() -> None:
    result = run_script("scripts/validate_result_contracts.py")
    assert result.returncode == 0, result.stdout
    assert "PASS:" in result.stdout


def test_reproducibility_manifest_is_current() -> None:
    result = run_script("scripts/make_reproducibility_manifest.py", "--check")
    assert result.returncode == 0, result.stdout
    assert "PASS:" in result.stdout


def test_property_run_record_reports_success() -> None:
    import json

    record = json.loads(
        (ROOT / "results_expected/cmpb_reference/property_test_run.json").read_text(encoding="utf-8")
    )
    assert record["unit_test_exit_code"] == 0
    assert record["property_test_exit_code"] == 0
    assert record["bounded_model_exit_code"] == 0
    assert record["unit_tests_passed"] > 0
    assert record["property_tests_passed"] == 8
    assert record["reported_property_passing_examples"] == record["declared_property_examples"]
    assert record["reported_property_failing_examples"] == 0
    assert record["bounded_failures"] == 0
