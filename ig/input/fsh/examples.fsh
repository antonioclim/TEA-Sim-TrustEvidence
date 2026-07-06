// draft examples. All fixture numerals, timestamps, identifiers and hashes are [ASSUMED:example-fixture].

Instance: TEAuditEventW1
InstanceOf: TEAuditEvent
Usage: #example
Title: "TrustEvidence AuditEvent W1"
Description: "Example AuditEvent for Direct-care access attestation; fixture values are not production measurements."
* id = "te-audit-w1"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:a1-central-audit:w1"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1001 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "AQIDBAUGBwgJCgsMDQ4PEA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w1"
* extension[evidenceAnchor].extension[consistencyProofRef].valueUri = "urn:te:proof:consistency:w1"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#a1-central-audit "a1-central-audit"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.system = "urn:te:checkpoint"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.value = "cp-w1"
* type = $AuditEventType#rest "RESTful Operation"
* subtype = $RestfulInteraction#read "read"
* action = #R
* period.start = "2026-07-03T10:01:00Z" // [ASSUMED:example-fixture]
* recorded = "2026-07-03T10:01:00Z" // [ASSUMED:example-fixture]
* outcome = #0
* purposeOfEvent[0] = $PurposeOfUse#TREAT "TREAT"
* agent[0].who.identifier.system = "urn:te:actor"
* agent[0].who.identifier.value = "actor-w1"
* agent[0].requestor = true
* agent[0].policy = "urn:te:policy:w1"
* source.observer.identifier.system = "urn:te:source"
* source.observer.identifier.value = "hapi-emitter"
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w1"
* entity[0].type = $TEEvidenceClassCS#access-attestation "access-attestation"
* entity[0].role = $ObjectRole#4 "domain resource" // [ASSUMED:example-fixture]
* entity[0].detail[0].type = "payload-commitment"
* entity[0].detail[0].valueString = "sha256:w1-payload-fixture"
* entity[0].detail[1].type = "policy-version"
* entity[0].detail[1].valueString = "policy-w1-v1"

Instance: TEProvenanceW1
InstanceOf: TEProvenance
Usage: #example
Title: "TrustEvidence Provenance W1"
Description: "Example Provenance companion for Direct-care access attestation; fixture values are not production measurements."
* id = "te-provenance-w1"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:a1-central-audit:w1"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1001 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "AQIDBAUGBwgJCgsMDQ4PEA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w1"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#a1-central-audit "a1-central-audit"
* target[0] = Reference(Observation/w1-observation-aggregate)
* recorded = "2026-07-03T10:01:00Z" // [ASSUMED:example-fixture]
* policy[0] = "urn:te:policy:w1"
* activity = $TEEvidenceClassCS#access-attestation "access-attestation"
* agent[0].who.identifier.system = "urn:te:emitter"
* agent[0].who.identifier.value = "emitter-w1"
* entity[0].role = #source
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w1"

Instance: TEAuditEventW2
InstanceOf: TEAuditEvent
Usage: #example
Title: "TrustEvidence AuditEvent W2"
Description: "Example AuditEvent for Interorganisational shared-care query; fixture values are not production measurements."
* id = "te-audit-w2"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:a2-merkle-hash-log:w2"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1002 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "ERITFBUWFxgZGhscHR4fIA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w2"
* extension[evidenceAnchor].extension[consistencyProofRef].valueUri = "urn:te:proof:consistency:w2"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#a2-merkle-hash-log "a2-merkle-hash-log"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.system = "urn:te:checkpoint"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.value = "cp-w2"
* type = $AuditEventType#rest "RESTful Operation"
* subtype = $RestfulInteraction#create "create"
* action = #C
* period.start = "2026-07-03T10:02:00Z" // [ASSUMED:example-fixture]
* recorded = "2026-07-03T10:02:00Z" // [ASSUMED:example-fixture]
* outcome = #0
* purposeOfEvent[0] = $PurposeOfUse#TREAT "TREAT"
* agent[0].who.identifier.system = "urn:te:actor"
* agent[0].who.identifier.value = "actor-w2"
* agent[0].requestor = true
* agent[0].policy = "urn:te:policy:w2"
* source.observer.identifier.system = "urn:te:source"
* source.observer.identifier.value = "hapi-emitter"
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w2"
* entity[0].type = $TEEvidenceClassCS#access-attestation "access-attestation"
* entity[0].role = $ObjectRole#4 "domain resource" // [ASSUMED:example-fixture]
* entity[0].detail[0].type = "payload-commitment"
* entity[0].detail[0].valueString = "sha256:w2-payload-fixture"
* entity[0].detail[1].type = "policy-version"
* entity[0].detail[1].valueString = "policy-w2-v1"

Instance: TEProvenanceW2
InstanceOf: TEProvenance
Usage: #example
Title: "TrustEvidence Provenance W2"
Description: "Example Provenance companion for Interorganisational shared-care query; fixture values are not production measurements."
* id = "te-provenance-w2"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:a2-merkle-hash-log:w2"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1002 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "ERITFBUWFxgZGhscHR4fIA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w2"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#a2-merkle-hash-log "a2-merkle-hash-log"
* target[0] = Reference(AuditEvent/te-audit-w2)
* recorded = "2026-07-03T10:02:00Z" // [ASSUMED:example-fixture]
* policy[0] = "urn:te:policy:w2"
* activity = $TEEvidenceClassCS#access-attestation "access-attestation"
* agent[0].who.identifier.system = "urn:te:emitter"
* agent[0].who.identifier.value = "emitter-w2"
* entity[0].role = #source
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w2"

Instance: TEAuditEventW3
InstanceOf: TEAuditEvent
Usage: #example
Title: "TrustEvidence AuditEvent W3"
Description: "Example AuditEvent for Secondary-use provenance assertion; fixture values are not production measurements."
* id = "te-audit-w3"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:trillian-transparency-log:w3"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1003 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "ISIjJCUmJygpKissLS4vMA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w3"
* extension[evidenceAnchor].extension[consistencyProofRef].valueUri = "urn:te:proof:consistency:w3"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#trillian-transparency-log "trillian-transparency-log"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.system = "urn:te:checkpoint"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.value = "cp-w3"
* type = $AuditEventType#rest "RESTful Operation"
* subtype = $RestfulInteraction#update "update"
* action = #U
* period.start = "2026-07-03T10:03:00Z" // [ASSUMED:example-fixture]
* recorded = "2026-07-03T10:03:00Z" // [ASSUMED:example-fixture]
* outcome = #0
* purposeOfEvent[0] = $PurposeOfUse#HRESCH "HRESCH"
* agent[0].who.identifier.system = "urn:te:actor"
* agent[0].who.identifier.value = "actor-w3"
* agent[0].requestor = true
* agent[0].policy = "urn:te:policy:w3"
* source.observer.identifier.system = "urn:te:source"
* source.observer.identifier.value = "hapi-emitter"
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w3"
* entity[0].type = $TEEvidenceClassCS#provenance-assertion "provenance-assertion"
* entity[0].role = $ObjectRole#4 "domain resource" // [ASSUMED:example-fixture]
* entity[0].detail[0].type = "payload-commitment"
* entity[0].detail[0].valueString = "sha256:w3-payload-fixture"
* entity[0].detail[1].type = "policy-version"
* entity[0].detail[1].valueString = "policy-w3-v1"

Instance: TEProvenanceW3
InstanceOf: TEProvenance
Usage: #example
Title: "TrustEvidence Provenance W3"
Description: "Example Provenance companion for Secondary-use provenance assertion; fixture values are not production measurements."
* id = "te-provenance-w3"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:trillian-transparency-log:w3"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1003 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "ISIjJCUmJygpKissLS4vMA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w3"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#trillian-transparency-log "trillian-transparency-log"
* target[0] = Reference(Provenance/w3-secondary-use-source)
* recorded = "2026-07-03T10:03:00Z" // [ASSUMED:example-fixture]
* policy[0] = "urn:te:policy:w3"
* activity = $TEEvidenceClassCS#provenance-assertion "provenance-assertion"
* agent[0].who.identifier.system = "urn:te:emitter"
* agent[0].who.identifier.value = "emitter-w3"
* entity[0].role = #source
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w3"

Instance: TEAuditEventW4
InstanceOf: TEAuditEvent
Usage: #example
Title: "TrustEvidence AuditEvent W4"
Description: "Example AuditEvent for High-dispute consent-state transition; fixture values are not production measurements."
* id = "te-audit-w4"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:a3-ledger-like:w4"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1004 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "MTIzNDU2Nzg5Ojs8PT4/QA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w4"
* extension[evidenceAnchor].extension[consistencyProofRef].valueUri = "urn:te:proof:consistency:w4"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#a3-ledger-like "a3-ledger-like"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.system = "urn:te:checkpoint"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.value = "cp-w4"
* type = $AuditEventType#rest "RESTful Operation"
* subtype = $RestfulInteraction#update "update"
* action = #U
* period.start = "2026-07-03T10:04:00Z" // [ASSUMED:example-fixture]
* recorded = "2026-07-03T10:04:00Z" // [ASSUMED:example-fixture]
* outcome = #0
* purposeOfEvent[0] = $PurposeOfUse#TREAT "TREAT"
* agent[0].who.identifier.system = "urn:te:actor"
* agent[0].who.identifier.value = "actor-w4"
* agent[0].requestor = true
* agent[0].policy = "urn:te:policy:w4"
* source.observer.identifier.system = "urn:te:source"
* source.observer.identifier.value = "hapi-emitter"
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w4"
* entity[0].type = $TEEvidenceClassCS#consent-state-transition "consent-state-transition"
* entity[0].role = $ObjectRole#4 "domain resource" // [ASSUMED:example-fixture]
* entity[0].detail[0].type = "payload-commitment"
* entity[0].detail[0].valueString = "sha256:w4-payload-fixture"
* entity[0].detail[1].type = "policy-version"
* entity[0].detail[1].valueString = "policy-w4-v1"

Instance: TEProvenanceW4
InstanceOf: TEProvenance
Usage: #example
Title: "TrustEvidence Provenance W4"
Description: "Example Provenance companion for High-dispute consent-state transition; fixture values are not production measurements."
* id = "te-provenance-w4"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:a3-ledger-like:w4"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1004 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "MTIzNDU2Nzg5Ojs8PT4/QA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w4"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#a3-ledger-like "a3-ledger-like"
* target[0] = Reference(Consent/w4-consent-transition)
* recorded = "2026-07-03T10:04:00Z" // [ASSUMED:example-fixture]
* policy[0] = "urn:te:policy:w4"
* activity = $TEEvidenceClassCS#consent-state-transition "consent-state-transition"
* agent[0].who.identifier.system = "urn:te:emitter"
* agent[0].who.identifier.value = "emitter-w4"
* entity[0].role = #source
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w4"

Instance: TEAuditEventW5
InstanceOf: TEAuditEvent
Usage: #example
Title: "TrustEvidence AuditEvent W5"
Description: "Example AuditEvent for Cryptographic-agility integrity anchor; fixture values are not production measurements."
* id = "te-audit-w5"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:rekor-transparency-log:w5"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1005 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "QUJDREVGR0hJSktMTU5PUA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w5"
* extension[evidenceAnchor].extension[consistencyProofRef].valueUri = "urn:te:proof:consistency:w5"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#rekor-transparency-log "rekor-transparency-log"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.system = "urn:te:checkpoint"
* extension[evidenceAnchor].extension[checkpointId].valueIdentifier.value = "cp-w5"
* type = $AuditEventType#rest "RESTful Operation"
* subtype = $RestfulInteraction#read "read"
* action = #R
* period.start = "2026-07-03T10:05:00Z" // [ASSUMED:example-fixture]
* recorded = "2026-07-03T10:05:00Z" // [ASSUMED:example-fixture]
* outcome = #0
* purposeOfEvent[0] = $PurposeOfUse#TREAT "TREAT"
* agent[0].who.identifier.system = "urn:te:actor"
* agent[0].who.identifier.value = "actor-w5"
* agent[0].requestor = true
* agent[0].policy = "urn:te:policy:w5"
* source.observer.identifier.system = "urn:te:source"
* source.observer.identifier.value = "hapi-emitter"
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w5"
* entity[0].type = $TEEvidenceClassCS#integrity-anchor "integrity-anchor"
* entity[0].role = $ObjectRole#4 "domain resource" // [ASSUMED:example-fixture]
* entity[0].detail[0].type = "payload-commitment"
* entity[0].detail[0].valueString = "sha256:w5-payload-fixture"
* entity[0].detail[1].type = "policy-version"
* entity[0].detail[1].valueString = "policy-w5-v1"

Instance: TEProvenanceW5
InstanceOf: TEProvenance
Usage: #example
Title: "TrustEvidence Provenance W5"
Description: "Example Provenance companion for Cryptographic-agility integrity anchor; fixture values are not production measurements."
* id = "te-provenance-w5"
* extension[evidenceAnchor].extension[logIdentity].valueUri = "urn:te:log:rekor-transparency-log:w5"
* extension[evidenceAnchor].extension[treeSize].valueUnsignedInt = 1005 // [ASSUMED:example-fixture]
* extension[evidenceAnchor].extension[rootHash].valueBase64Binary = "QUJDREVGR0hJSktMTU5PUA=="
* extension[evidenceAnchor].extension[inclusionProofRef].valueUri = "urn:te:proof:inclusion:w5"
* extension[evidenceAnchor].extension[algorithm].valueCoding.system = "urn:te:algorithm"
* extension[evidenceAnchor].extension[algorithm].valueCoding.code = #sha-256-merkle
* extension[evidenceAnchor].extension[backendType].valueCoding = $TEBackendTypeCS#rekor-transparency-log "rekor-transparency-log"
* target[0] = Reference(Observation/w5-observation-aggregate)
* recorded = "2026-07-03T10:05:00Z" // [ASSUMED:example-fixture]
* policy[0] = "urn:te:policy:w5"
* activity = $TEEvidenceClassCS#integrity-anchor "integrity-anchor"
* agent[0].who.identifier.system = "urn:te:emitter"
* agent[0].who.identifier.value = "emitter-w5"
* entity[0].role = #source
* entity[0].what.identifier.system = "urn:te:payload-ref"
* entity[0].what.identifier.value = "payload-ref-w5"

