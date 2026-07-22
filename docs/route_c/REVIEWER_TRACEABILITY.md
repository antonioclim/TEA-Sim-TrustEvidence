# Route C reviewer traceability

## Purpose

This register maps the JCIS revision requests to Route C evidence. It prevents a textual clarification from being used to close a request that requires an executed artefact or measurement.

## Editorial requirements

| ID | Requirement | Route C evidence |
|---|---|---|
| ED-01 | point-to-point response | C8 response document and closure matrix |
| ED-02 | revised Word manuscript with visible changes | anonymous tracked DOCX |
| ED-03 | title no longer than eight words | title decision and word-count audit |
| ED-04 | manuscript no longer than 10,000 words | generated word-count report |
| ED-05 | authorship unchanged | title-page and portal parity audit |
| ED-06 | JCIS reference and formatting requirements | manuscript QA report |
| ED-07 | unnumbered headings and subheadings | heading audit |

## Reviewer 1

| ID | Request | Route C action | Minimum evidence |
|---|---|---|---|
| R1-01 | specific health-data examples | C3 disclosure hero case | complete retained synthetic case |
| R1-02 | explain Merkle trees and their purpose | C4 mechanism and claim-boundary section | receipt/proof tests and diagram |
| R1-03 | explain process, steps and tools | C3-C5 IPO pipeline | executable commands and artefacts |
| R1-04 | extend the state of the art | C2 critical literature synthesis | verified direct-comparator matrix |
| R1-05 | readable tables and figures | C7 redesign | visual QA at final size |
| R1-06 | complete evidence entity with concrete data | C3 populated envelope | source, envelope, receipt and verification report |
| R1-07 | explain encryption | C4 cryptographic-controls table | exact distinction between commitment, signature and encryption |
| R1-08 | total overhead of adding TrustEvidence | C5 B0-B2 experiment | retained independent runs and p50/p95/p99 |

## Reviewer 2

| Concern family | Route C response |
|---|---|
| title and abstract | new eight-word title; abstract written after results freeze |
| recent literature | direct and recent healthcare audit, provenance, consent and integrity work |
| validity | explicit structural, semantic, standards, cryptographic and empirical evidence classes |
| terminology | first-use definitions, acronym reduction and terminology sheet |
| data and metadata | C3 case registry, source resources, field classification and provenance |
| Input-Processing-Output | one end-to-end case and algorithm diagram |
| figures and tables | reduced visual count, larger type, vector sources and visual audit |
| Results organisation | Results follow RQ and method order; interpretation moves to Discussion |
| numerical consistency | generated number registry and cross-document audit |

## Reviewer 3

The general concerns regarding contribution, methodology, literature, structure and abstract are addressed in C2 and C7. The references to generative artificial intelligence, programming occupations and labour-market transformation appear to concern a different manuscript. Route C will respond respectfully to that mismatch and will not add unrelated literature.

## Reviewer 4

| ID | Request | Route C response | Claim ceiling |
|---|---|---|---|
| R4-01 | define the identity and novelty of TrustEvidence | C2 scientific identity and comparator matrix | healthcare-specific boundary and reference profile |
| R4-02 | distinguish from FHIR AuditEvent, Provenance and Consent | C2/C3 mapping and hero case | FHIR provides representation; TrustEvidence defines the selected boundary and binding |
| R4-03 | distinguish from cryptographic integrations | C2/C4 literature and controls | no claim to a new signature or Merkle primitive |
| R4-04 | assess scalability | C5 local state-size and timing evidence only if executed | no large-network claim |
| R4-05 | discuss deployability | C7 bounded reference-deployment analysis | no hospital-readiness claim |
| R4-06 | explain interoperability beyond FHIR | C3 semantic and byte-preservation tests | audit-evidence interoperability, not improved clinical semantics |
| R4-07 | address cost and complexity | C5 measured local increments and component inventory | no organisational cost-reduction claim |
| R4-08 | accountability, transparency and trust | C4/C7 property-specific discussion | attributable evidence and local transparency properties; trust not measured |

## Evidence-level rule

- Presentation requests may be closed by manuscript evidence.
- Specification requests require an inspectable artefact.
- Validation and performance requests require executed outputs.
- Production, organisational and clinical-effectiveness questions remain limitations under Route C.

## Closure statuses

- `CLOSED-EVIDENCE` — executed evidence closes the request.
- `CLOSED-ARTEFACT` — an inspectable validated artefact closes the request.
- `CLOSED-MANUSCRIPT` — a presentation or definition problem is repaired.
- `CLOSED-CLAIM-BOUNDARY` — unsupported wording was removed or narrowed.
- `PARTIAL` — only the declared bounded portion was addressed.
- `NOT-APPLICABLE` — the request demonstrably concerns another manuscript.
- `OPEN` — submission is blocked if the request is major and no justified bounded response exists.
