# TrustEvidence HIE Reference Profile

This bounded Route C implementation guide projects a synthetic cross-organisational disclosure case onto FHIR R4 resources and the applicable IHE Basic Audit Log Patterns 1.1.4 AuditEvent profiles.

The exact signed TrustEvidence envelope is carried as canonical bytes in a profiled `Binary`. The structured FHIR projection contains a consent-authorisation AuditEvent, a privacy-disclosure AuditEvent, Provenance, a Consent derivative, pseudonymous context resources and a DocumentReference. The source DiagnosticReport and laboratory Observation values remain outside the portable evidence bundle.

Passing this guide's declared toolchain does not constitute HL7 or IHE certification, clinical validation or production deployment.
