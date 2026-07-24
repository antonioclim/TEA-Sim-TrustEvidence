# Phase C3 completion report

## Gate decision

```text
Phase: C3 — synthetic cross-organisational hero case and bounded official FHIR validation
Decision: PASS
Open C3 blockers: 0
Scope: exact retained Route C corpus and declared hosted toolchain only
Release status: working branch; v2.2.0 has not yet been released
Main branch modified: no
```

C3 establishes a complete synthetic medical disclosure case, a signed and minimised TrustEvidence envelope, a FHIR R4/BALP-facing projection, a project-specific local A2 receipt path and a retained official validation evidence package. It does not establish operational deployment, universal conformance, IHE certification, clinical validity, legal compliance or production performance.

## Authoritative repository state

| Item | Value |
|---|---|
| Repository | `antonioclim/TEA-Sim-TrustEvidence` |
| Working branch | `revision/jcis-route-c` |
| Pull request | draft PR #1 |
| Evidence materialisation commit | `5aac6c946eecadc697a9ec455ca45d1e7ab640b6` |
| All-green post-materialisation verification commit | `4ec83e43b2b7c6b75f0f2f9d7bb460d6c0304e7b` |
| All-green hosted workflow | `30002019712` |
| Workflow conclusion | `success` |
| Baseline public metadata during C3 | v2.1.0 |
| Target release | provisionally v2.2.0, pending C4–C6 |

The evidence materialisation commit retained the generated hero-case artefacts, compact implementation-guide package, validation logs, OperationOutcomes, tool records and integrity manifests. The subsequent hosted run executed both the complete offline release contract and the official FHIR toolchain successfully on the synchronised tree.

## Hero-case specification

### Case identity

```text
case_id: HIE-DISCLOSURE-001
data_status: synthetic
source organisation: Synthetic Hospital A
recipient organisation: Synthetic Hospital B
event: disclosure of DiagnosticReport version 2
purpose: treatment
Consent version: 3
Consent state: active
policy version: 6
authorisation decision: D-204
```

### Synthetic clinical source

The source clinical Bundle contains:

- one pseudonymous Patient;
- Synthetic Hospital A;
- one versioned DiagnosticReport;
- three laboratory Observations;
- sodium `140 mmol/L`;
- potassium `4 mmol/L`;
- creatinine `1 mg/dL`.

The integer-valued fixtures are deliberate. FHIR decimal values are valid JSON, but the existing `TE-JCS-1` application profile excludes Python floating-point values. Route C preserves that baseline rule and uses clinically plausible integer-valued synthetic fixtures for deterministic commitment bytes. This is a reference-fixture constraint, not a claim about the permitted value space of production FHIR resources.

### Processing path

```text
synthetic FHIR source Bundle
→ source-payload canonicalisation
→ nonce-based payload commitment
→ HIE disclosure input validation
→ four-class evidence/custody selection
→ TrustEvidence core construction
→ deterministic application-profile canonicalisation
→ Ed25519 issuer signature
→ project-specific local A2 append
→ signed local receipt
→ inclusion and retained-checkpoint verification
→ FHIR R4/BALP-facing projection
→ semantic, privacy and official-validator checks
```

## Four-class boundary instantiated by C3

C3 operationalises the frozen boundary classes as follows:

1. **Portable** — event identity, timestamps, pseudonymous actor and organisation context, role, purpose, outcome, Consent reference/version/state, policy reference/version/digest, decision reference, provenance context, issuer signature and local receipt evidence.
2. **Referenced** — the source DiagnosticReport is represented by resource type plus versioned identifier rather than copied into the portable Bundle.
3. **Committed** — the exact canonical source clinical Bundle is bound by the declared nonce-based SHA-256 commitment profile.
4. **Excluded** — direct patient identity, raw Observation resources, laboratory values, DiagnosticReport conclusion, credentials, private keys and the commitment nonce are absent from the positive portable Bundle.

The field-level rationale is retained in `HIE_BOUNDARY_MATRIX.csv`; the accountability-question and necessity audit is retained in `C3_NECESSITY_AUDIT.md`.

## Retained artefacts

### Healthcare case

```text
data_examples/hie_disclosure/
├── case_manifest.json
├── hie_disclosure_event.json
├── signed_envelope.json
├── signed_envelope_with_receipt.json
├── signed_envelope_with_receipt.canonical.json
├── retained_checkpoint.json
├── verification_report.json
├── source/
├── negative/
└── private_test_material/
```

The builder reports `41 retained files` and fails when a retained output differs from the deterministic reconstruction.

### FHIR artefacts

```text
standards/fhir_ig/
├── sushi-config.yaml
├── ig.ini
├── input/fsh/profiles.fsh
├── input/resources/
├── negative/
├── fsh-generated/
├── validation/
├── WARNING_ADJUDICATION.md
└── validation/org.trustevidence.hie-0.1.0.tgz
```

Rendered-site, temporary Jekyll, downloaded-template and terminology-cache directories are excluded from the distributed package. The retained evidence checker and integrity builder explicitly reject or omit:

```text
standards/fhir_ig/output
standards/fhir_ig/temp
standards/fhir_ig/input-cache
standards/fhir_ig/template
```

## Semantic and payload-custody results

The retained semantic report has status `PASS` and records:

- HIE event schema accepted;
- signed-envelope schema accepted;
- exact signed-envelope bytes preserved after Base64 decoding from FHIR `Binary`;
- Binary and DocumentReference content types equal to `application/json`;
- no `Observation` resource in the positive portable Bundle;
- no `DiagnosticReport` resource in the positive portable Bundle;
- no declared forbidden clinical-value path;
- no unresolved local source-resource reference;
- decision `D-204` present;
- policy version `6` present;
- Consent reference present;
- versioned DiagnosticReport identifier present in the relevant AuditEvent, Provenance and Consent derivative.

The canonical signed-envelope SHA-256 retained by the case is:

```text
a210b264ac5e0e10a629aae86181912aae69c990f0d89cbbe118e247b45049dd
```

The finding supports absence of the declared forbidden fields in the inspected artefacts. It does not establish anonymity, absence of all sensitive metadata or zero re-identification risk.

## Official FHIR toolchain

### Recorded environment

```text
Python:             3.13.14
Java:               OpenJDK 17.0.19
Node:               22.23.1
Ruby:               3.3.12
Jekyll:             4.4.1
SUSHI:              3.20.0
FHIR core:          4.0.1
BALP dependency:    1.1.4
FHIR Validator:     6.9.12
Terminology server: https://tx.fhir.org/r4
```

The publisher and validator JAR SHA-256 values are retained in `tool_sha256.txt`; complete environment strings are retained in `tool_versions.txt`.

### SUSHI

The C3 source generated:

- four StructureDefinition profiles;
- one project CodeSystem;
- one project ValueSet;
- zero SUSHI errors;
- zero SUSHI warnings.

### IG Publisher

The retained publisher summary reports:

```text
status:               PASS
QA errors:            0
log errors:           0
warnings:            33
information/hints:   16
broken links:         0
suppressed warnings:  0
suppressed hints:     0
```

The thirty-three warnings are retained, not hidden:

- four unused generic base-template fragments;
- two recommendations to allocate OIDs;
- twenty-seven synthetic namespace or local evidence-URL findings.

Fourteen avoidable missing-description warnings found in an earlier run were eliminated before the final retained evidence was created. The warning families, rationale and claim effects are recorded in `WARNING_ADJUDICATION.md`.

### HL7 FHIR Validator

Four positive validation units were executed:

1. authorisation-decision AuditEvent;
2. privacy-disclosure source AuditEvent;
3. positive Portable Evidence Bundle;
4. source clinical Bundle.

Result:

```text
positive units: 4
fatal findings: 0
error findings: 0
```

Two negative units were executed:

1. privacy-disclosure AuditEvent without the required recipient agent;
2. portable evidence Bundle containing an Observation.

Result:

```text
negative units: 2
intended negative rejections: 2
unintended negative rejection: 0
accepted negative unit: 0
```

The first negative exposes the required BALP recipient/minimum-cardinality failure. The second exposes the local Bundle-profile closure that excludes `Observation`. The summariser rejects a negative unit if it fails only for an unrelated reason.

The positive privacy-disclosure AuditEvent and positive Bundle retain a terminology warning concerning `iso-21089-lifecycle#disclose` in the recorded environment. This is reported and bounded; it is not converted into an error-free universal conformance claim.

## Complete hosted release contract

The hosted `make release-check` at workflow `30002019712` passed and produced no generated repository drift. Its retained transcript reports:

| Check | Result |
|---|---:|
| Unit/regression pytest items | 41 passed |
| Property-test pytest items | 8 passed |
| Mandatory skips observed | 0 |
| Finite bounded checks | 29,105 |
| Bounded failures | 0 |
| Canonical objects checked | 729 |
| Append transitions checked | 1,641 |
| Inclusion proofs checked | 1,641 |
| Consistency proofs checked | 1,278 |
| Same-size fork pairs checked | 4,059 |
| Verifier checkpoint advances | 16 |
| Reproducibility-manifest rows | 52 current |
| Result contracts | 10 |
| Parsed retained-result rows | 472 |
| Distributed files | 349 |
| SHA-256 entries | 348 |
| File-manifest rows | 347 |
| HIE retained files | 41 current |
| C3 positive validation units | 4 |
| C3 intended negative rejections | 2 of 2 |
| Quick-pipeline events | 48 |
| Successful receipt checks | 16 |
| Quick controlled mutations | 2 |
| Quick mutations rejected | 2 of 2 |
| Ordinary verification failures | 0 |
| Validation failures | 0 |
| Quick result rows | 66 |
| Deterministic-output comparison | PASS |
| Workload semantic invariants | PASS |
| Integrity patch | 0 bytes |
| Final contract | `RELEASE-CHECK: PASS` |

The quick-pipeline mutation count is baseline smoke evidence only. It must not be substituted for the broader preregistered C4 adversarial suite.

## Defects exposed and corrected during C3

The repair history is part of the audit trail:

1. **Floating-point fixture incompatibility.** The first HIE fixture used Python floats not admitted by `TE-JCS-1`. Route C adopted explicit integer-valued synthetic fixtures without weakening the baseline canonicalisation rule.
2. **Over-broad payload scanner.** The first scanner treated every FHIR `valueString` as clinical content. It was corrected to distinguish non-clinical audit details from clinical values.
3. **Missing Jekyll executable.** IG Publisher reached the rendering stage but could not invoke Jekyll. Ruby 3.3 and Jekyll 4.4.1 were added to the hosted toolchain.
4. **Malformed IG-template selection.** A legacy template path was replaced with a maintained explicit template version.
5. **Invalid or unresolved fixture vocabulary.** Non-existent Device coding and dangling source-resource relations were replaced by valid optional-element handling and typed versioned identifiers.
6. **Non-standard media type warning.** The exact signed JSON bytes are now carried using `application/json`; the project profile remains explicit in the signed content.
7. **Unintended negative-test success risk.** Negative validation now requires the registered failure family, not merely any validator error.
8. **Example-description configuration error.** The first description mapping used incorrect resource keys. It failed the publisher and was corrected to `ResourceType/id` identifiers.
9. **Build-residue contamination.** The first materialisation retained a downloaded IG template tree. The cleaner, materialisation script, integrity builder and offline checker now reject rendered-site, template and cache residue.
10. **Pre-materialisation manifest drift.** The strict integrity contract correctly rejected unlisted C3 artefacts. Manifests were regenerated only after the official evidence was retained.

No failed attempt was reclassified as a success. Each defect was repaired and rerun under the same claim ceiling.

## Claim decisions after C3

### Claims now permitted

- A complete **synthetic** cross-organisational disclosure case traversed the reported Route C pipeline.
- The case instantiated the four-class portable/referenced/committed/excluded boundary for its frozen accountability questions.
- Exact signed-envelope bytes were preserved in the FHIR Binary and checked byte-for-byte.
- The inspected positive portable Bundle contained neither Observation nor DiagnosticReport resources and exposed no declared forbidden clinical-value path.
- The exact four positive validation units completed the declared FHIR R4/local-IG/applicable-BALP pathway without fatal or error findings.
- The two declared negative units were rejected for their intended constraints.
- The compact C3 evidence package and its integrity manifests passed the hosted offline release contract.

### Claims still prohibited

- real-patient or operational-hospital case;
- FHIR compliance without exact corpus and profile qualification;
- universal BALP conformance;
- IHE or HL7 certification;
- production readiness or healthcare-network scalability;
- clinical validity or clinical truth;
- legal compliance;
- privacy guarantee or zero re-identification risk;
- encryption by hashing;
- SCITT or RFC 9942 receipt conformance;
- public transparency or global non-equivocation;
- total production EHR overhead;
- expert-validated boundary completeness.

## Reviewer-closure effect

C3 directly addresses the most concrete part of Reviewer 1's request for a medical evidence object and detailed process:

- the input is a concrete synthetic DiagnosticReport disclosure case;
- the source data, Consent, policy, decision, actor role, organisations and resource version are explicit;
- the end-to-end tool sequence is executable and retained;
- exact evidence-envelope and FHIR resources are supplied;
- hashing, commitment, signature and backend receipt are separated conceptually and in code;
- official FHIR tooling has been executed;
- positive and negative outputs are archived.

C3 does not close Reviewer 1's total-overhead request; that remains C5. It does not close the full security mutation request; that remains C4. It does not remove the need to explain transport and at-rest encryption as deployment controls in C7.

C3 also materially supports Reviewer 2's requests for concrete data, an input–processing–output explanation, case-based evaluation and understandable research execution. The manuscript and figures still require reconstruction in C7 before those comments can be marked closed.

## Residual work transferred to later phases

| Residual obligation | Owning phase |
|---|---|
| Expanded issuer-signature field substitutions and wrong-key tests | C4 |
| Payload and nonce commitment mutations | C4 |
| Local A2 index, size, root, path, key and checkpoint mutations | C4 |
| State non-advancement after failed verification | C4 |
| Encryption/confidentiality wording and deployment controls | C4/C7 |
| B0–B2 paired local overhead experiment | C5 |
| p50, p95 and p99 processing/byte increments | C5 |
| Release-wide privacy, secret and residue scan | C6 |
| v2.2.0 metadata and fresh-extraction release candidate | C6 |
| Manuscript integration, figures and tables | C7 |
| Point-to-point reviewer response | C8 |
| Public GitHub and Zenodo release | C9 |

## Gate checklist

| C3 criterion | Verdict |
|---|---|
| Frozen concrete medical case | PASS |
| Synthetic status explicit | PASS |
| Separate HIE schema and profile | PASS |
| `TE-HIE-Min-1` | PASS |
| Consent v3, policy v6 and D-204 | PASS |
| Versioned DiagnosticReport source | PASS |
| Exact source-payload commitment | PASS for the retained case |
| Signed TrustEvidence envelope | PASS |
| Project-specific local A2 receipt | PASS for the retained case |
| Exact Binary bytes | PASS |
| Positive portable payload exclusion | PASS for declared fields/types |
| SUSHI | PASS |
| IG Publisher | PASS with 33 adjudicated warnings |
| Positive FHIR Validator corpus | PASS: 4/4 without fatal/error |
| Intended negative corpus | PASS: 2/2 intended rejections |
| Warning suppression | PASS: none |
| Retained compact evidence | PASS |
| Build-residue exclusion | PASS |
| Offline retained-evidence checker | PASS |
| Current checksums and file manifest | PASS |
| Complete hosted `make release-check` | PASS |
| Generated repository drift | PASS: none |
| Claim–Evidence Ledger updated | PASS |
| Standards status updated | PASS |
| Hostile review completed | PASS |
| **Gate C3** | **PASS** |

## Final C3 verdict

> The Route C branch now contains a complete, concrete and reproducible synthetic healthcare disclosure case whose exact positive and negative FHIR artefacts were exercised through the declared SUSHI, IG Publisher and HL7 FHIR Validator pathway. The retained evidence supports a bounded case-level and corpus-level result. It does not support universal conformance, certification, deployment, clinical, legal or production claims.

C3 is closed. C4 may begin without reopening C3 unless a later mutation or release check falsifies a C3 invariant.
