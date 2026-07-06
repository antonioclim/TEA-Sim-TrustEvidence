#!/usr/bin/env python3
from pathlib import Path
import json, re
base=Path('validation_logs')
summary={}
for name in ['tool_versions.log','tool_download_attempt.log','sushi.log','ig_publisher.log','fhir_validator.log','local_json_integrity_lint.log']:
    p=base/name
    text=p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''
    summary[name]={'exists':p.exists(),'bytes':p.stat().st_size if p.exists() else 0,'warning_or_error_lines':[ln for ln in text.splitlines() if re.search(r'warn|error|failed|skipped|could not|not present',ln,re.I)][:100]}
(base/'validation_summary.json').write_text(json.dumps(summary,indent=2), encoding='utf-8')
print(json.dumps(summary,indent=2))
