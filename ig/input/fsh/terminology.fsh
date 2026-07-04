CodeSystem: TEEvidenceClassCS
Id: te-evidence-class
Title: "TrustEvidence Evidence Class CodeSystem"
Description: "Codes for TrustEvidence artefact classes. This is a draft FHIR IG draft terminology system and is not a legal or security classification."
* ^url = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/CodeSystem/te-evidence-class"
* ^status = #draft
* ^experimental = true
* ^caseSensitive = true
* ^content = #complete
* #consent-receipt "Consent receipt" "Evidence that a consent state or consent grant was received by the emitting system."
* #access-attestation "Access attestation" "Evidence that a read, query, disclosure or other access event occurred or was attempted."
* #provenance-assertion "Provenance assertion" "Evidence about an actor, entity, transformation or process involved in producing or modifying information."
* #integrity-anchor "Integrity anchor" "Evidence that binds an off-chain payload, aggregate or policy state to a digest or checkpoint."
* #consent-state-transition "Consent-state transition" "Evidence that a consent state was revoked, superseded or otherwise changed."
* #emission-failure "Emission failure" "Evidence that an in-scope event crossed the boundary but could not be accepted by the intended backend."

ValueSet: TEEvidenceClassVS
Id: te-evidence-class
Title: "TrustEvidence Evidence Class ValueSet"
Description: "All draft evidence-class codes defined by TrustEvidence."
* ^url = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/ValueSet/te-evidence-class"
* ^status = #draft
* ^experimental = true
* include codes from system $TEEvidenceClassCS

CodeSystem: TEBackendTypeCS
Id: te-backend-type
Title: "TrustEvidence Backend Type CodeSystem"
Description: "Codes for evidence-storage backends used by the TrustEvidence evaluation and interface specification."
* ^url = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/CodeSystem/te-backend-type"
* ^status = #draft
* ^experimental = true
* ^caseSensitive = true
* ^content = #complete
* #a1-central-audit "A1 central audit" "Single controlled audit repository."
* #a2-merkle-hash-log "A2 Merkle hash log" "Append-only hash log with inclusion and consistency proofs."
* #a3-ledger-like "A3 ledger-like backend" "Replicated evidence backend under an explicit quorum/finality assumption."
* #trillian-transparency-log "Trillian transparency log" "External transparency-log baseline consumed through a TrustEvidence personality."
* #rekor-transparency-log "Rekor transparency log" "External Sigstore/Rekor transparency-log baseline consumed through its REST interface."

ValueSet: TEBackendTypeVS
Id: te-backend-type
Title: "TrustEvidence Backend Type ValueSet"
Description: "All draft evidence-backend codes defined by TrustEvidence."
* ^url = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/ValueSet/te-backend-type"
* ^status = #draft
* ^experimental = true
* include codes from system $TEBackendTypeCS
