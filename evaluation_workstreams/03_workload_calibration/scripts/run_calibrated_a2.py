
from __future__ import annotations
import argparse, csv, json, platform, statistics, time, uuid
from pathlib import Path
from typing import Any, Dict

from te_backend_upgrade.canonical import canonical_hash, sha256_hex
from te_backend_upgrade.merkle_log import MerkleLog

def p95(xs: list[float]) -> float:
    if not xs:
        return float('nan')
    if len(xs) >= 20:
        return statistics.quantiles(xs, n=20, method='inclusive')[18]
    return max(xs)

def make_calibrated_evidence(scenario: Dict[str, str], i: int) -> Dict[str, Any]:
    scenario_id = scenario['scenario_id']
    event_count = int(float(scenario['planned_evidence_events']))
    patients_raw = scenario.get('patients') or '1'
    try:
        patients = max(1, int(float(patients_raw)))
    except Exception:
        patients = 1
    obj: Dict[str, Any] = {
        'evidence_id': str(uuid.uuid5(uuid.NAMESPACE_URL, f'trustevidence-workload-calibration workstream-{scenario_id}-{i}')),
        'evidence_type': 'calibrated_workload_event' if i % 7 else 'calibrated_governance_anchor',
        'scenario_id': scenario_id,
        'source_basis_hash': sha256_hex(scenario['source_basis'].encode('utf-8')),
        'scenario_event_index': i,
        'scenario_event_count': event_count,
        'subject_ref_token': f'{scenario_id.lower()}-subject-{i % patients:04d}',
        'payload_hash': sha256_hex(f'workload-calibration workstream-calibrated-payload-{scenario_id}-{i}'.encode('utf-8')),
        'policy_version': 'workload-calibration workstream-calibration-policy-v1',
        'consent_state': 'active' if i % 19 else 'revoked_or_disputed',
        'actor_role': 'service' if i % 3 else 'auditor',
        'organisation_ref': f'org-{i % 5}',
        'backend_type': 'A2_MERKLE',
        'created_at': f'2026-07-05T00:{(i//60)%60:02d}:{i%60:02d}Z',
        'calibration_status': scenario['calibration_status'],
        'dispute_risk': scenario['dispute_risk'],
    }
    obj['canonical_hash'] = canonical_hash(obj)
    return obj

def bench_scenario(scenario: Dict[str, str], sample_count: int, raw_dir: Path, execution_cap: int) -> Dict[str, Any]:
    planned_n = int(float(scenario['planned_evidence_events']))
    n = min(planned_n, execution_cap) if execution_cap > 0 else planned_n
    log = MerkleLog()
    objects: list[dict[str, Any]] = []
    append_times: list[float] = []
    verify_times: list[float] = []
    receipt_sizes: list[int] = []
    proof_sizes: list[int] = []
    start = time.perf_counter()
    for i in range(n):
        obj = make_calibrated_evidence(scenario, i)
        t0 = time.perf_counter_ns(); receipt = log.append(obj); t1 = time.perf_counter_ns()
        append_times.append((t1 - t0) / 1_000_000)
        receipt_sizes.append(log.receipt_size_bytes(receipt))
        objects.append(obj)
    step = max(1, n // sample_count)
    sampled = list(range(0, n, step))[:sample_count]
    root = log.root_hash()
    for idx in sampled:
        proof = log.inclusion_proof(idx)
        proof_sizes.append(log.proof_size_bytes(proof))
        t0 = time.perf_counter_ns(); ok = MerkleLog.verify_inclusion(objects[idx], proof, root); t1 = time.perf_counter_ns()
        verify_times.append((t1 - t0) / 1_000_000)
        if not ok:
            raise RuntimeError(f'Inclusion proof failed for {scenario["scenario_id"]} at index {idx}')
    prefix_size = n // 2
    prefix_ok = log.verify_consistency_by_prefix(prefix_size, log.roots_by_size[prefix_size])
    if not prefix_ok:
        raise RuntimeError(f'Prefix consistency failed for {scenario["scenario_id"]}')
    elapsed = time.perf_counter() - start
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f'{scenario["scenario_id"]}_a2_raw.json'
    raw_path.write_text(json.dumps({'scenario_id': scenario['scenario_id'], 'planned_object_count': planned_n, 'executed_object_count': n, 'root_hash': root, 'append_ms_sample_first_1000': append_times[:1000], 'verify_ms': verify_times, 'proof_sizes': proof_sizes, 'storage_approx_bytes': log.approximate_storage_bytes()}, indent=2, sort_keys=True), encoding='utf-8')
    return {
        'scenario_id': scenario['scenario_id'],
        'backend': 'A2_MERKLE',
        'measurement_scope': 'local_reference_implementation_calibrated_workload',
        'calibration_status': scenario['calibration_status'],
        'planned_evidence_events': planned_n,
        'executed_evidence_events': n,
        'execution_cap_applied': execution_cap if execution_cap > 0 and planned_n > execution_cap else 'no',
        'sampled_verifications': len(sampled),
        'append_p50_ms': round(statistics.median(append_times), 6),
        'append_p95_ms': round(p95(append_times), 6),
        'verify_p50_ms': round(statistics.median(verify_times), 6),
        'verify_p95_ms': round(p95(verify_times), 6),
        'receipt_size_p50_bytes': statistics.median(receipt_sizes),
        'proof_size_p50_bytes': statistics.median(proof_sizes),
        'storage_approx_bytes': log.approximate_storage_bytes(),
        'root_hash': root,
        'elapsed_seconds': round(elapsed, 6),
        'raw_run_file': str(raw_path),
        'python': platform.python_version(),
        'status': 'PASS',
        'interpretation': 'local A2 passage of capped deterministic calibrated TrustEvidence objects; not full workload execution, not production performance and not clinical validation',
    }

def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

def main() -> None:
    parser = argparse.ArgumentParser(description='Run calibrated scenario event counts through the A2 Merkle reference backend.')
    parser.add_argument('--scenarios', default='calibrated_scenarios/calibrated_scenarios.csv')
    parser.add_argument('--out', default='benchmark_outputs/raw_runs/calibrated_a2_raw_runs.csv')
    parser.add_argument('--summary-out', default='benchmark_outputs/calibrated_a2_summary.csv')
    parser.add_argument('--sample-count', type=int, default=128)
    parser.add_argument('--execution-cap', type=int, default=10000, help='Maximum number of descriptor-derived evidence objects to execute locally per scenario; 0 means no cap.')
    parser.add_argument('--raw-dir', default='benchmark_outputs/raw_runs/json')
    args = parser.parse_args()
    with Path(args.scenarios).open(newline='', encoding='utf-8') as f:
        scenarios = list(csv.DictReader(f))
    rows = []
    for scenario in scenarios:
        row = bench_scenario(scenario, args.sample_count, Path(args.raw_dir), args.execution_cap)
        rows.append(row)
        print(json.dumps({'scenario_id': row['scenario_id'], 'planned_events': row['planned_evidence_events'], 'executed_events': row['executed_evidence_events'], 'status': row['status'], 'elapsed_seconds': row['elapsed_seconds']}, sort_keys=True), flush=True)
    write_csv(Path(args.out), rows)
    write_csv(Path(args.summary_out), rows)
    print(f'wrote {args.out}')
    print(f'wrote {args.summary_out}')

if __name__ == '__main__':
    main()
