#!/usr/bin/env python3
"""Conservative release-sanity checks for the public release archive."""
from __future__ import annotations
import json, re
from pathlib import Path
REQUIRED = [
    'README.md','QUICKSTART.md','REPRODUCIBILITY.md','DATA_ACCESS.md','REVIEWER_REPRODUCTION.md',
    'CITATION.cff','.zenodo.json','LICENSE','CHANGELOG.md','SHA256SUMS.txt','FILE_MANIFEST.tsv',
    'OUTPUT_MANIFEST.md','pyproject.toml','Makefile','src/trustevidence/__init__.py','src/te_backend_upgrade/__init__.py',
    'tests/test_merkle_property_evaluation.py','experiments/run_experiments.py','scripts/validate_results_schema.py',
    'evaluation_workstreams/01_fhir_balp_validation/VALIDATION_MATRIX.csv','evaluation_workstreams/02_real_backends/BACKEND_EXECUTION_REPORT.md',
    'evaluation_workstreams/03_workload_calibration/CALIBRATION_REPORT.md','evaluation_workstreams/04_formal_property_validation/FORMAL_PROPERTY_RESULTS.md',
    'protocols/05_expert_validation_protocol/EXPERT_VALIDATION_PROTOCOL_ONLY.md'
]
FORBIDDEN_PHRASES = [
    'computer standards & interfaces','journal of computer standards','csi submission','questionnaire item start','questionnaire item end',
    'sit tight','do not submit','legal compliance is demonstrated','balp conformance is demonstrated',
    'fhir conformance is demonstrated','clinical validation is demonstrated','production-ready system',
    'cryptographic proof is provided','exceptional','unsupported superlative','unsupported superlative','unsupported priority claim'
]
TEXT_SUFFIXES={'.md','.txt','.csv','.json','.yaml','.yml','.toml','.cff','.fsh','.ini','.py','.sh','.bib','.sql','.xml','.cfg','.tla','.als'}
TEXT_NAMES={'Makefile','.gitignore','.gitattributes','.dockerignore','.env.example','LICENSE'}
SKIP_PARTS={'.git','__pycache__','.pytest_cache','.hypothesis','.mypy_cache','.ruff_cache','node_modules','validation','results'}
LOCAL_PATH_RE=re.compile(r'<runtime-workdir>|<runtime-home>|C:\\\\Users|/tmp/stage[0-9]|stage[0-9]_')
def iter_text(root):
    for p in root.rglob('*'):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts): continue
        if p.suffix in TEXT_SUFFIXES or p.name in TEXT_NAMES: yield p, rel.as_posix()
def main() -> int:
    root=Path.cwd(); issues=[]
    for rel in REQUIRED:
        if not (root/rel).exists(): issues.append('missing:'+rel)
    for forbidden_dir in ['audits','corpus_audit_deliverables','environment_plan_deliverables','fhir_balp_workstream_deliverables','backend_workstream_deliverables','workload_workstream_deliverables','property_workstream_deliverables','expert_protocol_workstream_deliverables']:
        if (root/forbidden_dir).exists(): issues.append('unexpected-internal-dir:'+forbidden_dir)
    for p, rel in iter_text(root):
        text=p.read_text(encoding='utf-8', errors='ignore')
        low=text.lower()
        if rel != 'scripts/repository_check.py':
            for phrase in FORBIDDEN_PHRASES:
                if phrase in low: issues.append(f'forbidden:{rel}:{phrase}')
            if LOCAL_PATH_RE.search(text): issues.append(f'local-path:{rel}')
    try:
        data=json.loads((root/'.zenodo.json').read_text(encoding='utf-8'))
        if '10.5281/zenodo.21193829' not in json.dumps(data): issues.append('previous-version-doi-not-recorded-in-zenodo-json')
        if data.get('license') != 'Apache-2.0': issues.append('local-license-not-apache-2.0')
        notes=(data.get('notes') or '').lower()
        if 'previous version' not in notes and 'new version' not in notes: issues.append('versioning-caution-missing')
    except Exception as exc:
        issues.append('zenodo-json-invalid:'+str(exc))
    if issues:
        print('Repository check: FAIL')
        for issue in issues: print(' -', issue)
        return 1
    print('Repository check: PASS')
    return 0
if __name__=='__main__': raise SystemExit(main())
