# Route C manuscript blueprint

## Editorial constraints

- Journal: *Journal of Computer Information Systems*.
- Manuscript ID: 264354984.
- Revised title: **Designing Portable Audit Evidence for Health Information Exchange**.
- Title length: eight words.
- Internal total-text target: no more than 9,300 words.
- Hard editorial limit: 10,000 words.
- Headings and subheadings: unnumbered.
- Authorship: unchanged from the original submission.
- Abstract: written only after the Route C results and number registry are frozen.
- Reviewer-visible manuscript: anonymous, with changes visibly highlighted.

## Scientific identity

The paper is an improvement-oriented design-science study of a healthcare-specific audit-evidence boundary and executable reference profile. It is not presented as a new FHIR standard, generic transparency architecture, blockchain platform, production deployment or mature explanatory design theory.

The narrative question is:

> How should portable, authenticated audit evidence be bounded and operationalised for cross-organisational health information exchange without copying the underlying clinical payload?

## Contribution architecture

### Construct and boundary

A field-level portable/referenced/committed/excluded classification tied to declared accountability questions.

### Executable artefact

A closed signed TrustEvidence envelope, a minimal FHIR R4/BALP-facing projection and a bounded project-specific local A2 receipt-verification path.

### Evaluation evidence

Official validator outputs, a complete synthetic healthcare case, negative and mutation tests, a local B0–B2 incremental-cost experiment and a version-coherent reproducibility release.

Claim-governance and claim-demotion artefacts remain supporting quality controls. They are not described as the most important practical result.

## Frozen research questions

**RQ1.** Which accountability facts should be portable, referenced, cryptographically committed or excluded when audit evidence crosses organisational boundaries in health information exchange?

**RQ2.** How can the boundary be operationalised through a signed TrustEvidence envelope and a FHIR R4/BALP-facing projection without copying the underlying clinical payload?

**RQ3.** Which structural, semantic, signature, commitment, receipt and retained-checkpoint properties are established by the executed validation and mutation corpus?

**RQ4.** What local incremental processing and message-size cost does the complete reference pipeline introduce relative to the declared source-processing and conventional audit-projection baselines?

## Reader-centred narrative arc

```text
A versioned diagnostic report is disclosed across organisations.
        ↓
The exchange is clinically interoperable, but a later dispute requires
actor, organisation, purpose, Consent, policy, resource-version and
provenance evidence.
        ↓
FHIR and BALP provide essential representation patterns, while signatures
and transparency mechanisms provide distinct assurance properties.
        ↓
The unresolved design decision is which facts may cross the boundary and
which clinical content must remain under source custody.
        ↓
TrustEvidence classifies, signs, projects and verifies a bounded evidence set.
        ↓
The hero case, official validators, mutations and B0–B2 experiment test the
reported properties and costs.
```

## Main-manuscript structure and word budget

| Section | Target words | Function | Evidence gate |
|---|---:|---|---|
| Abstract | 190–210 | Problem, artefact, method, principal executed findings and claim ceiling | C6 results freeze |
| Introduction | 800–900 | Hero case, problem construct, gap, objective, RQs and three contributions | C2 identity; C3 case |
| Related Work and Contribution | 1,000–1,150 | Critical comparison with FHIR/BALP, consent systems, healthcare ledger approaches and SCITT/COSE | C2 literature |
| Research Design | 800–900 | Improvement-oriented DSR, inputs, build/evaluate cycles, validity architecture and case separation | C2–C5 protocols |
| TrustEvidence Boundary | 750–850 | Four classes, accountability fields, design rationale and hero-case field decisions | C3 |
| Reference Implementation | 700–800 | Envelope, canonicalisation, signature, commitment, FHIR projection and local A2 path | C3–C4 |
| Evaluation | 750–850 | Standards, case, mutation, privacy, B0–B2 and release methods | C3–C6 |
| Results | 1,100–1,300 | Objective findings in RQ order with no mechanism newly introduced | C3–C6 |
| Discussion | 850–1,000 | Design contribution, relation to standards, assurance/cost trade-offs and practical implications | C2–C6 |
| Limitations | 350–450 | Construct, technical, empirical and practical limitations | C6 |
| Conclusion | 200–275 | Boundary contribution, executed result and claim ceiling | C6 |
| Declarations | 120–180 | Ethics, funding, conflicts, contributions and availability | Author-confirmed facts |
| **Target total** | **8,600–9,300** | Includes table notes and captions conservatively | Hard maximum 10,000 |

## Section blueprint

### Abstract

Write last. Use five moves:

1. cross-organisational audit-evidence problem;
2. bounded TrustEvidence contribution;
3. design and evaluation methods;
4. quantitative and validation findings imported only from frozen registries;
5. implication and non-claims.

Do not include citations, repository paths, undefined acronyms, planned work or adjectives in place of measurements.

### Introduction

#### Opening hero case

Begin with Hospital A disclosing DiagnosticReport version 2 and its associated laboratory context to Hospital B for treatment under Consent version 3, policy version 6 and authorisation decision D-204. A later dispute asks what was sent, by whom, for which purpose and under which versioned decision context.

No standards or Merkle terminology appears before the practical dispute is clear.

#### Problem construct

Distinguish clinical semantic interoperability from audit-evidence interoperability. Define the latter in one sentence.

#### Existing capabilities and unresolved design decision

State fairly that FHIR R4 AuditEvent, Provenance and Consent and IHE BALP already provide rich healthcare audit representation. State separately that digital signatures and transparency mechanisms provide authentication, inclusion or consistency. The gap is not the absence of these primitives; it is the field-level evidence/custody profile and its tested cross-layer binding for the declared healthcare dispute.

#### Objective, RQs and contributions

Present four RQs and three contributions. End with one concise scope sentence: technical efficacy and local reference cost are evaluated; clinical truth, event completeness, legal compliance, organisational effectiveness and hospital-production performance are not.

### Related Work and Contribution

Organise by analytical dimension rather than a catalogue of papers.

#### Healthcare audit representation

- FHIR AuditEvent;
- Provenance;
- Consent;
- IHE BALP;
- consent lifecycle implementations such as MAGIC, gICS and Consent Management 2.0.

#### Cryptographic and transparency substrates

- canonicalisation and signatures;
- Certificate Transparency inclusion and consistency;
- SCITT signed-statement architecture;
- COSE Receipts.

#### Healthcare sharing and ledger systems

- MedRec;
- FHIRChain;
- recent blockchain-enabled EHR access auditing;
- current systematic review evidence on privacy and maturity.

#### Narrow contribution statement

Conclude with a direct matrix and the bounded novelty statement from the Scientific Identity Card. Do not use “first”, “unique”, “novel architecture” or “no existing standard supports”.

### Research Design

#### Research paradigm

Describe Route C as improvement-oriented design science. The artefact is built from established representation and cryptographic substrates for a more specific evidence-boundary problem.

#### Inputs, processing and outputs

Use the following Input–Processing–Output model:

```text
INPUT
versioned FHIR source context; actor and organisations; Consent; policy;
authorisation decision; resource bytes; provenance; verification policy

PROCESSING
validate → classify → minimise → commit → canonicalise → sign → project →
append locally → verify → report

OUTPUT
signed TrustEvidence envelope; portable FHIR evidence bundle; project-specific
local receipt; property-specific verification report
```

#### Build/evaluate cycles

Summarise C1–C6 without exposing internal project-management detail. Explain that the hero case is frozen before the final mutations and cost experiment.

#### Validity architecture

Separate:

- construct validity of the accountability questions and boundary classes;
- standards validity under the executed toolchain;
- implementation verification;
- property-specific security evidence;
- empirical conclusion validity for B0–B2;
- external-validity limits of synthetic cases and one reference environment.

### TrustEvidence Boundary

#### Four classes

Define portable, referenced, committed and excluded with one concrete hero-case example each.

#### Field rationale

Present only the mandatory hero-case fields in the main paper:

- event ID/type/time;
- actor token and role;
- source and recipient organisations;
- purpose and outcome;
- Consent reference/version/state;
- policy reference/version;
- decision ID/outcome;
- DiagnosticReport reference/version;
- provenance relation;
- payload commitment;
- issuer and profile identifiers.

Move the complete registry to the supplement.

#### Evidence boundary table

Use a compact table showing source fact, treatment, portable representation and rationale. Explicitly show patient name and raw Observation values as excluded.

### Reference Implementation

#### Envelope and canonical bytes

Describe the closed schema, strict JSON parsing and RFC 8785 application profile. Avoid implying a new canonicalisation method.

#### Signature and commitment

State exactly what issuer-signature bytes cover. Explain that SHA-256 commitment is not encryption. Describe nonce custody and the conditions under which a verifier can test a candidate payload.

#### FHIR projection

Explain AuditEvent, Provenance, Consent, Binary, DocumentReference and Bundle roles. State whether the final examples inherit applicable BALP profiles or are only mapped to them, according to C3 evidence.

#### Local A2 path

Explain entry commitment, root, inclusion path, signed local receipt and retained checkpoint. Use `project-specific local A2 Merkle receipt`. Explicitly distinguish it from RFC 9942 COSE Receipts and SCITT.

### Evaluation

#### Standards and round-trip evaluation

Report the exact FHIR packages, SUSHI, IG Publisher, HL7 Validator, positive/negative corpus and byte-preservation tests.

#### End-to-end case and privacy evaluation

Report hero-case source, field classification, accountability questions, field deletion, payload-exclusion scan and A1/A2 terminology limits.

#### Security evaluation

Report mutation families and expected property-specific errors. Do not use a single generic “secure” outcome.

#### Local incremental-cost evaluation

Define B0, B1 and B2, the two frozen workloads, independent paired runs, warm-up, p50/p95/p99, byte measures, failure retention and raw-data provenance.

#### Reproducibility

Report CI, release-check, fresh extraction, version identity, manifests and the distinction between deterministic and measurement-variable outputs.

### Results

Order strictly by RQ.

#### RQ1 result

Field classification, question coverage, deletions and residual unknowns.

#### RQ2 result

Hero case, FHIR validation, semantic round trip and byte preservation.

#### RQ3 result

Positive and negative counts, mutation outcomes, false accepts, state behaviour and explicit properties not established.

#### RQ4 result

B0–B2 p50/p95/p99, paired increments, byte sizes, failures and environment. Do not interpret the measurements as production EHR latency.

Each paragraph reports one major finding. Interpretive explanation belongs in Discussion.

### Discussion

#### What the boundary contributes

Explain the value of making custody and evidence selection explicit before applying representation or cryptography.

#### Relation to FHIR/BALP and SCITT/COSE

Use the formulation:

> FHIR and BALP provide healthcare audit representation; generic signed-statement and receipt standards provide separate cryptographic substrates; TrustEvidence contributes the bounded healthcare field-selection and cross-layer profile evaluated here.

#### Local A2 assurance and cost

Discuss additional inclusion/consistency evidence alongside its measured local cost and retained-state assumption. Do not rank it morally above conventional audit.

#### Practical implications

Identify integration prerequisites and metadata risks without claiming adoption, cost reduction or organisational trust effects.

#### Negative knowledge

Report rejected fields, unsupported properties, validator limitations and any contradicted proposition.

### Limitations

Cover:

- one declared accountability model rather than a universal field set;
- synthetic cases and bounded external data use;
- a reference implementation and local in-memory A2 backend;
- no SCITT/COSE Receipt conformance;
- one primary local measurement environment;
- no operational hospital deployment;
- no expert study;
- no legal, clinical-truth or complete-event-capture result.

### Conclusion

Return to the hero-case problem. State the boundary contribution and the strongest executed result. End with the narrow next step: external implementation and operational evaluation, not a promotional adoption claim.

## Main figures

Maximum three.

### Figure 1 — Cross-Organisational Evidence Flow

Clinical payload path, evidence path, source custody, Hospital A, Hospital B, emitter, local A2 and verifier. Short noun-phrase labels only.

### Figure 2 — TrustEvidence Processing Pipeline

Input–Processing–Output sequence with boundary classes and exact outputs. This replaces the ambiguous legacy flow figure.

### Figure 3 — Local Incremental Cost

B0–B2 run-level p50/p95/p99 with uncertainty or paired increments, generated only after C5 freeze.

## Main tables

Maximum five.

1. Direct comparator and novelty boundary.
2. Hero-case evidence/custody decisions.
3. Standards and round-trip results.
4. Security mutation results and claim ceiling.
5. B0–B2 processing and message-size results.

Large field, test and reference registries move to the supplement or repository.

## Legacy material disposition

| Legacy material | Route C action |
|---|---|
| Original title | Replace with the eight-word title |
| Original four RQs tied to draft FHIR/local A2 limitations | Replace with frozen Route C RQ1–RQ4 |
| Claim demotion described as the most important practical result | Demote to supporting research-governance control |
| Intended A1/A3 comparison not executed | Remove from the principal method and results; mention only as excluded scope if necessary |
| Draft FHIR mapping presented near conformance language | Replace with C3 executed validation or narrow to FHIR/BALP-facing |
| `Bennett et al., 2023, 2024, 2025` bundled citation | Separate article, full dataset and demo records by evidential function |
| Five dense figures | Replace with maximum three readable figures |
| Numbered headings | Remove |
| Repeated non-claim lists | Consolidate in scope, verification report and limitations |
| v2.0.1 timings and retained outputs | Do not combine with v2.2.0 Route C findings |
| “real data” wording for synthetic examples | Replace with `clinically plausible synthetic data` |

## Evidence-to-writing gates

- No past-tense C3 sentence before official validator and hero-case evidence exists.
- No security result before C4 mutation freeze.
- No overhead number before C5 raw-data and analysis freeze.
- No v2.2.0 release statement before C6 fresh-extraction pass.
- No abstract result before the manuscript number registry is frozen.
- No reviewer response may say `implemented`, `validated` or `measured` unless the Claim–Evidence Ledger status permits it.

## Numerical control

All reported numbers will be generated into a single machine-readable registry. The abstract, Results, figures, tables and response letter must use that source. Manual transcription from terminal output is prohibited.

## Reference control

Every citation must appear in `VERIFIED_REFERENCE_REGISTRY.csv` or a later verified extension. DOI resolution, title, author, year, venue and the supported claim must be checked before manuscript freeze. Dataset article, dataset release and demo release are cited separately.

## Definition of manuscript completion

The manuscript is complete only when:

- all four RQs have a direct evidence-bounded answer;
- title, structure and word limit satisfy the editorial letter;
- every numerical statement resolves to the frozen registry;
- every literature claim resolves to a verified source;
- all figures and tables are readable at final size;
- all legacy claims have been removed or reconciled;
- declarations contain no placeholders;
- anonymous and identified versions are scientifically identical;
- the response letter can point to exact manuscript locations and executed evidence.
