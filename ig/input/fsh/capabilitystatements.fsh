// draft CapabilityStatements. Requirements statements only; not deployed endpoint evidence.

Instance: TEEmitterCapabilityStatement
InstanceOf: CapabilityStatement
Usage: #definition
Title: "TrustEvidence Emitter CapabilityStatement"
Description: "Requirements-style CapabilityStatement for an actor that emits TrustEvidence AuditEvent and Provenance resources. This draft does not describe an actual deployed endpoint."
* id = "te-emitter-capabilitystatement"
* url = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/CapabilityStatement/te-emitter"
* version = "0.2.0"
* name = "TEEmitterCapabilityStatement"
* title = "TrustEvidence Emitter CapabilityStatement"
* status = #draft
* experimental = true
* date = "2026-07-03"
* publisher = "Antonio Clim"
* description = "An emitting actor SHALL be able to create TrustEvidence AuditEvent resources and their Provenance companions, populate the evidence-anchor extension, and preserve the boundary between clinical payload repositories and evidence artefacts."
* kind = #requirements
* fhirVersion = #4.0.1
* format[0] = #json
* implementationGuide[0] = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/ImplementationGuide/trustevidence.fhir.uv"
* rest[0].mode = #client
* rest[0].documentation = "Client requirements for emitting TrustEvidence resources to a FHIR endpoint or audit repository endpoint."
* rest[0].security.description = "The emitter SHALL use deployment-appropriate authentication, authorisation, transport protection and audit governance. This CapabilityStatement is not by itself an ATNA conformance claim."
* rest[0].resource[0].type = #AuditEvent
* rest[0].resource[0].supportedProfile[0] = Canonical(TEAuditEvent)
* rest[0].resource[0].interaction[0].code = #create
* rest[0].resource[1].type = #Provenance
* rest[0].resource[1].supportedProfile[0] = Canonical(TEProvenance)
* rest[0].resource[1].interaction[0].code = #create

Instance: TEVerifierCapabilityStatement
InstanceOf: CapabilityStatement
Usage: #definition
Title: "TrustEvidence Verifier CapabilityStatement"
Description: "Requirements-style CapabilityStatement for an actor that retrieves TrustEvidence AuditEvent and Provenance resources and verifies their evidence-anchor material. This draft does not describe an actual deployed endpoint."
* id = "te-verifier-capabilitystatement"
* url = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/CapabilityStatement/te-verifier"
* version = "0.2.0"
* name = "TEVerifierCapabilityStatement"
* title = "TrustEvidence Verifier CapabilityStatement"
* status = #draft
* experimental = true
* date = "2026-07-03"
* publisher = "Antonio Clim"
* description = "A verifying actor SHALL be able to retrieve TrustEvidence AuditEvent and Provenance resources, inspect EvidenceAnchor extension content, and invoke out-of-band proof verification according to the TrustEvidence specification."
* kind = #requirements
* fhirVersion = #4.0.1
* format[0] = #json
* implementationGuide[0] = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/ImplementationGuide/trustevidence.fhir.uv"
* rest[0].mode = #client
* rest[0].documentation = "Client requirements for an auditor or verifier that queries FHIR resources and then verifies evidence material offline or through backend-specific online checks."
* rest[0].security.description = "The verifier SHALL respect deployment access-control, patient privacy and audit-governance requirements. Possession of a proof reference does not authorise access to clinical payloads."
* rest[0].resource[0].type = #AuditEvent
* rest[0].resource[0].supportedProfile[0] = Canonical(TEAuditEvent)
* rest[0].resource[0].interaction[0].code = #read
* rest[0].resource[0].interaction[1].code = #search-type
* rest[0].resource[1].type = #Provenance
* rest[0].resource[1].supportedProfile[0] = Canonical(TEProvenance)
* rest[0].resource[1].interaction[0].code = #read
* rest[0].resource[1].interaction[1].code = #search-type
