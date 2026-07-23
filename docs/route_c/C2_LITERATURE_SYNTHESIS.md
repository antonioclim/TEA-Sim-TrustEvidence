# C2 direct literature synthesis and hostile novelty test

## Purpose

This document records the literature conclusion that may support the Route C manuscript. It is deliberately narrower than a narrative literature review: each stream identifies what established work already provides, what remains a defensible project contribution and which claims must be removed.

The source registry is `VERIFIED_REFERENCE_REGISTRY.csv`. Official standards are treated as the primary authority for their own capabilities. Peer-reviewed direct comparators are used to position the healthcare problem and implementation choices.

## Healthcare audit representation already exists

FHIR R4 `AuditEvent` is explicitly designed to record security- and privacy-relevant events. It already supports event type, action, occurrence and recording times, outcome, purpose, one or more agents, applicable policy URIs, reporting source and affected entities. It also states that audited entity references should be version specific. `Provenance` records entities, agents and activities involved in creating, revising, signing, importing or transforming a resource version. `Consent` records healthcare-consumer choices involving recipients, actions, purposes, periods and policy context, and recognises that partial consent derivatives may refer back to protected source directives.

Consequently, the manuscript must not claim that FHIR lacks the actor, purpose, policy, Consent or provenance concepts needed for auditability. The legitimate question is not whether these facts can be represented, but which subset should be required and portable for a particular cross-organisational accountability dispute, which source material should remain under custody and how the structured projection relates to the exact signed statement.

IHE Basic Audit Log Patterns 1.1.4 further weakens any broad novelty claim. BALP is a current published FHIR R4 implementation guide with reusable AuditEvent patterns for RESTful activity, SAML and OAuth token use, consent-authorised decisions and privacy disclosure. Route C must therefore compare its disclosure projection to the applicable BALP profiles and use `BALP-facing` until the exact profile combination passes the official validation toolchain.

### Literature conclusion

FHIR and BALP are the representation substrate, not an inferior baseline invented for comparison. TrustEvidence can add a bounded selection and binding profile only if C3 demonstrates that:

- the field set is justified by frozen accountability questions;
- lower-exposure references or commitments replace unnecessary values;
- exact signed bytes are preserved separately from FHIR serialisation;
- the FHIR projection retains all mandatory semantics;
- applicable profile constraints are passed rather than merely cited.

## Consent lifecycle and interoperability are established work

MAGIC, the gICS FHIR gateway and Consent Management 2.0 demonstrate a substantial lineage of FHIR-based consent management. The literature covers structured consent, exchange across university-medicine networks, withdrawal, refusal, objection, aggregated consent status, historical state, standardised search and practical implementation issues.

Therefore, Route C cannot claim novelty from:

- using a FHIR Consent resource;
- recording consent state;
- representing withdrawal or revocation;
- exchanging consent metadata;
- separating a consent derivative from a protected source document.

The defensible addition is narrower: the executed event envelope binds a particular Consent reference, version and event-time state to the actor, organisation, purpose, policy, decision, resource version and provenance facts required by the declared dispute. Consent state and access-decision outcome must remain separate fields.

## Healthcare blockchain and cryptographic integration are established work

MedRec introduced blockchain-mediated medical-data access and permission management while records remained outside the ledger. FHIRChain combined FHIR, digital health identities and blockchain-mediated sharing. More recent work has implemented blockchain-backed EHR access auditing with actor, time, purpose and access-policy verification. A 2025 systematic review describes a large and still predominantly proof-of-concept literature on privacy-preserving blockchain healthcare data sharing, including on-chain/off-chain partitioning, encryption, access control and verification mechanisms.

Therefore, Route C cannot claim novelty from:

- keeping clinical data off chain;
- placing hashes or references in a ledger;
- signing healthcare events;
- recording who accessed what, when and for which purpose;
- using a blockchain or Merkle tree for tamper evidence;
- combining FHIR and cryptography.

Wüst and Gervais further require the manuscript to justify why any ledger-like mechanism is proportionate rather than treating decentralisation as an intrinsic benefit. Route C has only a local A2 reference backend. It will not claim decentralised consensus, public witnessing, production persistence or superiority over a conventional audit store.

## Generic transparency standards now define the primitives

Certificate Transparency v2 defines the Merkle inclusion and consistency algorithmic lineage relevant to the current local tree. RFC 9943 defines a generic architecture for single-issuer signed-statement transparency. RFC 9942 defines standards-track COSE receipts for verifiable-data-structure properties, including RFC9162_SHA256 inclusion and consistency.

These 2026 RFCs require particularly strict wording. The current implementation uses signed JSON envelopes and a project-specific JSON receipt. It does not use the COSE protected headers, receipt structures, media types or profile requirements defined by RFC 9942, and it is not a SCITT implementation.

Therefore:

- `signed statement`, `issuer`, `transparency service`, `receipt`, `inclusion proof` and `consistency proof` are not TrustEvidence inventions;
- the local object must be called a `project-specific local A2 Merkle receipt`;
- SCITT and COSE Receipts are direct comparators and future alignment directions, not executed claims;
- inclusion must not be described as event completeness;
- consistency relative to retained state must not be described as universal non-equivocation.

## The defensible Route C gap

After adverse comparison, the residual problem is specific but non-trivial:

> Existing healthcare standards can represent rich event, Consent and provenance context, and existing cryptographic standards can authenticate statements or prove properties of log states. They do not, by themselves, decide the healthcare-specific evidence/custody boundary for a declared cross-organisational dispute or test the exact relationship between that boundary, a signed semantic envelope, a FHIR projection and a bounded backend verifier.

The Route C contribution is therefore the operationalised sequence:

```text
accountability questions
→ candidate field inventory
→ portable / referenced / committed / excluded decision
→ closed semantic envelope
→ deterministic canonical bytes
→ issuer signature
→ FHIR R4/BALP-facing projection
→ optional project-specific local receipt
→ property-specific verification report
```

The contribution survives only if C3–C6 execute this sequence without raw clinical-payload leakage, semantic loss, accepted critical mutations or irreproducible results.

## Hostile novelty test

### Attack 1 — “Everything is already in FHIR”

**Substantially true at the element level.** AuditEvent, Provenance and Consent cover much of the required representation. Route C is not defensible as a new information model merely because it renames these fields.

**Residual defence:** the project contributes a mandatory field-selection and custody profile tied to a signed non-FHIR semantic core, exact resource/Consent/policy versions, commitment rules and an executed cross-layer mapping. This defence fails if C3 shows arbitrary extensions or semantic loss.

### Attack 2 — “BALP already covers the workflow”

**Substantially true for the FHIR disclosure and authorisation audit patterns.** Route C should derive from or validate against the applicable BALP profiles wherever feasible.

**Residual defence:** BALP is the structured audit pattern; TrustEvidence adds the project-defined portable/reference/commitment/exclusion decision and exact signed-envelope/backend relationship. This defence fails if the manuscript claims a replacement for BALP.

### Attack 3 — “SCITT and COSE Receipts already define the architecture”

**True for generic signed-statement transparency and receipt mechanics.** Route C cannot claim these primitives.

**Residual defence:** healthcare semantics, Consent/policy/resource-version selection, custody decisions and the FHIR projection are outside those generic RFCs. Route C does not claim conformance and uses them as a precise novelty boundary.

### Attack 4 — “MedRec, FHIRChain and later healthcare ledgers already keep data off chain”

**True.** Off-chain clinical records and on-chain permissions or commitments are established patterns.

**Residual defence:** Route C is not a data-sharing ledger. It targets minimised portable audit evidence, separates issuer evidence from backend evidence and evaluates a field-level custody boundary. The defence fails if the paper markets the Merkle tree as the main innovation.

### Attack 5 — “The JSON schema is arbitrary”

**Currently plausible.** A closed schema alone is not design knowledge.

**Required defence:** C3 must tie every mandatory field to an accountability question, a lower-exposure alternative, a FHIR path and a falsification test. Redundant fields must be removed or made profile-specific.

### Attack 6 — “Claim demotion is ordinary research hygiene”

**Correct.** Claim–evidence mapping and demotion are valuable governance controls but not the primary scientific contribution.

**Decision:** claim governance moves to reproducibility and response-to-reviewers material. It may support trustworthiness of reporting but will not anchor the title, abstract or main contribution.

### Attack 7 — “The evaluation proves only that the author's implementation accepts its own examples”

**Currently valid for the legacy submission.**

**Required defence:** C3 introduces official FHIR validators and negative examples; C4 broadens controlled mutations; C5 preregisters paired independent runs; C6 performs hosted and fresh-extraction release checks. The paper must still call the result bounded technical efficacy.

## Final contribution statement for the manuscript

> TrustEvidence contributes a healthcare-specific, field-level audit-evidence boundary and an executable reference profile that binds versioned actor, organisation, purpose, Consent, policy, decision, resource and provenance context while the underlying clinical payload remains under source custody. FHIR and BALP supply the structured healthcare representation, and established cryptographic mechanisms supply canonicalisation, signatures and Merkle-proof primitives. The contribution is the bounded selection, cross-layer binding and executed evaluation of these elements, not a new standard or cryptographic primitive.

## Claims removed by C2

The revised manuscript must remove or avoid:

- `new architecture` without the qualifier `reference profile`;
- `novel Merkle backend`;
- `FHIR cannot represent portable audit evidence`;
- `blockchain keeps clinical data private`;
- `receipt proves a complete audit trail`;
- `signature proves that the clinical event occurred`;
- `Consent status proves that access was authorised`;
- `TrustEvidence improves organisational trust`;
- `claim demotion is the most important practical result`;
- any priority or universal coverage claim.

## Remaining literature work for C7

Before manuscript freeze:

1. export final APA metadata for any dataset records actually retained;
2. verify page ranges and all author names from DOI metadata;
3. construct the paragraph-level claim–citation matrix;
4. check retractions, corrections and version-of-record status;
5. remove conditional sources not used by the executed Route C case;
6. ensure every recent citation advances a direct analytical comparison rather than satisfying a date quota.
