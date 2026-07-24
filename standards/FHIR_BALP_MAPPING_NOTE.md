# FHIR R4/BALP-facing mapping note

TrustEvidence is a project-defined healthcare audit-evidence boundary and executable reference profile. It does not replace FHIR resources or IHE Basic Audit Log Patterns (BALP). The Route C projection uses FHIR R4 AuditEvent, Provenance, Consent, DocumentReference, Binary and Bundle structures to carry or reference the declared evidence set while retaining the exact signed envelope bytes in Binary.

The added value is not a new FHIR primitive. It is the explicit selection and binding of four field classes for one synthetic cross-organisational disclosure case: portable audit facts, source-custody references, cryptographic commitments and excluded clinical payload fields. The positive portable Bundle excludes DiagnosticReport and Observation resources and the declared clinical-value paths.

The exact Route C corpus completed the recorded SUSHI, IG Publisher and HL7 FHIR Validator pathway. Four positive units contained no fatal/error findings and two intended-negative units were rejected for their registered constraint families. This evidence is bounded to the recorded FHIR R4 core, local IG package, applicable BALP profiles, tool versions and resources retained under `standards/fhir_ig/validation/`.

Permitted wording is therefore exact-corpus validator wording. The package does not claim universal FHIR/BALP conformance, an HL7-recognised profile, IHE certification, production interoperability, operational namespace governance or improved clinical semantics.
