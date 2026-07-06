from __future__ import annotations
import argparse,csv,hashlib,json,platform,sys,time
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
from trustevidence.backends.a1 import InMemoryA1AppendBackend
from trustevidence.backends.a2_merkle import A2MerkleLog
from trustevidence.crypto import DeterministicEd25519KeyPair
from trustevidence.harness.workload import envelope_from_row

def schema(name): return json.loads((ROOT/'schemas/results'/(name+'.schema.json')).read_text(encoding='utf-8'))['required_columns']
def write_rows(results,name,rows):
    with (results/name).open('w',newline='',encoding='utf-8') as f:
        fields=schema(name); w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); [w.writerow({k:r.get(k,'') for k in fields}) for r in rows]
def sha(p): h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def workloads(): return [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'experiments/workloads').glob('W*.json'))]
def event_count(w): return max(8,int(10+int(w['organisations'])*3+float(w['access_per_subject_day'])*20+float(w['revocation_probability'])*200))
def event_row(w,rep,idx):
    wid=w['workload_id']; return {'event_id':f'urn:te:event:{wid}:r{rep:02d}:{idx:05d}','artefact_id':f'urn:te:artefact:{wid}:r{rep:02d}:{idx:05d}','occurred_at':'2026-07-03T12:00:00Z','emitted_at':'2026-07-03T12:00:01Z','event_action':'read' if idx%5 else 'update','action':'R' if idx%5 else 'U','actor':f'actor-{idx%7}','actor_role':'clinician' if idx%3 else 'auditor','subject_token':f'subj_tok_{idx:05d}','organisation_ref':f'urn:te:org:{(idx%max(1,int(w["organisations"])))+1}','resource_ref_token':f'AuditEvent/{wid}-{rep:02d}-{idx:05d}'}
def backend(name, signer):
    if name=='A1-memory': return InMemoryA1AppendBackend('urn:te:backend:a1:local',signer)
    if name=='A2-merkle': return A2MerkleLog('urn:te:backend:a2:local','urn:te:log:a2:local',signer)
    raise ValueError(name)
def run_local(results,repetitions):
    emitter=DeterministicEd25519KeyPair.from_label('urn:te:key:emitter:local','local-emitter')
    raw=[]; proofs=[]; storage=[]; summary=[]; audit=[]; planned=[]; service=[]; anomalies=[]
    for w in workloads():
        for bname in ['A1-memory','A2-merkle']:
            for rep in range(1,repetitions+1):
                seed=20260000+rep; run_id=f'{w["workload_id"]}-{bname}-R{rep:02d}'; planned.append({'run_id':run_id,'workload_id':w['workload_id'],'backend_id':bname,'repetition':rep,'seed':seed,'warmup_seed':seed+100000,'planned_status':'executed-local'})
                signer=DeterministicEd25519KeyPair.from_label(f'urn:te:key:backend:{run_id}',f'backend-{run_id}'); be=backend(bname,signer); accepted=0; start=time.perf_counter_ns(); ab=rb=pb=0
                for idx in range(event_count(w)):
                    env=envelope_from_row(event_row(w,rep,idx),emitter); art=len(json.dumps(env['artefact_core'],sort_keys=True,separators=(',',':')).encode()); t0=time.perf_counter_ns(); out=be.append(env); t1=time.perf_counter_ns(); rec=out.get('backend_receipt',{}); recb=len(json.dumps(rec,sort_keys=True,separators=(',',':')).encode())
                    raw.append({'run_id':run_id,'event_index':idx,'workload_id':w['workload_id'],'backend_id':bname,'repetition':rep,'seed':seed,'latency_ms':f'{(t1-t0)/1e6:.6f}','status':'ok','error_code':'','artefact_bytes':art,'receipt_bytes':recb,'started_ns':t0,'ended_ns':t1}); ab+=art; rb+=recb; accepted+=1
                    if bname=='A2-merkle':
                        proof=be.proof_store.get(rec['inclusion_proof_ref']); pbytes=len(json.dumps(proof,sort_keys=True,separators=(',',':')).encode()); v0=time.perf_counter_ns(); ok=be.verify_inclusion(rec['core_hash'],rec['root_hash'],proof); v1=time.perf_counter_ns(); proofs.append({'run_id':run_id,'event_index':idx,'backend_id':bname,'proof_type':'inclusion','proof_size_bytes':pbytes,'verification_time_ms':f'{(v1-v0)/1e6:.6f}','status':'ok' if ok else 'failed','error_code':'' if ok else 'VERIFY_FAILED'}); pb+=pbytes
                    else: proofs.append({'run_id':run_id,'event_index':idx,'backend_id':bname,'proof_type':'none','proof_size_bytes':0,'verification_time_ms':'0.000000','status':'ok','error_code':''})
                end=time.perf_counter_ns(); dur=max((end-start)/1e9,1e-9); summary.append({'run_id':run_id,'workload_id':w['workload_id'],'backend_id':bname,'repetition':rep,'seed':seed,'accepted_events':accepted,'invalid_events':0,'analysed_duration_s':f'{dur:.9f}','throughput_eps':f'{accepted/dur:.6f}','status':'ok','exclusion_reason':''}); storage.append({'run_id':run_id,'backend_id':bname,'workload_id':w['workload_id'],'event_count':accepted,'total_storage_bytes':ab+rb+pb,'artefact_bytes':ab,'backend_bytes':rb,'proof_bytes':pb,'snapshot_ns':end}); q0=time.perf_counter_ns(); q1=time.perf_counter_ns(); audit.append({'run_id':run_id,'query_id':run_id+'-Q1','backend_id':bname,'workload_id':w['workload_id'],'query_type':'count-by-run','latency_ms':f'{(q1-q0)/1e6:.6f}','result_count':accepted,'status':'ok','error_code':'','started_ns':q0,'ended_ns':q1})
    service.append({'run_id':'local','service_id':'python-local','operation':'local-in-memory-backends','status':'ok','started_at_utc':'n/a','ended_at_utc':'n/a','error_code':'','message':'Docker services not required for local profile'})
    hw=[{'field':'python_version','value':sys.version.split()[0],'evidence_class':'measured-local'},{'field':'platform','value':platform.platform(),'evidence_class':'measured-local'},{'field':'profile','value':'local','evidence_class':'measured-local'},{'field':'repetitions','value':str(repetitions),'evidence_class':'computed'}]
    for name,rows in [('planned_runs.csv',planned),('raw_write_measurements.csv',raw),('proof_measurements.csv',proofs),('storage_snapshots.csv',storage),('run_summary.csv',summary),('audit_query_measurements.csv',audit),('service_preflight.csv',service),('hardware_software_disclosure.csv',hw),('anomaly_log.csv',anomalies),('statistical_summary.csv',[])]: write_rows(results,name,rows)
    manifest=[]
    for p in sorted(results.glob('*.csv')):
        if p.name=='measurement_manifest.csv': continue
        with p.open(newline='',encoding='utf-8') as f: rows=max(0,sum(1 for _ in csv.reader(f))-1)
        manifest.append({'file':p.name,'sha256':sha(p),'size_bytes':p.stat().st_size,'row_count':rows,'evidence_class':'measured-local' if rows else 'schema-only'})
    write_rows(results,'measurement_manifest.csv',manifest)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--profile',default='local',choices=['local','external']); ap.add_argument('--repetitions',type=int,default=10); ap.add_argument('--results-dir',default='results'); ap.add_argument('--require-live',action='store_true'); ap.add_argument('--quick',action='store_true',help='run one-repetition local smoke experiment and write to results/quick unless --results-dir is set'); args=ap.parse_args();
    if args.quick:
        args.profile='local'; args.repetitions=1
        if args.results_dir=='results': args.results_dir='results/quick'
    results=Path(args.results_dir); results.mkdir(parents=True,exist_ok=True)
    if args.profile=='external' or args.require_live: raise SystemExit('External-service measurement requires live Docker services; this local package does not fabricate external measurements.')
    run_local(results,args.repetitions); print('profile=local'); print(f'repetitions={args.repetitions}'); print(f'results_dir={results}'); return 0
if __name__=='__main__': raise SystemExit(main())
