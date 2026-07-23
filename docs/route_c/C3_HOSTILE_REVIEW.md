# Final hostile review of Phase C3

## Audit verdict

```text
Hero-case implementation:                PASS
Semantic and payload-custody checks:     PASS
Official hosted FHIR toolchain:          PASS
Positive Validator units:                4/4 without fatal or error findings
Intended negative Validator units:       2/2 rejected for registered families
Retained repository evidence:            PASS
Offline retained-evidence checker:       PASS
Complete hosted release contract:        PASS
Integrity patch:                         0 bytes
Gate C3:                                 PASS
```

This verdict is bounded to the exact retained Route C corpus, local implementation-guide package, tool versions, terminology endpoint and JAR digests. A hostile reviewer should continue to assume that no broader healthcare, conformance, privacy, deployment or cryptographic property exists unless later phases provide separate evidence.

## Adversarial thesis

The strongest hostile interpretation is that C3 is a well-engineered, self-consistent synthetic demonstration. That criticism is partly correct. C3 is not a hospital deployment, not a patient study and not a certification exercise. Its value lies in the fact that the artefacts are concrete, independently exercised by official tools, retained with their failures and warnings, and constrained by an explicit claim ceiling.

## Attack 1 — “This is still not a real medical example”

### Attack

Reviewer 1 requested a real evidence entity/resource containing real data. A purely synthetic case could be presented as an evasion.

### Finding

The case is medically concrete but not operational:

- versioned DiagnosticReport;
- three laboratory Observations with explicit source values;
- source and recipient hospitals;
- treatment purpose;
- Consent version 3;
- policy version 6;
- decision D-204;
- signed evidence envelope;
- local A2 receipt;
- portable FHIR projection.

The case is labelled synthetic at every relevant layer. Clinical values remain under source custody and are not copied into the portable Bundle.

### Verdict

**Defensible as a complete synthetic medical case only.** The manuscript and response must not say `real patient`, `operational hospital`, `clinical deployment` or `real-world validation`. The reviewer request is answered through concreteness and inspectability, not by falsely claiming a clinical deployment.

## Attack 2 — “The boundary merely removes data until the fixture passes”

### Attack

A minimisation claim is trivial if fields are excluded without an accountability rationale.

### Finding

The field decisions were frozen through nine accountability questions and recorded in:

```text
docs/route_c/C3_NECESSITY_AUDIT.md
docs/route_c/HIE_BOUNDARY_MATRIX.csv
```

Consent state, policy version, decision identity and event outcome remain distinct. The source DiagnosticReport is version-identified; the exact source Bundle is committed; clinical values, direct identity and the nonce are excluded.

### Residual weakness

No clinician, auditor, data-protection officer or legal expert has established institutional sufficiency.

### Verdict

**Bounded design evidence, not expert-validated minimisation.** RQ1 may be supported for the frozen case, not universally.

## Attack 3 — “The author invented a private schema instead of using FHIR”

### Attack

A project JSON envelope may become an unrecognised parallel standard.

### Finding

FHIR R4 and applicable BALP AuditEvent profiles are used for the structured healthcare projection. The project envelope carries the exact signed semantic statement and local receipt. The Binary preserves exact canonical JSON bytes; the FHIR resources expose selected semantics for healthcare tooling.

### Residual weakness

No independent implementation consumes `TE-HIE-Envelope-1`, and no standards body recognises the project profile.

### Verdict

**Executable reference profile only.** No new-standard or universal interoperability claim is permitted.

## Attack 4 — “The portable Bundle cheats by referencing an absent local resource”

### Attack

A relative `DiagnosticReport/.../_history/2` reference inside the portable Bundle would be a dangling local link rather than a meaningful cross-organisational reference.

### Finding

The source resource is represented by type plus a versioned identifier, not a local `reference` element. The semantic checker fails if the relative source reference reappears. The positive portable Bundle contains neither DiagnosticReport nor Observation resources.

### Verdict

**Addressed for the exact corpus.** Operational resolver and enterprise identifier-governance behaviour remain untested.

## Attack 5 — “The signature authenticates different bytes from the FHIR resources”

### Attack

A signature over a project JSON serialisation cannot automatically authenticate a separately generated FHIR representation.

### Finding

The project does not claim that the FHIR serialisation is the signed source of truth. The exact canonical signed-envelope bytes are embedded in `Binary` and compared byte-for-byte after Base64 decoding. Selected structured fields are checked for semantic parity.

### Residual weakness

Only the fields in the local parity checker are cross-layer assertions. No generic bidirectional converter or cross-language implementation exists.

### Verdict

**Exact-byte preservation established; universal semantic round-trip not established.**

## Attack 6 — “The commitment is marketed as encryption”

### Attack

Hashing with a nonce does not encrypt clinical data.

### Finding

The mechanism is consistently identified as a nonce-based payload commitment. The candidate bytes and nonce are required for verification. The nonce is retained as private fixture material and is absent from the portable Bundle.

### Verdict

**Terminology remains strict.** C4 and C7 must distinguish:

- payload commitment;
- issuer signature;
- receipt signature;
- TLS or other transport confidentiality, if deployed;
- encryption at rest, if deployed.

No confidentiality-by-hashing claim is permitted.

## Attack 7 — “The Merkle receipt is SCITT or a COSE Receipt in disguise”

### Attack

The use of Merkle inclusion and consistency concepts may invite unsupported standards language.

### Finding

The receipt framing, fields, signature, backend identity and application semantics are project-specific. The implementation does not provide SCITT registration, COSE Receipt structures, gossip, public witnessing or a transparency service.

### Verdict

**Project-specific local A2 receipt only.** C4 must execute the expanded receipt mutation corpus before stronger adversarial wording is allowed.

## Attack 8 — “Official validation only validates the author's permissive profile”

### Attack

A local profile may be made permissive enough that passing it proves little.

### Finding

The declared toolchain applies:

- FHIR R4 4.0.1;
- IHE BALP 1.1.4;
- the local Route C package;
- the FHIR terminology endpoint;
- four positive units;
- two intended negative units.

The authorisation and privacy-disclosure AuditEvents are separately validated against the applicable BALP profiles. The local portable Bundle profile closes `entry.resource` to declared evidence-resource types and rejects an appended Observation.

### Residual weakness

The result is corpus-bounded and is not an IHE certification event.

### Verdict

**Meaningful bounded validator evidence, not broad conformance.**

## Attack 9 — “The negative examples fail for arbitrary reasons”

### Attack

A malformed or multiply invalid file may fail without testing the intended property.

### Finding

The validator summariser contains an expected-failure registry. It requires:

- the missing-recipient AuditEvent to expose recipient/minimum-cardinality errors;
- the payload-containing Bundle to expose Observation/profile-closure errors.

A negative unit rejected only for an unrelated reason fails the summary.

### Verdict

**Addressed for the two declared FHIR failure families.** This does not replace the broader C4 cryptographic mutation suite.

## Attack 10 — “The warnings were hidden or waved away”

### Attack

A publisher result with dozens of warnings may be misreported as clean validation.

### Finding

The final retained publisher evidence reports:

```text
errors:               0
warnings:            33
information/hints:   16
broken links:         0
suppressed warnings:  0
suppressed hints:     0
```

The warning register explains:

- four unused base-template fragments;
- two OID recommendations;
- twenty-seven synthetic namespace or local URL findings.

Fourteen avoidable missing-description warnings identified in an earlier run were corrected. Nothing was suppressed.

### Verdict

**No warning-free claim is permitted.** The bounded pass is nevertheless defensible because there are zero errors, zero broken links and no hidden findings.

## Attack 11 — “An ephemeral Actions artefact is not reproducible evidence”

### Attack

A passing workflow artefact may expire and cannot by itself support a published claim.

### Finding

The branch retains:

- generated hero-case resources;
- generated FSH conformance resources;
- compact IG package;
- SUSHI and IG Publisher logs;
- IG Publisher QA;
- positive and negative Validator OperationOutcomes;
- semantic and validator summaries;
- tool versions and JAR digests;
- file manifest and checksums.

`check_c3_retained_evidence.py` verifies this package offline. The complete hosted `make release-check` passed on the retained tree.

### Verdict

**Attack addressed.** The hosted ZIP remains convenient evidence, but the durable repository package is authoritative.

## Attack 12 — “The retained package contains downloaded template and build debris”

### Attack

A release archive containing a downloaded IG template, rendered site and caches is bloated, unstable and potentially misleading.

### Finding

An early materialisation exposed exactly this problem. The following are now cleaned, excluded from integrity generation and rejected by the offline checker:

```text
standards/fhir_ig/output
standards/fhir_ig/temp
standards/fhir_ig/input-cache
standards/fhir_ig/template
```

The final integrity rebuild removed the generated-template rows. The final integrity patch was zero bytes.

### Verdict

**Attack addressed.** Build products are not distributed as scientific evidence.

## Attack 13 — “The HIE case silently breaks v2.1 behaviour”

### Attack

Adding HIE semantics might alter the personal-monitoring schemas, canonicalisation or retained baseline outputs.

### Finding

The HIE input and envelope schemas are separate. `TE-PHM-Min-1` remains unchanged. The full hosted release contract passed:

- 41 unit/regression pytest items;
- 8 property-test items;
- 29,105 bounded checks;
- deterministic retained-output comparison;
- legacy result contracts;
- metadata and integrity checks;
- quick baseline pipeline;
- the new HIE checks.

### Verdict

**Backward compatibility demonstrated for the executed regression contract.** This is not a promise of compatibility for untested external consumers.

## Attack 14 — “The privacy claim is stronger than the checker”

### Attack

Absence of deny-list terms does not prove privacy or anonymity.

### Finding

The checker covers declared resource types, declared clinical-value paths, exact Binary bytes and selected source-identifier relations. It does not model linkage attacks, metadata inference or all possible sensitive content.

### Verdict

Allowed:

> No declared forbidden clinical field or forbidden clinical resource type was found in the inspected positive portable artefacts.

Forbidden:

- privacy guaranteed;
- anonymous;
- zero re-identification risk;
- GDPR compliant.

## Attack 15 — “The research question was rewritten after the result”

### Attack

The question and claim may have been tuned to whatever the validators accepted.

### Finding

The four Route C research questions, Claim–Evidence Ledger and prohibited wording were frozen in C2. C3 repaired implementation defects while preserving the gate and claim ceiling. Failed intermediate runs and the repair history remain documented.

### Verdict

**Attack addressed.** The result is post-specification repair, not retrospective research-question substitution.

## Attack 16 — “The positive corpus still contains terminology warnings”

### Attack

The privacy-disclosure AuditEvent and Bundle retain a warning for `iso-21089-lifecycle#disclose`, so the result may be overstated.

### Finding

The warning is present in the retained OperationOutcomes and is not suppressed. The positive units have zero fatal and error findings under the declared environment. The manuscript will identify the exact corpus, profiles and toolchain rather than claim universal compliance.

### Verdict

**Bounded pass, not universal conformance.** The warning remains a visible limitation.

## Attack 17 — “C3 still does not answer total EHR overhead”

### Attack

Reviewer 1 explicitly requested total overhead.

### Finding

C3 provides an executable end-to-end case but does not provide the preregistered paired B0–B2 measurement. Existing local A2 timings are not a substitute for the complete reference-pipeline increment.

### Verdict

**Open by design and transferred to C5.** C3 must not be used to declare the overhead comment closed.

## Attack 18 — “C3 security evidence is too narrow”

### Attack

The retained case and two FHIR negatives do not establish robust signature, commitment and receipt mutation resistance.

### Finding

C1 retains baseline tests and C3 retains the concrete signed case. The wider Route C adversarial families — actor substitution, policy and Consent version mutation, wrong key, signature bytes, nonce, index, size, root, path and checkpoint state — remain unexecuted.

### Verdict

**Open by design and transferred to C4.**

## Final claim boundary

C3 permits:

- complete synthetic case;
- case-level four-class boundary instantiation;
- exact signed-byte preservation;
- absence of declared clinical payload types/paths in inspected positive portable artefacts;
- four positive units without fatal/error findings;
- two intended negative rejections;
- retained compact evidence and all-green hosted release contract.

C3 does not permit:

- real patient or operational hospital claim;
- universal FHIR/BALP conformance;
- certification;
- privacy or anonymity guarantee;
- production deployment or scalability;
- clinical truth;
- legal compliance;
- SCITT/RFC 9942 conformance;
- total EHR overhead;
- expert validation.

## Final hostile verdict

> C3 survives hostile review because it does not depend on rhetorical novelty or an ephemeral green badge. The branch contains a concrete synthetic medical case, exact signed bytes, a bounded FHIR/BALP-facing projection, official positive and intended-negative validator evidence, complete warning disclosure, an offline retained-evidence checker, current integrity manifests and an all-green hosted release contract. Its remaining weaknesses are explicit later-phase obligations rather than concealed C3 claims.

```text
Gate C3 = PASS
C3 open blockers = 0
Transferred blockers = C4 security mutations; C5 B0–B2 overhead; C6 release-wide QA; C7 manuscript; C8 response package
```
