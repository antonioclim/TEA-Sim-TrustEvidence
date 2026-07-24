# Route C Phase C2 completion report

## Phase objective

C2 fixes the scientific identity, research questions, direct comparator set, novelty boundary, claim–evidence architecture, reviewer requirement registry and manuscript reconstruction plan before the Route C hero case or new empirical claims are built.

## Inputs reviewed

### Submission evidence

- identified and anonymous manuscript versions;
- portal submission PDF;
- editorial decision and four reviewer reports;
- the existing v2.1.0 repository documentation, schema, standards note and retained evidence.

### Authoritative standards

- FHIR R4 4.0.1 `AuditEvent`;
- FHIR R4 4.0.1 `Provenance`;
- FHIR R4 4.0.1 `Consent`;
- IHE Basic Audit Log Patterns 1.1.4;
- RFC 9162;
- RFC 9942;
- RFC 9943.

### Direct literature streams

- FHIR-based consent management and consent exchange;
- healthcare blockchain permissions and sharing;
- FHIRChain;
- blockchain-enabled EHR access auditing;
- current systematic review evidence on privacy-preserving blockchain healthcare sharing;
- design-science and empirical-reporting methodology.

## Files created

```text
docs/route_c/SCIENTIFIC_IDENTITY_CARD.md
docs/route_c/RQ_REGISTER_ROUTE_C.csv
docs/route_c/DIRECT_COMPARATOR_MATRIX.csv
docs/route_c/FHIR_SCITT_TRUSTEVIDENCE_DELTA.csv
docs/route_c/VERIFIED_REFERENCE_REGISTRY.csv
docs/route_c/CLAIM_EVIDENCE_LEDGER.csv
docs/route_c/MANUSCRIPT_BLUEPRINT_ROUTE_C.md
docs/route_c/REVIEWER_COMMENT_REGISTRY.csv
docs/route_c/C2_LITERATURE_SYNTHESIS.md
docs/route_c/C2_COMPLETION_REPORT.md
```

## Frozen scientific identity

### Title

**Designing Portable Audit Evidence for Health Information Exchange**

The title contains exactly eight words.

### Artefact identity

TrustEvidence is a **healthcare-specific audit-evidence boundary and executable reference profile**.

The primary artefact is the field-level boundary model. The secondary artefact is the executable profile consisting of the closed envelope schema, application-profile canonicalisation, issuer signature, nonce-based commitment, FHIR R4/BALP-facing projection and project-specific local A2 verifier.

Route C does not describe the artefact as:

- a new FHIR standard;
- a generic transparency architecture;
- a SCITT or COSE Receipts implementation;
- a blockchain consensus system;
- a production hospital system;
- a mature explanatory design theory.

## Frozen problem construct

**Audit-evidence interoperability** is the capacity of organisations to exchange and independently inspect a declared set of accountability facts without copying the underlying clinical payload and without treating representation, signature or backend inclusion as proof of clinical truth.

## Frozen research questions

1. Which accountability facts should be portable, referenced, cryptographically committed or excluded when audit evidence crosses organisational boundaries in health information exchange?
2. How can the boundary be operationalised through a signed TrustEvidence envelope and a FHIR R4/BALP-facing projection without copying the underlying clinical payload?
3. Which structural, semantic, signature, commitment, receipt and retained-checkpoint properties are established by the executed validation and mutation corpus?
4. What local incremental processing and message-size cost does the complete reference pipeline introduce relative to the declared source-processing and conventional audit-projection baselines?

These RQs are design-frozen. They have not yet been answered by new Route C evidence.

## Frozen contribution architecture

### Contribution A — Construct and boundary

A field-level portable/referenced/committed/excluded classification tied to declared healthcare accountability questions.

### Contribution B — Executable artefact

A closed signed TrustEvidence envelope, a bounded FHIR R4/BALP-facing projection and a project-specific local receipt-verification path.

### Contribution C — Evaluation discipline

An evidence chain linking the hero case, official validators, negative and mutation tests, local B0–B2 measurements and release provenance to claim-specific wording.

Claim-demotion and claim-governance records are supporting research controls rather than the principal scientific contribution.

## Hostile novelty verdict

### What is not novel

The following capabilities are established and must be attributed to prior standards or literature:

- healthcare security-event representation;
- actor, purpose, outcome and policy fields in FHIR AuditEvent;
- versioned provenance and transformation context;
- FHIR Consent and its source-derived or partial representations;
- consent withdrawal, refusal, objection and historical consent status;
- blockchain-mediated medical-data permissions;
- FHIR-plus-blockchain sharing architectures;
- EHR access logging by actor, time and purpose;
- deterministic JSON canonicalisation;
- digital signatures;
- Merkle inclusion and consistency algorithms;
- generic signed-statement transparency;
- COSE receipt structures.

### Residual defensible contribution

The defensible Route C contribution is the healthcare-specific selection, custody treatment and cross-layer binding of versioned event, actor, organisation, purpose, Consent, policy, decision, resource and provenance facts, evaluated through a concrete case and bounded tools.

No priority claim is permitted.

## Literature corrections fixed in design

- FHIR/BALP are treated as essential substrates rather than weak strawman baselines.
- SCITT and COSE Receipts are direct novelty-boundary standards, not project features.
- MedRec, FHIRChain and current EHR audit work are direct comparators.
- The peer-reviewed MIMIC-IV-on-FHIR article, full dataset record and demo dataset record are separated by evidential function.
- Foundational design-science references remain where they define the method; recent references are added for direct domain developments rather than by date quota.
- Conditional dataset records cannot enter the final APA list until exact record metadata are exported and checked.

## Claim–evidence status after C2

### Baseline executed but release-candidate rerun required

- RFC 8785 application-profile canonicalisation;
- current issuer-signature checks;
- current nonce-based commitment checks;
- current project-specific local A2 inclusion and retained-checkpoint checks.

### Partial baseline only

- field-level boundary;
- payload minimisation;
- release reproducibility;
- reviewer traceability.

### Not executed for Route C

- complete cross-organisational hero case;
- official FHIR/BALP validation;
- new Route C mutation corpus;
- B0–B2 local incremental-cost experiment;
- v2.2.0 release candidate.

No C2 document converts a planned item into a result.

## Reviewer-registry result

The editorial letter and four reviewer reports have been atomised into:

- eight editorial requirements;
- nine Reviewer 1 requirements;
- twenty-seven Reviewer 2 requirements;
- six Reviewer 3 requirements;
- ten Reviewer 4 requirements.

Reviewer 3's generative-AI/programming/labour-market request is marked `MISMATCH` and `NOT-APPLICABLE`; the reviewer's general requests on contribution, method, literature, structure and abstract remain mandatory.

## Manuscript reconstruction decision

The revised paper will be rebuilt from the Route C blueprint rather than incrementally patched. The main manuscript will contain no more than:

- three principal figures;
- five principal tables;
- four RQs;
- 9,300 internally budgeted words.

Legacy claim-demotion emphasis, non-executed A1/A3 comparison language, bundled Bennett citations, dense figures, numbered headings and v2.0.1 result values are quarantined from the final narrative.

## C3 design blockers identified

### Blocker C3-B01 — monitoring-specific object vocabulary

The current `monitoring_event.schema.json` limits `data_category_code` to glucose, wearable and personal-monitoring summaries and limits `resource_class` to monitoring-centric values plus consent, policy, evidence operations and checkpoints.

A DiagnosticReport hero case cannot be represented honestly by relabelling it as a personal-monitoring summary. C3 must choose one of two controlled options:

1. add backward-compatible v2.2.0 values for diagnostic reports and related laboratory resources; or
2. narrow the hero case to a resource class already supported, which would weaken the response to Reviewer 1.

The recommended decision is a backward-compatible v2.2.0 vocabulary extension with new positive, negative, migration and version-identity tests.

### Blocker C3-B02 — monitoring-specific privacy-profile identifier

The current minimisation profile is fixed to `TE-PHM-Min-1`. The cross-organisational disclosure case requires an explicit HIE profile identifier rather than reusing a personal-health-monitoring label.

C3 must decide whether to:

- extend the schema with an additional `TE-HIE-Min-1` value while retaining v2.1 compatibility; or
- version the profile field more generally.

The former is preferred for Route C because it is smaller and testable.

### Blocker C3-B03 — authorisation decision identifier

The current model records decision source and outcome but may not carry an explicit decision identifier required by the frozen hero-case dispute. C3 must perform a field-level necessity audit before adding any field.

### Blocker C3-B04 — no official FHIR artefact set

The v2.1 repository contains a mapping note but no minimal canonical IG, official validator logs or negative FHIR corpus. These are mandatory C3 outputs.

### Blocker C3-B05 — local A2 terminology

The existing backend is not SCITT or RFC 9942. All C3 examples and C4 reports must use the project-specific local terminology fixed in C2.

## C2 stop-the-line conditions

C3 must stop and return to C2 if:

- the hero case requires a new contribution identity;
- a mandatory field has no accountability question;
- a proposed field duplicates a native FHIR element without a mapping rationale;
- the schema change becomes backward incompatible and the version remains 2.2.0;
- the FHIR projection is presented as the signed semantic source of truth;
- any SCITT or COSE Receipt conformance wording is introduced.

## Gate C2 criteria

| Criterion | Result |
|---|---|
| One scientific identity | PASS |
| Eight-word title | PASS |
| Four research questions | PASS |
| Contribution separated from established primitives | PASS |
| Direct standards comparator set | PASS |
| Direct healthcare comparator set | PASS |
| Verified DOI/canonical registry | PASS WITH TWO CONDITIONAL DATASET METADATA EXPORTS |
| Claim–evidence ledger | PASS |
| Reviewer atomisation | PASS |
| Manuscript blueprint and word budget | PASS |
| No new empirical claim | PASS |
| C3 schema debt explicitly identified | PASS |

## Gate verdict

```text
C2 = PASS
C2 open blocker count = 0
C3 controlled design blockers = 5
```

The five C3 blockers are inputs to the next phase, not unresolved C2 identity or literature defects.

## Claims permitted after C2

The project may state that:

- Route C defines TrustEvidence as a healthcare-specific boundary model with an executable reference profile;
- the contribution has been explicitly delimited against FHIR/BALP, healthcare consent systems, healthcare ledger approaches, SCITT and COSE Receipts;
- the manuscript title, research questions, contribution structure, claim ledger, reviewer registry and reconstruction blueprint are frozen;
- the existing v2.1 schema already contains several required version, actor, policy, commitment and provenance constructs but remains monitoring-specific.

## Claims prohibited after C2

C2 does not permit claims that:

- the hero case has been implemented;
- the schema already supports a DiagnosticReport without modification;
- any Route C FHIR example is conformant;
- the local receipt is SCITT or RFC 9942 compliant;
- the new mutation suite has passed;
- B0–B2 overhead has been measured;
- v2.2.0 exists;
- the revised manuscript is complete.
