# Route C scientific identity card

## Decision status

Frozen for the bounded JCIS revision unless C3 or C4 falsifies a mandatory design assumption.

## Canonical manuscript title

**Designing Portable Audit Evidence for Health Information Exchange**

Word count: eight.

## One-sentence identity

TrustEvidence is a healthcare-specific audit-evidence boundary and executable reference profile that classifies accountability facts as portable, referenced, cryptographically committed or excluded, then binds the selected facts to a signed evidence envelope, a FHIR R4/BALP-facing projection and a bounded local receipt-verification path.

## Primary artefact identity

The primary artefact is a **boundary model**.

The boundary model answers a field-level design question: when evidence about a healthcare information event crosses an organisational boundary, which facts should travel, which facts should remain under source custody but be referenced, which facts should be represented only by a cryptographic commitment and which facts should be excluded from the portable layer?

The secondary artefact is an **executable reference profile** consisting of:

- a closed TrustEvidence JSON Schema;
- an application-profile canonicalisation rule;
- issuer signatures;
- nonce-based payload commitments;
- a FHIR R4/BALP-facing projection;
- a project-specific local A2 Merkle receipt and retained-checkpoint verifier;
- positive, negative and mutation corpora;
- reproducibility and measurement protocols.

The manuscript must not relabel this combination as a new healthcare standard, a generic transparency protocol, a production system or a mature design theory.

## Problem construct

### Audit-evidence interoperability

For Route C, **audit-evidence interoperability** means the capacity of organisations to exchange and independently inspect a declared set of accountability facts without copying the underlying clinical payload and without treating representation, signature or backend inclusion as proof of clinical truth.

This construct is narrower than clinical semantic interoperability and broader than local log retention.

### Unit of design

The unit of design is the **portable evidence envelope for one declared event**, including its relationships to:

- the actor and issuing organisation;
- the source and recipient organisations;
- event purpose and outcome;
- Consent reference, version and state;
- policy reference, version and optional digest;
- versioned clinical-resource references and commitments;
- provenance activity and agents;
- issuer signature;
- backend evidence, where present.

## Four boundary classes

1. **Portable** — accountability facts that may be carried in the envelope and its FHIR projection.
2. **Referenced** — facts needed for reconstruction but retained under an authorised source custodian.
3. **Committed** — bytes whose integrity is bound cryptographically without disclosure in the portable layer.
4. **Excluded** — direct identifiers, raw clinical values, credentials, private keys, commitment nonces and other material not justified by the declared accountability questions.

`Governance-only` is not a fifth portable class. Governance context may inform local interpretation, but it is not automatically part of the signed portable statement.

## Contribution claim

The Route C contribution is not any individual primitive. FHIR resources, BALP AuditEvent patterns, JSON canonicalisation, digital signatures, Merkle trees, signed statements and verifiable-data-structure receipts all have independent prior specifications or implementations.

The contribution is the **healthcare-specific integration and operationalisation of a field-level evidence/custody decision**:

> accountability questions → field classification → minimised signed envelope → FHIR projection → optional backend evidence → property-specific verification

The distinctive combination evaluated in Route C is:

- explicit portable/referenced/committed/excluded classification;
- actor, organisation, purpose and outcome context;
- versioned Consent and policy binding;
- versioned clinical-resource reference and payload commitment;
- provenance linkage;
- strict separation of issuer authentication from backend assurance;
- strict separation of inclusion from completeness;
- a concrete synthetic cross-organisational healthcare case;
- bounded official validation, mutation and local incremental-cost evidence.

No priority or “first” claim is made. The novelty claim is comparative and bounded to the verified literature set in `VERIFIED_REFERENCE_REGISTRY.csv`.

## What established standards already provide

### FHIR R4

- `AuditEvent` records security- or privacy-relevant events, including agents, entities, purposes and outcomes.
- `Provenance` records entities, agents and activities involved in creating, revising, deleting or signing resource versions.
- `Consent` represents healthcare-consumer choices, policy context, permitted or denied actions, purposes, recipients and periods.

### IHE BALP 1.1.4

BALP defines reusable FHIR R4 `AuditEvent` patterns for RESTful operations, security-token use, consent-authorised decisions and privacy disclosures. Its current published guide is a content profile based on FHIR 4.0.1.

### SCITT and COSE Receipts

RFC 9943 defines a generic architecture for single-issuer signed-statement transparency. RFC 9942 defines COSE receipt structures for proving properties of verifiable data structures, including Merkle inclusion and consistency. Route C does not implement or claim conformance to either RFC.

## What TrustEvidence adds in Route C

TrustEvidence adds a project-defined healthcare profile that decides and tests:

- which accountability facts are necessary for the declared dispute questions;
- which of those facts may cross organisations;
- how Consent, policy, provenance and resource versions are bound without copying the clinical payload;
- how the same semantic core is projected into FHIR resources;
- how issuer-authentication evidence is kept distinct from a local backend receipt;
- what the supplied validators, mutations and local experiment actually establish.

## What TrustEvidence does not add

TrustEvidence does not add:

- a new FHIR resource;
- a replacement for BALP, ATNA, SMART, OAuth or local audit repositories;
- a new canonicalisation algorithm;
- a new digital-signature algorithm;
- a new Merkle-tree construction;
- a SCITT implementation;
- a COSE Receipt implementation;
- a blockchain consensus mechanism;
- identity proofing;
- confidentiality for the public envelope;
- legal or regulatory adjudication;
- event-completeness instrumentation;
- operational hospital deployment.

## Design-science positioning

Route C is an **improvement-oriented design-science study**. It applies established design and security knowledge to a more specific problem configuration and contributes an inspectable boundary artefact plus bounded evaluation evidence.

The manuscript will not claim a mature explanatory design theory. It may report design rationale and reusable principles, but its main scholarly unit remains the evaluated boundary artefact.

## Frozen research questions

### RQ1 — Boundary

Which accountability facts should be portable, referenced, cryptographically committed or excluded when audit evidence crosses organisational boundaries in health information exchange?

### RQ2 — Operationalisation

How can the boundary be operationalised through a signed TrustEvidence envelope and a FHIR R4/BALP-facing projection without copying the underlying clinical payload?

### RQ3 — Assurance

Which structural, semantic, signature, commitment, receipt and retained-checkpoint properties are established by the executed validation and mutation corpus?

### RQ4 — Local incremental cost

What local incremental processing and message-size cost does the complete reference pipeline introduce relative to the declared source-processing and conventional audit-projection baselines?

## Contribution architecture

### Contribution A — Construct and boundary

A field-level definition of portable audit evidence and clinical-payload custody for cross-organisational healthcare events.

### Contribution B — Executable artefact

A closed signed-envelope profile, a bounded FHIR R4/BALP-facing projection and a local A2 receipt-verification implementation.

### Contribution C — Evaluation discipline

A case-, validator-, mutation-, measurement- and release-based evidence chain in which each public claim is constrained by the property actually executed.

Claim-governance documents support the evaluation but are not the primary scientific contribution.

## Falsification conditions

The central Route C contribution must be narrowed or rejected if any of the following occurs:

- the hero case cannot answer its declared accountability questions without raw clinical payload;
- the boundary omits a field required by the frozen case and no lower-exposure alternative exists;
- the envelope cannot be mapped to the declared FHIR corpus without semantic loss material to the research questions;
- positive FHIR examples fail undeferred mandatory validation constraints;
- a negative example or critical mutation is accepted;
- the issuer signature or payload commitment is not bound to the exact intended bytes;
- the local receipt verifier accepts inconsistent index, tree-size, root, path or checkpoint state;
- B0–B2 do not process identical source inputs;
- release artefacts and manuscript results cannot be reconciled.

## Canonical terminology

Use:

- `TrustEvidence`;
- `audit-evidence boundary`;
- `portable audit evidence`;
- `clinical payload custody`;
- `signed TrustEvidence envelope`;
- `payload commitment`;
- `issuer signature`;
- `local A2 Merkle receipt`;
- `FHIR R4/BALP-facing projection` until exact validator evidence permits narrower conformance wording;
- `local reference-pipeline increment` for the B0–B2 result.

Do not use:

- `Trust-Evidence`;
- `blockchain solution` as the artefact identity;
- `immutable`;
- `tamper-proof`;
- `encrypted by hashing`;
- `complete audit trail`;
- `FHIR compliant`;
- `hospital ready`;
- `expert validated`;
- `real-world validation` for synthetic cases.

## Reviewer-facing identity statement

The concise reviewer response is:

> The revised manuscript defines TrustEvidence as a healthcare-specific boundary model with an executable reference profile. FHIR and BALP provide healthcare audit representation; SCITT and COSE Receipts provide generic signed-statement and receipt mechanisms; prior healthcare systems provide access, consent, identity, integrity or ledger solutions. TrustEvidence contributes the field-level evidence/custody classification and its version-bound, minimised healthcare operationalisation. It does not claim a new primitive, standard or production architecture.
