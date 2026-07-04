#!/usr/bin/env python3
from pathlib import Path
import csv, json, sys
root=Path(__file__).resolve().parents[1]
req=['ig/input/fsh/capabilitystatements.fsh','ig/input/pagecontent/index.md','ig/input/pagecontent/background.md','ig/input/pagecontent/actors.md','ig/input/pagecontent/capabilitystatements.md','ig/input/pagecontent/balp-atna-mapping.md','ig/input/pagecontent/conformance.md','ig/input/pagecontent/security.md','ig/input/pagecontent/privacy.md','ig/input/pagecontent/validation.md','tables/fhir_capability_statements.csv','tables/balp_atna_mapping.csv','tables/fhir_conformance_test_plan.csv','tables/fhir_ig_qa_checklist.csv','docs/STANDARDS_PATHWAY.md','ig/VALIDATION_INSTRUCTIONS.md']
missing=[x for x in req if not (root/x).exists()]
cap=(root/'ig/input/fsh/capabilitystatements.fsh').read_text(encoding='utf-8') if not missing else ''
checks={'emitter':'Instance: TEEmitterCapabilityStatement' in cap,'verifier':'Instance: TEVerifierCapabilityStatement' in cap,'requirements':'kind = #requirements' in cap,'r4':'fhirVersion = #4.0.1' in cap,'audit':'type = #AuditEvent' in cap,'provenance':'type = #Provenance' in cap}
counts={}
for fname in ['fhir_capability_statements.csv','balp_atna_mapping.csv','fhir_conformance_test_plan.csv','fhir_ig_qa_checklist.csv','standards_pathway.csv']:
    with (root/'tables'/fname).open(newline='',encoding='utf-8') as f: counts[fname]=sum(1 for _ in csv.DictReader(f))
status=not missing and all(checks.values())
print('Static IG check: '+('PASS' if status else 'FAIL')); print('missing='+json.dumps(missing)); print('checks='+json.dumps(checks,sort_keys=True)); print('counts='+json.dumps(counts,sort_keys=True)); sys.exit(0 if status else 1)
