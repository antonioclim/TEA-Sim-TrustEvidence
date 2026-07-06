Extension: TEBackendType
Id: te-backend-type
Title: "TrustEvidence backend type"
Description: "Evidence backend class: A1 central audit, A2 append-only Merkle/hash log or A3 transparency/ledger-like backend."
* value[x] only code
* valueCode from TEBackendTypeVS (required)

Extension: TEEvidenceHash
Id: te-evidence-hash
Title: "TrustEvidence canonical evidence hash"
Description: "SHA-256 commitment to the canonical TrustEvidence object or payload reference."
* value[x] only string

Extension: TEPolicyVersion
Id: te-policy-version
Title: "TrustEvidence policy version"
Description: "Policy or consent-policy version applicable at the time the evidence artefact was emitted."
* value[x] only string

Extension: TEReceiptRoot
Id: te-receipt-root
Title: "TrustEvidence receipt root"
Description: "Merkle/transparency root or equivalent backend receipt root."
* value[x] only string

ValueSet: TEBackendTypeVS
Id: te-backend-type-vs
Title: "TrustEvidence backend type value set"
* TEBackendTypeCS#A1_POSTGRES
* TEBackendTypeCS#A2_MERKLE
* TEBackendTypeCS#A3_REKOR
* TEBackendTypeCS#A3_TRILLIAN
* TEBackendTypeCS#A3_FABRIC

CodeSystem: TEBackendTypeCS
Id: te-backend-type-cs
Title: "TrustEvidence backend type code system"
* #A1_POSTGRES "A1 PostgreSQL central audit"
* #A2_MERKLE "A2 local append-only Merkle log"
* #A3_REKOR "A3 Rekor transparency-log pathway"
* #A3_TRILLIAN "A3 Trillian transparency-log pathway"
* #A3_FABRIC "A3 Fabric ledger-like pathway"
