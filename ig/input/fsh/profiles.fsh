Profile: TEAuditEvent
Parent: AuditEvent
Id: te-audit-event
Title: "TrustEvidence AuditEvent"
Description: "AuditEvent profile for TrustEvidence emission and verification events. This draft adds an evidence-anchor extension while preserving the AuditEvent event-record role."
* ^url = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/StructureDefinition/te-audit-event"
* ^status = #draft
* ^experimental = true
* extension contains EvidenceAnchor named evidenceAnchor 1..1 MS
* type 1..1 MS
* type ^short = "General audit-event category; use audit-event-type#rest for RESTful operations when applicable."
* subtype MS
* action MS
* period MS
* recorded 1..1 MS
* outcome 0..1 MS
* outcomeDesc MS
* purposeOfEvent MS
* agent 1..* MS
* agent.who 1..1 MS
* agent.requestor 1..1 MS
* agent.policy MS
* agent.purposeOfUse MS
* source 1..1 MS
* source.observer 1..1 MS
* entity 1..* MS
* entity.what MS
* entity.type MS
* entity.role MS
* entity.securityLabel MS
* entity.detail MS
* entity.detail.type 1..1 MS
* entity.detail.value[x] 1..1 MS

Profile: TEProvenance
Parent: Provenance
Id: te-provenance
Title: "TrustEvidence Provenance"
Description: "Provenance profile for TrustEvidence artefacts and evidence-anchor binding. This draft records the actors, entities, activity and policy references associated with the evidence artefact."
* ^url = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/StructureDefinition/te-provenance"
* ^status = #draft
* ^experimental = true
* extension contains EvidenceAnchor named evidenceAnchor 1..1 MS
* target 1..* MS
* target only Reference(AuditEvent or Observation or Consent or Provenance or DocumentReference)
* recorded 1..1 MS
* policy MS
* activity MS
* agent 1..* MS
* agent.who 1..1 MS
* agent.onBehalfOf MS
* entity MS
* entity.role 1..1 MS
* entity.what 1..1 MS
* signature MS
