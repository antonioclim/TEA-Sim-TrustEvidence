Profile: TrustEvidenceAuditEvent
Parent: AuditEvent
Id: trustevidence-auditevent
Title: "TrustEvidence AuditEvent"
Description: "Draft profile for AuditEvent instances carrying compact TrustEvidence commitments."
* extension contains TEBackendType named backendType 0..1 and TEEvidenceHash named evidenceHash 0..1 and TEPolicyVersion named policyVersion 0..1 and TEReceiptRoot named receiptRoot 0..1
* type 1..1
* recorded 1..1
* agent 1..*
* source 1..1
* entity 0..*

Profile: TrustEvidenceProvenance
Parent: Provenance
Id: trustevidence-provenance
Title: "TrustEvidence Provenance"
Description: "Draft Provenance profile for transformation/integrity evidence without clinical payload replication."
* extension contains TEEvidenceHash named evidenceHash 0..1 and TEPolicyVersion named policyVersion 0..1
* target 1..*
* recorded 1..1
* agent 1..*

Profile: TrustEvidenceConsent
Parent: Consent
Id: trustevidence-consent
Title: "TrustEvidence Consent"
Description: "Draft Consent profile for consent-state evidence. It does not implement enforcement logic."
* extension contains TEPolicyVersion named policyVersion 0..1
* status 1..1
* scope 1..1
* category 1..*
