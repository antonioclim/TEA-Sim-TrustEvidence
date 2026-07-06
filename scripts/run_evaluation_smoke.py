#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
checks = []

def run(label, cmd, cwd):
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, env={**__import__('os').environ, 'PYTHONPATH':'src', 'PYTHONDONTWRITEBYTECODE':'1', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1'})
    status = 'PASS' if proc.returncode == 0 else 'FAIL'
    print(f'{label}: {status}')
    if proc.stdout.strip(): print(proc.stdout.strip().splitlines()[-1])
    if proc.returncode != 0 and proc.stderr.strip(): print(proc.stderr.strip())
    checks.append((label,status))

def exists(label, rel):
    status='PASS' if (ROOT/rel).exists() else 'FAIL'
    print(f'{label}: {status} - {rel}')
    checks.append((label,status))

exists('fhir_validation_matrix','evaluation_workstreams/01_fhir_balp_validation/VALIDATION_MATRIX.csv')
exists('backend_execution_report','evaluation_workstreams/02_real_backends/BACKEND_EXECUTION_REPORT.md')
exists('workload_calibration_report','evaluation_workstreams/03_workload_calibration/CALIBRATION_REPORT.md')
exists('formal_property_results','evaluation_workstreams/04_formal_property_validation/FORMAL_PROPERTY_RESULTS.md')
exists('expert_protocol','protocols/05_expert_validation_protocol/EXPERT_VALIDATION_PROTOCOL_ONLY.md')
# Run lightweight executable checks where paths are available.
fhir_lint = ROOT/'evaluation_workstreams/01_fhir_balp_validation/scripts/local_json_integrity_lint.py'
if fhir_lint.exists():
    run('fhir_local_json_integrity_lint',[sys.executable, str(fhir_lint.relative_to(fhir_lint.parents[1]))], fhir_lint.parents[1])
bounded = ROOT/'evaluation_workstreams/04_formal_property_validation/04_formalisation/bounded_model/bounded_model_check.py'
if bounded.exists():
    run('bounded_model_executable_check',[sys.executable, str(bounded.relative_to(ROOT/'evaluation_workstreams/04_formal_property_validation'))], ROOT/'evaluation_workstreams/04_formal_property_validation')
if any(s=='FAIL' for _,s in checks):
    raise SystemExit(1)
