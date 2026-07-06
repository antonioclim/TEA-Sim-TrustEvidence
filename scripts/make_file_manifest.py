#!/usr/bin/env python3
from pathlib import Path
import argparse, csv, hashlib, mimetypes
EXCLUDE_PARTS={'.git','__pycache__','.pytest_cache','.hypothesis','.mypy_cache','.ruff_cache','node_modules'}
EXCLUDE_TOPLEVEL={'validation','results','dist','build'}
EXCLUDE_NAMES={'FILE_MANIFEST.tsv','SHA256SUMS.txt'}
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()
def role(rel):
    parts=rel.parts
    if parts[0]=='src': return 'source_code'
    if parts[0]=='tests': return 'tests'
    if parts[0]=='experiments': return 'experiment_workflow'
    if parts[0]=='evaluation_workstreams': return 'evaluation_workstreams_evidence_or_protocol'
    if parts[0]=='protocols': return 'protocol_material'
    if parts[0]=='schemas': return 'schema'
    if parts[0] in {'figures','tables'}: return 'research_output'
    if parts[0] in {'docs','references'}: return 'documentation'
    if rel.name in {'README.md','QUICKSTART.md','REPRODUCIBILITY.md','DATA_ACCESS.md','REVIEWER_REPRODUCTION.md','CITATION.cff','.zenodo.json','LICENSE','CHANGELOG.md'}: return 'top_level_metadata'
    return 'other_release_file'
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--output', default='FILE_MANIFEST.tsv'); args=ap.parse_args(); root=Path(args.root).resolve(); rows=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if p.name in EXCLUDE_NAMES or any(part in EXCLUDE_PARTS for part in rel.parts) or (rel.parts and rel.parts[0] in EXCLUDE_TOPLEVEL): continue
        mt=mimetypes.guess_type(str(p))[0] or 'application/octet-stream'
        rows.append({'path':rel.as_posix(),'size_bytes':p.stat().st_size,'sha256':digest(p),'media_type':mt,'role':role(rel)})
    with (root/args.output).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=['path','size_bytes','sha256','media_type','role'], delimiter='\t')
        w.writeheader(); w.writerows(rows)
    print(f'wrote {len(rows)} rows to {root/args.output}')
if __name__=='__main__': main()
