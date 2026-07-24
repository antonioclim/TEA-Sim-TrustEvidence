# Route C charter for the JCIS revision

## Status

Active from 22 July 2026 for manuscript 264354984, *Journal of Computer Information Systems*.

Route C is an emergency, evidence-first revision. It is intended to produce a materially stronger and fully reproducible revision within a constrained calendar without presenting the unexecuted Route A research programme as completed work.

## Scientific objective

The revision will present TrustEvidence as a healthcare-specific audit-evidence boundary and executable reference profile. The central problem is to decide which facts about access, disclosure, consent, policy, provenance and integrity may cross organisational boundaries as portable audit evidence, which facts remain references or commitments, and which facts remain under clinical payload custody.

The revision is not intended to establish a production healthcare auditing platform, a new FHIR standard, a generic transparency protocol, clinical truth, complete event capture, legal compliance, organisational effectiveness or expert consensus.

## Source-of-truth policy

The following order governs all public claims:

1. executed source code and retained outputs;
2. validated schemas and test vectors;
3. official standards-tool reports, where executed;
4. analysis outputs generated from retained raw data;
5. manuscript wording;
6. repository and release metadata.

If two layers disagree, the higher layer in this list controls and the lower layer must be corrected. Documentation must never upgrade an unexecuted pathway into a result.

## Version and branch policy

- Baseline public release: `v2.1.0`.
- Route C development branch: `revision/jcis-route-c`.
- Provisional revision release: `v2.2.0`.
- Release candidate: `v2.2.0-rc.1`.
- The default branch remains unchanged until all Route C gates required for integration have passed.
- A major version is required if the signed envelope semantics, canonical bytes or verification contract become incompatible with `v2.1.0`.

## Mandatory Route C outcomes

Route C must deliver:

- a single, stable scientific identity for the manuscript and software;
- a complete synthetic cross-organisational disclosure case;
- a concrete, fully populated TrustEvidence envelope without raw clinical payload;
- an officially executed, narrowly scoped FHIR R4 validation route;
- explicit separation of commitment, signature, Merkle assurance and encryption;
- controlled semantic, signature, receipt and checkpoint mutations;
- a local incremental B0-B2 overhead experiment with independent runs and retained raw data;
- restored continuous integration on Python 3.13;
- an exact-version GitHub release and Zenodo software record;
- a reconstructed JCIS manuscript and evidence-backed point-to-point response;
- an anonymous tracked manuscript and a scientifically identical identified manuscript.

## Priorities

### Must

- continuous integration and `make release-check`;
- hero disclosure case;
- official FHIR validator execution for the declared corpus;
- negative FHIR and TrustEvidence cases;
- payload-exclusion scan;
- B0-B2 local incremental experiment;
- version, citation and Zenodo metadata parity;
- reviewer-response and anonymity audits.

### Should

- a wearable-batch case;
- p50, p95 and p99 reporting;
- field-deletion evidence integrated into the manuscript;
- a simple conventional-audit baseline;
- readable regenerated figures and tables.

### Could

- a public-derived FHIR demonstration case;
- a PostgreSQL comparator;
- controlled network-latency sensitivity;
- an informative SCITT comparison note.

### Excluded from Route C claims

- SCITT or RFC 9942 conformance;
- a production transparency service;
- an independent Java verifier;
- operational hospital deployment;
- human-participant or Delphi studies;
- complete formal verification;
- multi-host or multi-issuer scaling;
- Rekor, Trillian or Fabric execution;
- full external clinical-dataset extraction.

## Route C phases and gates

| Phase | Purpose | Gate |
|---|---|---|
| C1 | Repository and CI stabilisation | CI exists; Python 3.13 coherent; release checks pass |
| C2 | Scientific identity and literature | one contribution identity; verified references; bounded claims |
| C3 | Hero case and FHIR validation | positive corpus valid; negative corpus rejected; no payload leakage |
| C4 | Security and mutation suite | zero false accepts in declared attacks; exact claim boundaries |
| C5 | Local incremental overhead | same inputs; independent runs; retained raw data; p50/p95/p99 |
| C6 | Release candidate | metadata, manifests and fresh extraction agree |
| C7 | Manuscript reconstruction | editorial constraints, numerical parity and readable visuals |
| C8 | Reviewer response and submission package | all comments accounted for; zero major blockers; anonymity passes |
| C9 | Public release hand-off | GitHub and Zenodo exact-version records agree |

## Evidence status vocabulary

- `EXECUTED-PASS`: executed under the declared protocol and passed.
- `EXECUTED-FAIL`: executed and failed; the failure remains part of the evidence.
- `NOT-EXECUTED`: no result may be claimed.
- `INDETERMINATE`: execution did not establish the requested property.
- `INFORMATIVE-ONLY`: design or mapping material without a conformance claim.
- `LEGACY`: retained only for provenance and not used for revised results.

## Stop-the-line conditions

Work stops and returns to the affected phase if any of the following occurs:

1. `make release-check` fails;
2. CI and the release environment use different Python versions;
3. a positive FHIR example fails an undeferred mandatory constraint;
4. a negative example is accepted for the wrong reason;
5. a critical mutation is accepted;
6. the envelope transported through FHIR differs from the envelope verified by the implementation;
7. the B0-B2 conditions do not use identical source inputs;
8. retained outputs cannot be regenerated or reconciled;
9. raw clinical payload or direct identifiers enter portable evidence;
10. repository, manuscript and release metadata identify different software versions;
11. a manuscript or reviewer response describes planned work as completed;
12. the anonymous package exposes the author.

## Definition of completion

A Route C phase is complete only when its files, commands, outputs, warnings, failures, claim ceiling and gate verdict have been recorded. Passing this charter does not itself close a reviewer request: only executed artefacts and evidence can do so.
