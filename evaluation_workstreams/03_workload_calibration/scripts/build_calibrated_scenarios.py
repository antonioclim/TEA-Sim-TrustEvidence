
from __future__ import annotations
import argparse, csv, math
from pathlib import Path
from typing import Dict, Any

def read_params(path: Path) -> Dict[str, Dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as f:
        return {row['parameter']: row for row in csv.DictReader(f)}

def get_float(params: Dict[str, Dict[str, str]], key: str, default: float) -> float:
    try:
        return float(params[key]['value'])
    except Exception:
        return default

def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fieldnames:
        fieldnames = list(rows[0].keys())
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(rows)

def main() -> None:
    parser = argparse.ArgumentParser(description='Build calibrated TrustEvidence workload scenarios from verified metadata.')
    parser.add_argument('--metadata', default='metadata/VERIFIED_PUBLIC_SOURCE_PARAMETERS.csv')
    parser.add_argument('--out', default='calibrated_scenarios/calibrated_scenarios.csv')
    parser.add_argument('--parameter-out', default='calibrated_scenarios/PARAMETER_REGISTER_CALIBRATED.csv')
    args = parser.parse_args()
    params = read_params(Path(args.metadata))
    big_participants = int(get_float(params, 'bigideas_participants', 16))
    big_days = int(get_float(params, 'bigideas_monitoring_days_max', 10))
    cgm_interval = get_float(params, 'bigideas_cgm_interval_minutes', 5)
    cgm_per_day = int(round(24 * 60 / max(cgm_interval, 1)))
    mimic_patients = int(get_float(params, 'mimic_demo_patients', 100))
    mimic_profiles = int(get_float(params, 'mimic_demo_resource_profile_files', 30))
    c1_obs = int(get_float(params, 'c1_routine_events_per_patient_day', 24))
    c4_multiplier = get_float(params, 'c4_dispute_anchor_multiplier', 1.1)
    scenarios = [
        {'scenario_id': 'C1_ROUTINE_SYNTHETIC_AMBULATORY','source_basis': 'Synthea FHIR R4 generator capability plus internal hourly evidence-event assumption','calibration_status': 'partially_calibrated_metadata_plus_assumption','patients': 1000,'days': 10,'obs_per_patient_day': c1_obs,'planned_evidence_events': 1000 * 10 * c1_obs,'event_count_derivation': '1000 patients × 10 days × 24 hourly TrustEvidence objects per patient-day','dispute_risk': 0.20,'backend_preference': 'A1/A2 candidate; A2 executed locally in workload-calibration workstream','full_external_extraction_status': 'Synthea not downloaded or run in this runtime'},
        {'scenario_id': 'C2_WEARABLE_CGM_MONITORING','source_basis': 'BIG IDEAs v1.1.3 participants, monitoring duration and Dexcom G6 5-minute sampling metadata','calibration_status': 'calibrated_from_verified_public_metadata','patients': big_participants,'days': big_days,'obs_per_patient_day': cgm_per_day,'planned_evidence_events': big_participants * big_days * cgm_per_day,'event_count_derivation': f'{big_participants} participants × {big_days} days × {cgm_per_day} CGM samples per participant-day','dispute_risk': 0.35,'backend_preference': 'A2 unless dispute escalation requires external anchoring','full_external_extraction_status': 'Full BIG IDEAs files not downloaded; large dataset and no runtime network'},
        {'scenario_id': 'C3_FHIR_HETEROGENEITY_DEMO','source_basis': 'MIMIC-IV Clinical Database Demo on FHIR v2.1.0 patient count and resource-profile file list','calibration_status': 'calibrated_from_verified_public_metadata_with_profile_pairing_assumption','patients': mimic_patients,'days': 'NA','obs_per_patient_day': 'NA','planned_evidence_events': mimic_patients * mimic_profiles,'event_count_derivation': f'{mimic_patients} patients × {mimic_profiles} FHIR resource-profile files','dispute_risk': 0.45,'backend_preference': 'A2; A1 unavailable; A3 adapter only','full_external_extraction_status': 'Demo files not downloaded in runtime; maintainer can run downloader externally'},
        {'scenario_id': 'C4_CROSS_ORGANISATIONAL_DISPUTE','source_basis': 'BIG IDEAs CGM density plus governance/dispute anchor multiplier','calibration_status': 'calibrated_metadata_plus_governance_stress_assumption','patients': big_participants,'days': big_days,'obs_per_patient_day': cgm_per_day,'planned_evidence_events': int(round(big_participants * big_days * cgm_per_day * c4_multiplier)),'event_count_derivation': f'C2 events × {c4_multiplier:g} governance/dispute anchor multiplier','dispute_risk': 0.85,'backend_preference': 'A3 candidate in principle; A2 only executed locally','full_external_extraction_status': 'No external dispute dataset; synthetic governance stress only'},
    ]
    fieldnames = ['scenario_id','source_basis','calibration_status','patients','days','obs_per_patient_day','planned_evidence_events','event_count_derivation','dispute_risk','backend_preference','full_external_extraction_status']
    write_csv(Path(args.out), scenarios, fieldnames)
    register = list(params.values())
    register.extend([
        {'parameter_id': 'COMP_001', 'parameter': 'bigideas_cgm_observations_per_patient_day', 'value': cgm_per_day, 'unit': 'count_per_patient_day', 'source_name': 'computed_from_BIG_004', 'source_version': '1.1.3', 'source_url': 'https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/', 'evidence_basis': '24*60/cgm_interval_minutes', 'calibration_status': 'computed_from_verified_metadata', 'notes': ''},
        {'parameter_id': 'COMP_002', 'parameter': 'c2_planned_evidence_events', 'value': big_participants * big_days * cgm_per_day, 'unit': 'events', 'source_name': 'computed_from_BIG_002_BIG_003_BIG_004', 'source_version': '1.1.3', 'source_url': 'https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/', 'evidence_basis': 'participants*days*obs_per_patient_day', 'calibration_status': 'computed_from_verified_metadata', 'notes': ''},
        {'parameter_id': 'COMP_003', 'parameter': 'c3_planned_profile_pairing_events', 'value': mimic_patients * mimic_profiles, 'unit': 'events', 'source_name': 'computed_from_MIMICD_002_MIMICD_003', 'source_version': '2.1.0', 'source_url': 'https://physionet.org/content/mimic-iv-fhir-demo/2.1.0/', 'evidence_basis': 'patients*resource_profile_file_count', 'calibration_status': 'computed_from_verified_metadata_with_assumption', 'notes': 'Proxy for heterogeneity stress, not actual record count.'},
    ])
    reg_fieldnames = ['parameter_id','parameter','value','unit','source_name','source_version','source_url','evidence_basis','calibration_status','notes']
    write_csv(Path(args.parameter_out), register, reg_fieldnames)
    print(f'wrote {args.out}')
    print(f'wrote {args.parameter_out}')

if __name__ == '__main__':
    main()
