# Data access

All healthcare and monitoring objects distributed in this release candidate are synthetic. No identifiable patient data, source participant identifiers, raw physiological time series, restricted clinical records or operational hospital data are included.

The C3 hero case contains clinically plausible synthetic FHIR resources solely to make the disclosure and evidence boundary inspectable. The portable evidence bundle and signed TrustEvidence envelope exclude the DiagnosticReport, Observation payload values and declared direct clinical-value paths. The source resources remain in the synthetic source-custody fixture.

External sources have bounded provenance roles documented in `data_sources/` and the verified reference registry:

- public documentation and metadata inform legacy synthetic workload descriptors;
- no external clinical dataset is downloaded or replayed by the retained executable passages;
- restricted or large datasets are not redistributed;
- C5 uses only the frozen synthetic W1 disclosure fixture.

Live access and licence conditions for cited external resources remain source-controlled publication metadata and do not convert the synthetic evidence into operational or clinical validation.
