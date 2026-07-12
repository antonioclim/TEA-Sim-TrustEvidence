# Source and workload-descriptor audit

The executed workload is an externally informed synthetic passage, not a replay of an external clinical dataset and not a full-dataset calibration study.

Public source families were considered only for bounded scenario design:

- Synthea documentation informs synthetic FHIR-style object heterogeneity;
- a BIG IDEAs or equivalent PhysioNet CGM source family informs plausible sampling and missingness context;
- MIMIC-IV-on-FHIR Demo documentation informs FHIR resource heterogeneity, subject to the exact source’s access and licence conditions.

No external clinical record or physiological time series is processed by the retained executable passage. One earlier aggregate-only single-participant CGM descriptor informed scenario design, but no raw values or participant identifiers are distributed here. Exact source versions, licences and access conditions require live verification before manuscript submission.

Permitted wording is “externally informed synthetic workload descriptors”. The archive does not support cohort calibration, representative-population, real-world clinical or production-workload claims.
