#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
EXAMPLES=BASE/'examples'
GEN=BASE/'ig'/'fsh-generated'/'resources'
OUT=BASE/'validation_logs'/'local_json_integrity_lint.csv'
LOG=BASE/'validation_logs'/'local_json_integrity_lint.log'
KNOWN={'Patient','Observation','Consent','Provenance','AuditEvent','Basic'}
LOCAL_PROFILE={
 'AuditEvent':'https://example.org/fhir/te/StructureDefinition/trustevidence-auditevent',
 'Consent':'https://example.org/fhir/te/StructureDefinition/trustevidence-consent',
 'Provenance':'https://example.org/fhir/te/StructureDefinition/trustevidence-provenance',
 'Basic':'https://example.org/fhir/te/StructureDefinition/trustevidence-receipt'
}
REQ={
 'Patient':['identifier'],
 'Observation':['status','code','subject','effectiveDateTime'],
 'Consent':['status','scope','category','patient'],
 'Provenance':['target','recorded','agent'],
 'AuditEvent':['type','subtype','action','recorded','outcome','agent','source'],
 'Basic':['code','extension']
}
allowed_ext={
 'https://example.org/fhir/te/StructureDefinition/te-backend-type',
 'https://example.org/fhir/te/StructureDefinition/te-evidence-hash',
 'https://example.org/fhir/te/StructureDefinition/te-policy-version',
 'https://example.org/fhir/te/StructureDefinition/te-receipt-root'
}
ids=set(); rows=[]; status=0
resources=[]
for p in sorted(EXAMPLES.glob('*.json')):
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        rows.append({'file':p.name,'resourceType':'','json_parse':'FAIL','required_fields':'FAIL','local_profile':'NOT_RUN','extension_check':'NOT_RUN','reference_check':'NOT_RUN','notes':repr(e)})
        status=1; continue
    resources.append((p,data)); ids.add(f"{data.get('resourceType')}/{data.get('id')}")
for p,data in resources:
    errors=[]; rt=data.get('resourceType')
    if rt not in KNOWN: errors.append(f'unknown resourceType {rt!r}')
    if not data.get('id'): errors.append('missing id')
    for k in REQ.get(rt,[]):
        if k not in data: errors.append(f'missing {k}')
    profiles=data.get('meta',{}).get('profile',[])
    local_needed=LOCAL_PROFILE.get(rt)
    local_profile_status='PASS'
    if local_needed and local_needed not in profiles:
        errors.append('missing local profile '+local_needed); local_profile_status='FAIL'
    ext_status='PASS'
    ext_notes=[]
    for ext in data.get('extension',[]):
        url=ext.get('url','')
        if url not in allowed_ext:
            ext_notes.append('unexpected extension '+url)
        if url.endswith('te-backend-type') and ext.get('valueCode') not in ['A1_POSTGRES','A2_MERKLE','A3_REKOR','A3_TRILLIAN','A3_FABRIC']:
            ext_notes.append('bad backend code '+str(ext.get('valueCode')))
        for key,val in ext.items():
            if key.startswith('value') and isinstance(val,str) and val.startswith('sha256:'):
                if not re.fullmatch(r'sha256:[0-9a-f]{64}', val): ext_notes.append('noncanonical sha256 value')
    if ext_notes: errors.extend(ext_notes); ext_status='FAIL'
    ref_status='PASS'
    refs=[]
    def walk(x):
        if isinstance(x,dict):
            if isinstance(x.get('reference'),str): refs.append(x['reference'])
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(data)
    missing=[r for r in refs if '/' in r and not r.startswith('http') and r not in ids]
    if missing: errors.append('missing local references: '+','.join(missing)); ref_status='FAIL'
    rows.append({'file':p.name,'resourceType':rt or '', 'json_parse':'PASS','required_fields':'PASS' if not errors else 'FAIL','local_profile':local_profile_status,'extension_check':ext_status,'reference_check':ref_status,'notes':'; '.join(errors) if errors else 'local structural checks passed'})
    if errors: status=1
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('w', newline='', encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=['file','resourceType','json_parse','required_fields','local_profile','extension_check','reference_check','notes'])
    w.writeheader(); w.writerows(rows)
LOG.write_text(f'local_json_integrity_lint_status={status}\nexamples_checked={len(rows)}\n', encoding='utf-8')
print(LOG.read_text(), end='')
sys.exit(status)
