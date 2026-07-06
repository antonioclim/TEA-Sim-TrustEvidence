# Calibration claim boundary

## Supported after workload-calibration workstream

- Public source metadata, access/licence boundaries and size constraints were recorded for Synthea, BIG IDEAs and MIMIC-on-FHIR sources.
- C1-C4 workload descriptors were generated from verified public metadata plus explicit modelling assumptions.
- C2 uses BIG IDEAs participant count, upper monitoring duration and Dexcom G6 five-minute CGM sampling metadata.
- C3 uses MIMIC-IV Clinical Database Demo on FHIR patient count and resource-profile file-list metadata.
- Deterministic synthetic TrustEvidence objects derived from C1-C4 were passed through the A2 Merkle reference backend locally.

## Not supported after workload-calibration workstream

- Full Synthea generation in this runtime.
- Full BIG IDEAs-derived extraction in this runtime.
- Full MIMIC-on-FHIR Demo structural extraction in this runtime.
- A1 PostgreSQL calibrated execution.
- A3 transparency-log or ledger-like calibrated execution.
- Not supported: clinical inference, clinical validation or real-world deployment.

## Public wording allowed

"We constructed externally informed workload descriptors from verified public metadata for Synthea, BIG IDEAs and MIMIC-on-FHIR sources and passed deterministic descriptor-derived TrustEvidence objects through the local A2 Merkle reference backend. Full external-data extraction remains an maintainer-run pathway."

## Public wording forbidden

Forbidden phrases: "Externally calibrated workload benchmark", "BIG IDEAs-calibrated results", "MIMIC-calibrated results", "real-world workload validation", "clinical validation", "A1/A3 calibrated backend comparison".
