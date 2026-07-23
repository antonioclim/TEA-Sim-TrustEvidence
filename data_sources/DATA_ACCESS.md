# Data-source access boundary

The retained executable evidence contains no downloaded external clinical dataset. Every monitoring event, HIE source resource and disclosure object passed through the implementation is synthetic.

External sources have bounded roles:

1. public documentation and metadata inform the preserved personal-monitoring workload descriptors;
2. cited FHIR/IHE standards and current literature position the HIE profile and validator corpus;
3. no external patient record or physiological time series is replayed by C3, C4 or C5;
4. C5 uses the frozen synthetic W1 disclosure fixture only.

No raw external values or participant identifiers are distributed. Source versions, licences and access routes are recorded separately and do not support cohort calibration, operational workload representativeness or clinical validation claims.
