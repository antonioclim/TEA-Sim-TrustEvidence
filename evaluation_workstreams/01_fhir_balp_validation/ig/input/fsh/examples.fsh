Instance: te-auditevent-read-example
InstanceOf: TrustEvidenceAuditEvent
Usage: #example
* type = http://terminology.hl7.org/CodeSystem/audit-event-type#rest "Restful Operation"
* subtype = http://hl7.org/fhir/restful-interaction#read "read"
* action = #R
* recorded = "2026-07-02T10:00:00Z"
* outcome = #0
* agent[0].type = http://terminology.hl7.org/CodeSystem/extra-security-role-type#humanuser "human user"
* agent[0].who.display = "Pseudonymous clinician actor"
* agent[0].requestor = true
* source.observer.display = "TrustEvidence reference implementation"
* source.type = http://terminology.hl7.org/CodeSystem/security-source-type#4 "Application Server"
* entity[0].what.reference = "Observation/observation-cgm-aggregate"
* entity[0].detail[0].type = "payload_hash"
* entity[0].detail[0].valueString = "sha256:example"
