#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

REQUIRED = [
    'README.md', 'QUICKSTART.md', 'REPRODUCIBILITY.md', 'CITATION.cff', '.zenodo.json',
    'CHANGELOG.md', 'ARTEFACT_EVALUATION.md', 'SHA256SUMS.txt', 'OUTPUT_MANIFEST.md',
    'pyproject.toml', 'Makefile', 'src/trustevidence/__init__.py', 'src/teasim/__init__.py',
    'SPEC.md', 'THREAT_MODEL.md', 'proofs/formal_core.md', 'ig/sushi-config.yaml',
    'experiments/run_experiments.py', 'scripts/repository_check.py',
    'docs/EXTERNAL_SERVICES.md', 'docs/IG_VALIDATION.md', 'docs/SHA256SUMS_PROTOCOL.md',
]
FORBIDDEN_CLAIMS = [
    'legal compliance is demonstrated',
    'balp conformance is demonstrated',
    'fhir conformance is demonstrated',
    'benchmark results demonstrate',
    'production deployment is demonstrated',
]


def main() -> int:
    root = Path.cwd()
    issues: list[str] = []
    for rel in REQUIRED:
        if not (root / rel).exists():
            issues.append('missing:' + rel)
    if (root / 'audits').exists():
        issues.append('unexpected:audits')
    for path in list(root.rglob('*.md')) + list(root.rglob('*.txt')):
        if 'legacy' in path.relative_to(root).parts:
            continue
        text = path.read_text(encoding='utf-8', errors='ignore').lower()
        for phrase in FORBIDDEN_CLAIMS:
            if phrase in text:
                issues.append(f'overclaim:{path.relative_to(root)}:{phrase}')
    try:
        payload = json.loads((root / '.zenodo.json').read_text(encoding='utf-8'))
        dump = json.dumps(payload)
        if '10.5281/zenodo.21134217' not in dump:
            issues.append('zenodo relation to v1.5.1 missing')
        if 'github.com/antonioclim/TEA-Sim-TrustEvidence' not in dump:
            issues.append('current repository relation missing')
    except Exception as exc:
        issues.append(f'zenodo json unreadable:{exc}')
    if issues:
        print('Repository check: FAIL')
        for issue in issues:
            print(issue)
        return 1
    print('Repository check: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
