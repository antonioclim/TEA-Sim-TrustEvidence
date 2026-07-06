Extension: EvidenceAnchor
Id: evidence-anchor
Title: "TrustEvidence Evidence Anchor"
Description: "Carries verifiable evidence-backend metadata for an AuditEvent or Provenance resource. The extension records commitments and proof references; it does not carry the clinical payload."
* ^url = "https://antonioclim.github.io/TEA-Sim/fhir/trustevidence/StructureDefinition/evidence-anchor"
* ^status = #draft
* ^experimental = true
* ^context[0].type = #element
* ^context[0].expression = "AuditEvent"
* ^context[1].type = #element
* ^context[1].expression = "Provenance"
* extension contains
    logIdentity 1..1 MS and
    treeSize 0..1 MS and
    rootHash 0..1 MS and
    inclusionProofRef 0..1 MS and
    consistencyProofRef 0..1 MS and
    algorithm 1..1 MS and
    backendType 1..1 MS and
    checkpointId 0..1 MS and
    checkpointSignature 0..1 MS and
    failureCode 0..1 MS
* extension[logIdentity] ^short = "Evidence-log or backend identity"
* extension[logIdentity].value[x] only uri
* extension[treeSize] ^short = "Tree size or monotone checkpoint size"
* extension[treeSize].value[x] only unsignedInt
* extension[rootHash] ^short = "Committed root hash or checkpoint digest"
* extension[rootHash].value[x] only base64Binary
* extension[inclusionProofRef] ^short = "Reference to inclusion-proof material"
* extension[inclusionProofRef].value[x] only uri
* extension[consistencyProofRef] ^short = "Reference to consistency-proof material"
* extension[consistencyProofRef].value[x] only uri
* extension[algorithm] ^short = "Hash, signature or proof algorithm identifier"
* extension[algorithm].value[x] only Coding
* extension[backendType] ^short = "Evidence-storage backend type"
* extension[backendType].value[x] only Coding
* extension[backendType].valueCoding from $TEBackendTypeVS (required)
* extension[checkpointId] ^short = "Checkpoint identifier"
* extension[checkpointId].value[x] only Identifier
* extension[checkpointSignature] ^short = "Backend checkpoint signature when supplied"
* extension[checkpointSignature].value[x] only Signature
* extension[failureCode] ^short = "TrustEvidence failure code when the artefact records a failed path"
* extension[failureCode].value[x] only code
