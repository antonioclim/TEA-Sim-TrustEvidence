# Related research, software-paper boundary and reuse

## Associated peer-reviewed article

TEA-Sim TrustEvidence v2.2.0 supports:

> Clim, A. (2026). Designing portable audit evidence for health information exchange. *Journal of Computer Information Systems*. <https://doi.org/10.1080/08874417.2026.2720000>

The article and the software are related but non-identical scholarly objects.

## Research article versus software description

The associated article may report:

- the design problem and research questions;
- the field/custody boundary;
- comparison with prior standards and systems;
- bounded validation, mutation and local incremental-cost results;
- scientific interpretation and limitations.

A software metapaper or repository description may report:

- software purpose and statement of need;
- architecture and implementation;
- installation and dependencies;
- quality-control procedures;
- availability, licence and support;
- reuse routes and extension points.

It must not duplicate the article's research questions, numerical result tables, inferential narrative or contribution argument.

## Reuse route 1 — profile a new healthcare event

A researcher may define a new cross-organisational event, classify each accountability fact as portable, referenced, committed or excluded, construct the corresponding envelope and project the selected semantics into FHIR-facing artefacts.

Acceptance requires:

- no raw clinical value in the portable layer unless explicitly justified;
- versioned resource, Consent and policy references where applicable;
- positive and intended-negative fixtures;
- property-specific claims only.

## Reuse route 2 — benchmark verification behaviour

The mutation corpus, result contracts and retained evidence may be reused to compare canonicalisation, issuer-signature, commitment, receipt and checkpoint implementations.

The benchmark must distinguish:

- structural validity;
- semantic validity;
- issuer authentication;
- payload integrity commitment;
- backend receipt validity;
- inclusion;
- retained-checkpoint consistency;
- event completeness, which is not established.

## Reuse route 3 — replace the backend

A researcher may replace the project-specific local A2 model with another receipt or transparency service while retaining the healthcare evidence/custody boundary.

The replacement must be described as an external comparator only when a maintained external implementation is actually executed. A project-authored substitute is an internal implementation or ablation.

## Citation

Cite the exact software version used. Cite the associated article when relying on its research contribution or evaluation.
