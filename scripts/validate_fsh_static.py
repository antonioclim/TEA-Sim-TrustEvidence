#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
fsh_dir = root / 'ig' / 'input' / 'fsh'
text = '\n'.join(p.read_text(encoding='utf-8') for p in sorted(fsh_dir.glob('*.fsh')))
counts = {
    'fsh_files': len(list(fsh_dir.glob('*.fsh'))),
    'profiles': len(re.findall(r'^Profile:\s+', text, re.M)),
    'extensions': len(re.findall(r'^Extension:\s+', text, re.M)),
    'codesystems': len(re.findall(r'^CodeSystem:\s+', text, re.M)),
    'valuesets': len(re.findall(r'^ValueSet:\s+', text, re.M)),
    'instances': len(re.findall(r'^Instance:\s+', text, re.M)),
}
expected = {'profiles': 2, 'extensions': 1, 'codesystems': 2, 'valuesets': 2, 'instances': 12}
errors: list[str] = []
for key, exp in expected.items():
    if counts[key] != exp:
        errors.append(f'{key}: expected {exp}, found {counts[key]}')
for item in [
    'Profile: TEAuditEvent', 'Profile: TEProvenance', 'Extension: EvidenceAnchor',
    'CodeSystem: TEEvidenceClassCS', 'CodeSystem: TEBackendTypeCS',
    'ValueSet: TEEvidenceClassVS', 'ValueSet: TEBackendTypeVS',
]:
    if item not in text:
        errors.append('missing ' + item)
print('Static FSH check: ' + ('PASS' if not errors else 'FAIL'))
for key, value in counts.items():
    print(f'{key}={value}')
for error in errors:
    print('- ' + error)
sys.exit(0 if not errors else 1)
