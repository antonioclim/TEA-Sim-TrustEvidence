# Hostile review of Phase C3

## Audit status

This is the pre-materialisation hostile audit for the Route C cross-organisational healthcare case and official FHIR validation pathway. It must be updated after retained evidence and the final full release contract pass. Until then, Gate C3 remains open.

## Adversarial thesis

A hostile reviewer should assume that the C3 work is an elaborate self-consistent demonstration that still fails to establish anything beyond the author's own fixtures. The burden is therefore to show, without rhetorical substitution, which parts are independently exercised by official tooling, which parts remain project-specific and which interpretations are prohibited.

## Attack 1 — “This is still not a real medical example”

### Attack

The case is synthetic. Calling it “real” would evade Reviewer 1's request rather than satisfy it.

### Finding

The case is concrete rather than operational:

- a versioned DiagnosticReport;
- three laboratory Observations with explicit values in the source Bundle;
- source and recipient hospitals;
- a treatment purpose;
- Consent version 3;
- policy version 6;
- authorisation decision D-204;
- a signed evidence envelope;
- a local A2 receipt;
- a portable FHIR projection.

The clinical values remain outside the portable evidence. All resources are labelled synthetic.

### Verdict

**Defensible only as a complete synthetic medical case.** The manuscript and response must not use `real patient`, `operational hospital`, `clinical deployment` or `real-world validation`.

## Attack 2 — “The boundary merely removes data until the example passes”

### Attack

A minimisation claim is trivial if fields are excluded without an accountability rationale.

### Finding

The field decisions are governed by frozen questions and recorded in `C3_NECESSITY_AUDIT.md` and `HIE_BOUNDARY_MATRIX.csv`. Consent state, policy version, decision identity and event outcome are deliberately distinct. The source DiagnosticReport is identified by type and version; the exact source Bundle is committed; clinical values, direct identity and the nonce are excluded.

### Residual weakness

No clinician, auditor, data-protection officer or legal expert has validated that the selected field set is institutionally sufficient.

### Verdict

**Bounded design evidence, not expert-validated minimisation.** RQ1 may be supported for the frozen case only.

## Attack 3 — “The author invented a new schema instead of using FHIR”

### Attack

A project JSON envelope can become a private parallel standard.

### Finding

FHIR R4 and applicable BALP AuditEvent profiles are used as the structured healthcare projection. The project envelope retains the exact signed semantic statement and local receipt. The Binary carries exact canonical JSON bytes; the FHIR resources make selected semantics inspectable. The manuscript must explain that these layers serve different purposes.

### Residual weakness

No independent implementation consumes the project envelope, and no standards body recognises `TE-HIE-Envelope-1` or `TE-HIE-Min-1`.

### Verdict

**Executable reference profile only.** No new-standard claim is permitted.

## Attack 4 — “The FHIR Bundle cheats by referencing absent resources”

### Attack

A relative `DiagnosticReport/.../_history/2` reference in a portable Bundle could be read as a broken local reference.

### Finding

The source resource is represented by a typed, versioned identifier rather than a local `reference` element. The semantic checker fails if the unresolved relative source reference reappears. The positive portable Bundle excludes DiagnosticReport and Observation resources.

### Verdict

**Attack addressed for the exact corpus.** Operational resolver behaviour remains untested.

## Attack 5 — “The signed bytes and the FHIR representation are different objects”

### Attack

A signature over one serialisation does not authenticate a separately generated FHIR representation.

### Finding

The project does not claim that the FHIR serialisation is the signed source of truth. The exact canonical signed-envelope bytes are embedded in a Binary and verified byte-for-byte after Base64 decoding. The structured projection is checked for selected semantic parity.

### Residual weakness

Only the fields included in the local parity checker are cross-layer assertions. No generic bidirectional converter or independent cross-language implementation exists.

### Verdict

**Exact-byte preservation established; universal semantic round-trip not established.**

## Attack 6 — “The commitment is marketed as encryption”

### Attack

Hashing with a nonce does not encrypt clinical data.

### Finding

The implementation and claim ledger call the mechanism a nonce-based payload commitment. The nonce is private test material, and the candidate source bytes are required for verification. Encryption is not implemented by this mechanism.

### Verdict

**Terminology must remain strict.** The response to Reviewer 1 must distinguish commitment, signature, transport encryption and storage encryption.

## Attack 7 — “The Merkle receipt is SCITT or a standard COSE Receipt in disguise”

### Attack

Using RFC-shaped Merkle algorithms may invite an unsupported standards claim.

### Finding

The receipt fields, signature framing, backend identity and application semantics are project-specific. The implementation is labelled a `project-specific local A2 Merkle receipt`. It does not implement a public transparency service, gossip, witnessing, SCITT registration or RFC 9942 COSE Receipt structure.

### Verdict

**Local receipt claim only.** C4 must extend the mutation corpus before the stronger Route C receipt wording is allowed.

## Attack 8 — “Official validation merely validates the author's profile”

### Attack

A local profile can be made permissive, so passing it is not meaningful.

### Finding

The declared toolchain validates against:

- FHIR R4 4.0.1;
- IHE BALP 1.1.4;
- the local Route C package;
- an official FHIR terminology server;
- four positive units;
- two intended negative units.

The privacy-disclosure and authorisation AuditEvents are validated separately against applicable BALP profiles. The local portable Bundle profile closes `entry.resource` to evidence-resource types and rejects an appended Observation.

### Residual weakness

The result remains corpus-bounded. It is not an IHE certification event and does not validate all possible instances.

### Verdict

**Meaningful bounded validator evidence, not broad conformance.**

## Attack 9 — “The negative tests fail for arbitrary reasons”

### Attack

A malformed or multiply invalid negative example proves little.

### Finding

The summariser maintains an explicit expected-failure registry. It requires the missing-recipient AuditEvent to expose the recipient/minimum-cardinality failure family and the payload-containing Bundle to expose the Observation/profile-closure failure family. A negative unit rejected only for an unrelated reason fails the C3 summary.

### Verdict

**Attack addressed for the two declared families.** C4 must provide the broader cryptographic and receipt mutation programme.

## Attack 10 — “Warnings were hidden or waved away”

### Attack

A publisher run with dozens of warnings can be misreported as a clean validation.

### Finding

The gate requires zero errors, zero broken links and zero suppressed warnings or hints. Every warning family is retained and adjudicated in `standards/fhir_ig/WARNING_ADJUDICATION.md`. Avoidable missing-description warnings have been remediated and require a rerun. Synthetic-namespace, optional OID and base-template warnings remain explicit limitations.

### Verdict

**No warning-free claim is permitted.** Final counts must be taken from retained outputs, not memory.

## Attack 11 — “The repository cannot reproduce the official result”

### Attack

An ephemeral Actions artefact is not a durable research package.

### Finding

C3 introduces a materialisation workflow that must retain:

- the generated hero-case resources;
- generated FSH conformance resources;
- compact IG package;
- SUSHI log;
- IG Publisher log and QA;
- HL7 Validator OperationOutcomes;
- semantic and validator summaries;
- tool versions and JAR digests;
- file manifest and checksums.

The full release contract is being extended with an offline retained-evidence checker.

### Stop condition

Until the materialisation commit exists and a subsequent hosted `make release-check` passes, C3 is not complete.

### Verdict

**Open pending materialisation and final green CI.**

## Attack 12 — “The case breaks v2.1 compatibility”

### Attack

Adding an HIE case could silently change the personal-monitoring semantics or invalidate retained v2.1 results.

### Finding

The HIE input and envelope schemas are separate. The existing personal-monitoring schemas and `TE-PHM-Min-1` are retained. The HIE wrapper adapts only the Route C fixture. Existing deterministic outputs must continue to match their retained references under the full release contract.

### Verdict

**Compatibility must be demonstrated by the final release-check, not inferred from code organisation.**

## Attack 13 — “The privacy claim is stronger than the scan”

### Attack

Absence of a deny-list term does not prove privacy or anonymity.

### Finding

The checker tests declared resource types, clinical-value keys, exact Binary bytes and selected source-identifier relations. It does not model linkage attacks, metadata inference or all possible sensitive content.

### Verdict

Allowed wording is limited to:

> No declared forbidden clinical field or forbidden clinical resource type was found in the inspected positive portable artefacts.

The following remain forbidden:

- privacy guaranteed;
- anonymous;
- zero re-identification risk;
- GDPR compliant.

## Attack 14 — “RQ2 is rewritten after observing the result”

### Attack

The question and claim may be tuned to fit whatever the validators accept.

### Finding

The four Route C research questions and Claim–Evidence Ledger were frozen in C2 before the final C3 toolchain execution. C3 repairs implementation defects, but the gate and prohibited wording remain unchanged.

### Verdict

**Acceptable if the final report preserves all failed attempts and does not erase the repair history.**

## Current hard blockers

At this pre-materialisation point, the blockers are:

1. retained C3 artefacts have not yet been committed;
2. integrity manifests do not yet cover the generated C3 evidence;
3. the offline retained-evidence checker has not yet passed in hosted CI;
4. the complete `make release-check` has not yet returned `PASS` on the materialised branch;
5. final publisher warning counts after description remediation are not yet frozen;
6. Claim–Evidence Ledger and standards status still describe the pre-C3 state.

## Provisional verdict

```text
hero case implementation                 PASS
semantic/privacy checker                 PASS in hosted successful run
official FHIR toolchain                  PASS in hosted successful run
positive Validator units                 4/4 without error
intended negative Validator units        2/2 rejected
retained repository evidence             OPEN
full release contract                    OPEN
Gate C3                                  NOT YET PASSED
```

C3 may be closed only after the retained artefacts, manifests, claim registry, standards status and final hosted CI all agree on one commit.
