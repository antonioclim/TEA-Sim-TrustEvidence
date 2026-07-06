from __future__ import annotations
import argparse,csv,json,statistics,hashlib
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
def schema(name): return json.loads((ROOT/'schemas/results'/(name+'.schema.json')).read_text(encoding='utf-8'))['required_columns']
def pct(vals,q):
    xs=sorted(vals)
    if not xs: return float('nan')
    if len(xs)==1: return xs[0]
    pos=(len(xs)-1)*q; lo=int(pos); hi=min(lo+1,len(xs)-1); frac=pos-lo; return xs[lo]*(1-frac)+xs[hi]*frac
def collect(path,keys,metric):
    out=defaultdict(list)
    with path.open(newline='',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r.get(metric,'')!='': out[tuple(r[k] for k in keys)].append(float(r[metric]))
    return out
def add(rows,grouped,metric_id):
    for key,vals in grouped.items():
        wid,bid=key if len(key)==2 else ('all',key[-1]); rows.append({'slot_id':f'{wid}-{bid}-{metric_id}','workload_id':wid,'backend_id':bid,'metric_id':metric_id,'estimate':f'{statistics.mean(vals):.6f}','ci_low':f'{pct(vals,0.025):.6f}','ci_high':f'{pct(vals,0.975):.6f}','effect_vs_a1':'','effect_vs_a2':'','ci_method':'empirical-percentile','evidence_class':'measured-local'})

def digest(p: Path) -> str:
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def update_manifest(results_dir: Path) -> None:
    fields=schema('measurement_manifest.csv'); rows=[]
    for p in sorted(results_dir.glob('*.csv')):
        if p.name=='measurement_manifest.csv': continue
        with p.open(newline='',encoding='utf-8') as f:
            row_count=max(0,sum(1 for _ in csv.reader(f))-1)
        rows.append({'file':p.name,'sha256':digest(p),'size_bytes':p.stat().st_size,'row_count':row_count,'evidence_class':'measured-local' if row_count else 'schema-only'})
    with (results_dir/'measurement_manifest.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); [w.writerow({k:r.get(k,'') for k in fields}) for r in rows]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--results-dir',default='results'); ap.add_argument('--out',default='results/statistical_summary.csv'); args=ap.parse_args(); rd=Path(args.results_dir); rows=[]
    add(rows,collect(rd/'raw_write_measurements.csv',['workload_id','backend_id'],'latency_ms'),'write_latency_ms_mean')
    add(rows,collect(rd/'run_summary.csv',['workload_id','backend_id'],'throughput_eps'),'throughput_eps_mean')
    add(rows,collect(rd/'storage_snapshots.csv',['workload_id','backend_id'],'total_storage_bytes'),'storage_total_bytes_mean')
    add(rows,collect(rd/'proof_measurements.csv',['run_id','backend_id'],'verification_time_ms'),'verification_time_ms_mean_by_run')
    fields=schema('statistical_summary.csv')
    with Path(args.out).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); [w.writerow({k:r.get(k,'') for k in fields}) for r in rows]
    update_manifest(rd); print('analysis: PASS'); print(f'summary_rows={len(rows)}'); print('measurement_manifest: refreshed'); return 0
if __name__=='__main__': raise SystemExit(main())
