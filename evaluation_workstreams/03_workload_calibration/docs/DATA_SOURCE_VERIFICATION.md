# Data source verification note

Verification date: 2026-07-05.

The source register records public metadata visible on official source pages. The in-container shell had no working DNS resolution, so direct command-line download was not possible during workload-calibration workstream. Full extraction remains an maintainer-run pathway.

- Synthea: official GitHub repository; synthetic patient population simulator; FHIR R4 output pathway; Apache-2.0 software licence shown by the repository interface.
- BIG IDEAs: PhysioNet v1.1.3; DOI 10.13026/aw6y-fc44; Open Data Commons Attribution License v1.0; participant and sampling metadata used for C2; reported ZIP size 4.7 GB and uncompressed size 34.1 GB.
- MIMIC-IV Clinical Database Demo on FHIR: PhysioNet v2.1.0; Open Data Commons Open Database License v1.0; 100-patient subset; compressed NDJSON resource files; reported uncompressed size 49.5 MB.
- MIMIC-IV on FHIR full project: credentialed access and DUA pathway only.

These sources provide parameter-calibration targets, not clinical validation evidence for TrustEvidence.
