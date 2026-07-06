# workload-calibration workstream calibration report

Verification/execution date: 2026-07-05.

## Purpose

workload-calibration workstream reduces the arbitrariness of the original internal stress-test scenarios by binding C1-C4 workload descriptors to verified public source metadata where possible. It does not claim clinical validation, production performance or complete external-data extraction.

## Source classes

- **Synthea** was used as a generator-compatible source class: public metadata confirms an FHIR R4 export pathway, but the generator was not downloaded or executed in this runtime.
- **BIG IDEAs v1.1.3** supplied wearable/CGM monitoring parameters: 16 participants, an upper monitoring period of 10 days and Dexcom G6 five-minute interstitial glucose sampling. These values yield 288 CGM observations per participant-day and 46,080 C2 evidence-event opportunities.
- **MIMIC-IV Clinical Database Demo on FHIR v2.1.0** supplied FHIR heterogeneity parameters: 100 demo patients and 30 compressed NDJSON resource-profile files. workload-calibration workstream uses a profile-pairing proxy of 3,000 C3 evidence-event opportunities; this is a workload-construction proxy, not an extracted record count.
- **C4 dispute stress** combines C2 event density with an explicit 1.1 governance/dispute anchor multiplier, yielding 50,688 planned evidence-event opportunities.

## Scenario construction

| Scenario | Source basis | Planned events | Executed events | Calibration status |
|---|---|---:|---:|---|
| C1_ROUTINE_SYNTHETIC_AMBULATORY | Synthea FHIR R4 generator capability plus internal hourly evidence-event assumption | 240,000 | 10,000 | partially_calibrated_metadata_plus_assumption |
| C2_WEARABLE_CGM_MONITORING | BIG IDEAs v1.1.3 participants, monitoring duration and Dexcom G6 5-minute sampling metadata | 46,080 | 10,000 | calibrated_from_verified_public_metadata |
| C3_FHIR_HETEROGENEITY_DEMO | MIMIC-IV Clinical Database Demo on FHIR v2.1.0 patient count and resource-profile file list | 3,000 | 3,000 | calibrated_from_verified_public_metadata_with_profile_pairing_assumption |
| C4_CROSS_ORGANISATIONAL_DISPUTE | BIG IDEAs CGM density plus governance/dispute anchor multiplier | 50,688 | 10,000 | calibrated_metadata_plus_governance_stress_assumption |


A local execution cap of 10,000 objects per scenario was applied to avoid converting a calibration stage into a large benchmark stage. C3 had only 3,000 planned events and therefore ran in full. C1, C2 and C4 were capped. This cap is recorded in `benchmark_outputs/calibrated_a2_summary.csv` and prevents any full-workload performance claim.

## A2 local passage results

| Scenario | Append p50 ms | Append p95 ms | Verify p50 ms | Verify p95 ms | Receipt p50 bytes | Proof p50 bytes | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| C1_ROUTINE_SYNTHETIC_AMBULATORY | 0.023893 | 0.031795 | 0.029755 | 0.034641 | 304 | 1073 | PASS |
| C2_WEARABLE_CGM_MONITORING | 0.023708 | 0.029832 | 0.030364 | 0.034204 | 304 | 1073 | PASS |
| C3_FHIR_HETEROGENEITY_DEMO | 0.023439 | 0.029640 | 0.025951 | 0.028614 | 304 | 919 | PASS |
| C4_CROSS_ORGANISATIONAL_DISPUTE | 0.024085 | 0.031680 | 0.029062 | 0.038285 | 304 | 1073 | PASS |


These values are local reference-implementation timings for deterministic TrustEvidence objects. They are useful for checking that calibrated descriptor-derived objects pass the A2 Merkle append and inclusion-verification pathway. They are not database measurements, transparency-log measurements, clinical-system latency values or production benchmarks.

## Full extraction status

Full external extraction remains pending because the execution container had no direct DNS/network access. BIG IDEAs is also too large for a lightweight release kit, and full MIMIC-IV on FHIR requires credentialed access, a data-use agreement and training. The kit therefore supplies maintainer-run scripts and non-redistribution boundaries.

## Manuscript wording

Allowed wording:

> We constructed externally informed workload descriptors from verified public metadata for Synthea, BIG IDEAs and MIMIC-on-FHIR sources and passed capped deterministic descriptor-derived TrustEvidence objects through the local A2 Merkle reference backend.

Forbidden wording:

> Forbidden: Full externally calibrated benchmark; BIG IDEAs-calibrated results; MIMIC-calibrated results; clinical validation; real-world workload validation; A1/A3 calibrated backend comparison.
