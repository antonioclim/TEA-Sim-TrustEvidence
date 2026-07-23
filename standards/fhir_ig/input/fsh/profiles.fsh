Alias: $teEvidenceType = https://example.org/fhir/trustevidence-hie/CodeSystem/te-evidence-type

CodeSystem: TEEvidenceType
Id: te-evidence-type
Title: "TrustEvidence Evidence Type"
Description: "Project-defined evidence-document types for the bounded Route C reference profile."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #portable-audit-evidence "Portable audit evidence"

ValueSet: TEEvidenceTypeVS
Id: te-evidence-type-vs
Title: "TrustEvidence Evidence Type Value Set"
Description: "Evidence-document types admitted by the bounded Route C profile."
* ^experimental = false
* include codes from system $teEvidenceType

Profile: TEPortableEvidenceBinary
Parent: Binary
Id: te-portable-evidence-binary
Title: "TrustEvidence Portable Evidence Binary"
Description: "Exact canonical JSON bytes of a signed TrustEvidence envelope with its project-specific local A2 receipt."
* contentType = #application/json (exactly)
* data 1..1
* securityContext 1..1

Profile: TEEvidenceDocumentReference
Parent: DocumentReference
Id: te-evidence-document-reference
Title: "TrustEvidence Evidence Document Reference"
Description: "DocumentReference that points to the exact signed TrustEvidence Binary and related audit artefacts."
* status = #current (exactly)
* type 1..1
* type from TEEvidenceTypeVS (required)
* subject 1..1
* date 1..1
* author 1..*
* custodian 1..1
* content 1..1
* content.attachment.contentType = #application/json (exactly)
* content.attachment.url 1..1
* content.attachment.hash 1..1
* context.related 3..*

Profile: TEEvidenceProvenance
Parent: Provenance
Id: te-evidence-provenance
Title: "TrustEvidence Evidence Provenance"
Description: "Provenance linking the disclosure AuditEvents and exact signed-envelope Binary to the version-identified source DiagnosticReport retained by the source custodian."
* target 3..*
* occurred[x] 1..1
* recorded 1..1
* agent 1..*
* entity 1..*

Profile: TEPortableEvidenceBundle
Parent: Bundle
Id: te-portable-evidence-bundle
Title: "TrustEvidence Portable Evidence Bundle"
Description: "Collection bundle containing pseudonymous context, BALP AuditEvents, Consent, Provenance and the exact signed-envelope Binary; clinical Observation and DiagnosticReport resources are not admitted."
* identifier 1..1
* type = #collection (exactly)
* timestamp 1..1
* entry 10..*
* entry.resource only Patient or Organization or Device or Practitioner or PractitionerRole or Consent or AuditEvent or Provenance or Binary or DocumentReference
