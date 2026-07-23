# Route C reviewer traceability

## Purpose

This document provides the high-level reviewer-to-evidence map. The authoritative atomised register is:

```text
docs/route_c/REVIEWER_COMMENT_REGISTRY.csv
```

The detailed register controls identifiers, severity, Route C phase, minimum evidence, current status, manuscript destination and closure rule. This summary must not be used to close a request independently.

## Evidence-level rule

- Presentation requests may be closed by a verified manuscript change.
- Specification requests require an inspectable artefact.
- Validation, security and performance requests require executed outputs.
- Production, organisational, legal and clinical-effectiveness questions remain explicit limitations under Route C.
- A planned task never closes an evidence request.

## Editorial requirements

| ID | Requirement | Route C evidence |
|---|---|---|
| ED-01 | Point-to-point response | C8 response document and closure matrix |
| ED-02 | Revised Word manuscript with visible changes | Anonymous tracked or controlled highlighted DOCX plus parity report |
| ED-03 | Title no longer than eight words | Frozen eight-word title and title audit |
| ED-04 | Manuscript no longer than 10,000 words | 9,300-word internal budget and final count |
| ED-05 | Avoid unnecessary self-citation | Citation and self-citation audit |
| ED-06 | Authorship unchanged | Title-page and portal parity audit |
| ED-07 | JCIS reference and formatting requirements | Manuscript QA report |
| ED-08 | Unnumbered headings and subheadings | Heading audit |

## Reviewer 1 evidence path

| Request family | Route C response | Minimum closure evidence |
|---|---|---|
| Concrete medical exchange and complete evidence object | C3 synthetic DiagnosticReport disclosure case | Source resources, field classification, signed envelope, FHIR projection, local receipt, verification report and checksums |
| Merkle explanation and purpose | C4 property-specific mechanism and mutations | Inclusion, consistency, stale-state, relabelling and explicit authorised-backend limitation results |
| Process, steps and tools | C3–C5 Input–Processing–Output chain | Executable commands, exact versions, retained outputs and the frozen B0–B2 timing boundaries |
| State of the art | C2 direct literature synthesis | Verified source registry and comparator matrix |
| Readable figures and tables | C7 redesign | Final-size vector/raster QA and reviewer-PDF inspection |
| Encryption | C4 controls table | Exact distinction among commitment, signature, receipt, TLS and optional at-rest controls; no implemented encryption claim |
| Total overhead | C5 B0–B2 local incremental experiment | Five excluded pilot blocks, twenty retained paired blocks, p50/p95/p99, canonical application-byte and storage-proxy increments, raw timings and explicit non-production wording |

## Reviewer 2 evidence path

| Concern family | Route C response |
|---|---|
| Title and abstract | Frozen eight-word title; abstract written after results freeze |
| Recent and direct literature | C2 DOI/canonical registry and critical comparator synthesis |
| Validity and verification | Separate standards, semantic, implementation, security, C5 paired empirical and reproducibility evidence |
| Terminology and acronyms | Canonical terminology and first-use expansion; `TrustEvidence` only |
| Data and metadata | C3 source registry, concrete synthetic resources, transformations and case provenance |
| Input–Processing–Output | Frozen processing pipeline and end-to-end hero case |
| Figures and tables | Reduced visual count, larger type, vector sources and visual audit |
| Results structure | Results follow RQ and method order; interpretation moves to Discussion |
| Numerical consistency | C5 machine-readable aggregates become the number source; C7–C8 perform the final cross-document audit |

## Reviewer 3 evidence path

The general concerns regarding contribution, methodology, literature, structure and abstract remain mandatory and are owned by C2 and C7.

The request concerning generative artificial intelligence, programming occupations and labour-market transformation is recorded as `R3-06`, severity `MISMATCH`, status `NOT-APPLICABLE`. C8 will respond respectfully to the apparent mismatch without introducing unrelated literature.

## Reviewer 4 evidence path

| Request family | Route C response | Claim ceiling |
|---|---|---|
| TrustEvidence identity and novelty | C2 Scientific Identity Card and hostile novelty test | Healthcare-specific boundary model and executable reference profile |
| Difference from FHIR AuditEvent, Provenance and Consent | C2 delta matrix plus C3 mapping and official validation | FHIR provides representation; TrustEvidence selects and binds the declared portable evidence set |
| Difference from cryptographic integrations | C2 literature and C4 mechanism audit | No new canonicalisation, signature, Merkle, SCITT or COSE Receipt primitive |
| Scalability | C5 executed one synthetic workload on one four-vCPU hosted runner | No large-network, concurrency, network or distributed-service claim |
| Deployability | C6/C7 component and release analysis | No hospital-readiness claim |
| Interoperability beyond FHIR | C3 semantic round trip and exact-byte preservation | Audit-evidence interoperability, not improved clinical semantics |
| Cost and complexity | C5 local processing and canonical application-byte increments; C6 adds the component inventory | No organisational cost-reduction, network-cost or database-cost claim |
| Accountability, transparency and trust | C4/C7 property-specific discussion | Attributable evidence and bounded local inclusion/consistency; backend honesty, completeness and organisational trust not measured |

## Closure statuses

- `CLOSED-EVIDENCE` — executed evidence closes the request.
- `CLOSED-ARTEFACT` — an inspectable validated artefact closes the request.
- `CLOSED-MANUSCRIPT` — a presentation or definition problem is repaired.
- `CLOSED-CLAIM-BOUNDARY` — unsupported wording was removed or narrowed.
- `PARTIAL` — only the declared bounded portion was addressed and the residual limit is explicit.
- `NOT-APPLICABLE` — the request demonstrably concerns another manuscript.
- `OPEN` — submission is blocked if the request is major and no justified bounded response exists.

## Current phase status

C2 closes the design-level concerns concerning title, artefact identity, research questions, novelty boundary, literature plan, reviewer atomisation and manuscript architecture.

C3 supplies the complete synthetic healthcare case, the field-level boundary instantiation and the bounded official FHIR toolchain evidence.

C4 supplies the executed semantic, issuer, commitment, receipt, proof and retained-state mutation corpus. Its most important negative result is that a valid backend receipt does not independently prove truthful tree size, actual log population or completeness.

C5 supplies the preregistered W1 B0–B2 paired local experiment: five pilot blocks retained and excluded, twenty confirmatory paired blocks, sixty process runs, 7,680 operation timings, p50/p95/p99 paired increments, canonical application-byte increments and a labelled local storage proxy. The evidence closes the empirical workstream only at the local reference-pipeline level; W2 was prospectively omitted and no production-EHR, hospital-latency, network, database, scalability or organisational-cost result is claimed.

Reviewer-facing closure remains partial until C7 integrates the C2–C5 evidence into the article and C8 resolves every comment to exact manuscript locations.
