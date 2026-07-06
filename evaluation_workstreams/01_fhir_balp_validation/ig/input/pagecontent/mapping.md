# TrustEvidence field-to-FHIR mapping

This draft mapping records how compact TrustEvidence facts are represented in FHIR R4-facing resources. It is a research artefact for local validation, not an HL7, IHE, GDPR, EHDS or ISO conformance claim.

| TrustEvidence fact | FHIR R4-facing representation | Replication boundary |
|---|---|---|
| subject pseudonym or reference | `Patient.identifier` or referenced `Patient/{id}` | pseudonymous identifier only; no clinical payload replication |
| access event | `AuditEvent.type`, `AuditEvent.subtype`, `AuditEvent.action`, `AuditEvent.recorded` | event fact stored as audit evidence |
| actor role/requestor | `AuditEvent.agent` | pseudonymous role/display value only |
| source system | `AuditEvent.source` | system identity/display value only |
| consent state | `Consent.status`, `Consent.scope`, `Consent.category` | consent-state evidence, not enforcement logic |
| provenance/transformation | `Provenance.target`, `Provenance.recorded`, `Provenance.agent` | transformation evidence; payload remains outside evidence boundary |
| canonical payload/evidence hash | `TEEvidenceHash` extension | hash commitment only |
| backend class | `TEBackendType` extension | local backend classification only |
| policy version | `TEPolicyVersion` extension | policy/governance version label |
| receipt/root | `TEReceiptRoot` extension on receipt examples | synthetic root/receipt value only |
