# Hostile review of Phase C4

## Audit posture

A hostile reviewer should assume that a deterministic mutation suite built by the same author as the verifier can overstate assurance. The purpose of this audit is therefore not to celebrate a green table. It is to identify which observations genuinely constrain the implementation, which depend on the project trust configuration and which remain negative results.

## Evidence examined

- frozen and amended C4 protocol;
- attack-family registry;
- original failed hosted result from workflow `30005609826`;
- protocol-deviation record and original artifact digest;
- retained 67-row final decision corpus;
- per-case evidence JSONL;
- state snapshots before and after verification;
- payload-commitment controls;
- current HIE schemas, issuer verifier and local A2 verifier;
- deterministic regeneration and result-contract controls;
- hosted CI and integrity artefacts, once the final synchronised run completes.

## Attack 1 — “The suite proves security because the author labelled all rows PASS”

### Finding

The final corpus distinguishes three outcome types:

- expected acceptance;
- expected rejection;
- expected absence from inspected portable artefacts.

It also distinguishes expected limitation acceptances from attack rejections. The final result contains 67 cases: 54 expected rejections, 11 expected acceptances and two expected-absence checks. All final registered decisions match their observed decisions. Six accepted cases are explicit limitations rather than security successes.

### Verdict

**The suite may support decision consistency, not generic security.** Any manuscript table that reports only “67/67 passed” without separating the 54 rejections from the six limitation acceptances would be misleading.

## Attack 2 — “The protocol was rewritten after a false accept”

### Finding

The first hosted run produced one false accept under the original registry: `RSIG-005`. The original materialisation job failed, did not commit its results and uploaded an artifact with digest:

```text
sha256:7e4835bac2606f52dc9e62131aab682c91fe2b65eab1fe4eed4d07d4e53d4799
```

The result was not hidden. `C4_PROTOCOL_DEVIATION.md` records the original expectation, workflow, job, artifact digest, observed acceptance and subsequent amendment. The case was renamed `LIM-BACKEND-002` and converted into a negative claim-boundary result.

### Residual risk

Post-observation amendment introduces an obvious risk of HARKing. The mitigation is documentary rather than magical: the original failure remains retrievable, the case count remains unchanged, the verifier was not weakened and the amended claim is less ambitious.

### Verdict

**Acceptable only because the original failure is preserved and the claim is narrowed.** It would be unacceptable to present the final zero-false-accept count without disclosing the amendment.

## Attack 3 — “A valid issuer signature proves who acted and whether Consent or policy was true”

### Finding

Stale-signature changes to actor, organisation, Consent version, policy version/digest, decision, outcome, resource version and provenance are rejected. Wrong key material and corrupted signature bytes are also rejected under the deterministic fixture registry.

However, three newly signed, schema-valid alternatives are accepted when the authorised issuer key is used. These cases show that signature validity authenticates the issuer statement; it does not independently establish identity proofing, Consent truth, policy truth or clinical truth.

### Verdict

**Unauthorised mutation detection is supported; statement truth is not.** Legal non-repudiation and post-compromise security remain unestablished.

## Attack 4 — “The payload commitment encrypts or anonymises the clinical data”

### Finding

The exact canonical source bytes and test nonce reproduce the commitment. Changed payload bytes, an alternate JSON serialisation, changed nonce, changed representation profile, changed context and a nonce shorter than 128 bits are rejected under the declared commitment framing.

The mechanism remains SHA-256 commitment, not encryption. The verifier requires the candidate bytes and nonce. The package retains the nonce as labelled deterministic test material. The nonce is absent from the inspected signed envelope and Portable Evidence Bundle, but this does not make the distribution anonymous or the source payload confidential.

### Verdict

**Exact-byte integrity binding is supported. Encryption, confidentiality, anonymisation and zero re-identification risk are not.**

## Attack 5 — “A receipt proves the backend was honest and the log contained the asserted number of events”

### Finding

Stale-signature and wrong-key receipt changes are rejected. Re-signed changes to core binding, proof path, root, leaf index, proof digest, backend identity and log identity are also rejected where they violate independently checked relations.

The first hosted run falsified the expectation that a coherently changed and re-signed tree size would necessarily fail. `LIM-BACKEND-002` is accepted: the authorised backend can sign an internally admissible alternative tree-size statement. The verifier has no independent evidence of actual log population.

### Verdict

**Receipt authentication is not backend-honesty evidence.** No completeness, truthful-tree-size, trustworthy-operator or post-key-compromise claim is permitted.

## Attack 6 — “Merkle inclusion proves a complete audit trail”

### Finding

The verifier checks the supplied leaf, index, tree size, path and root. Inclusion establishes membership relative to the supplied local tree statement. It does not instrument event capture and cannot show that omitted events were ever presented to the log.

### Verdict

**Membership, not completeness.** The phrases `complete audit trail`, `all events captured`, `immutable history` and equivalents remain prohibited.

## Attack 7 — “Retained state prevents equivocation”

### Finding

The stateful wrapper:

- accepts the same retained checkpoint without changing state;
- rejects a smaller valid tree as rollback;
- rejects a same-size divergent root as a verifier-visible fork;
- rejects a larger tree without a consistency proof;
- rejects mutated proof path, root, size and identity;
- accepts a valid prefix extension and advances state once;
- rejects the old valid receipt after advancement;
- leaves state unchanged after all eight rejected state cases.

A coherent alternative view remains accepted by a stateless verifier. Two isolated verifiers can therefore be shown different signed states unless they compare checkpoints or use another witnessing mechanism.

### Verdict

**Local retained-state checking is supported; global non-equivocation is not.** No gossip, witness, public transparency or cross-verifier consistency claim is permitted.

## Attack 8 — “The verifier prevents replay”

### Finding

A receipt transplanted to a different signed core is rejected by core binding. An exact same-state replay is accepted and does not change the checkpoint.

### Verdict

**Cross-core transplant rejection is supported; duplicate replay prevention is absent.** Freshness, nonce tracking, event-id uniqueness and business-level idempotency are higher-layer controls.

## Attack 9 — “State non-advancement is a production safety property”

### Finding

The in-memory wrapper updates its checkpoint only after complete acceptance. Every rejected state case retained the exact pre-verification tuple. This is useful executable evidence.

The wrapper does not persist state, perform atomic durable writes, recover after crashes, coordinate concurrent verifiers or protect the checkpoint from local administrative compromise.

### Verdict

**In-memory transition discipline only.** No database transaction, recovery or production-state-safety claim is permitted.

## Attack 10 — “The suite is independent”

### Finding

The suite, verifier and fixtures are implemented in the same Python package and use the same deterministic key material. Official FHIR tooling supplies partial external tool diversity for C3, but C4 has no independent cryptographic implementation or cross-language verifier.

### Verdict

**Self-hosted adversarial testing, not independent verification.** Deterministic reruns and hosted CI reduce accidental error; they do not remove common-mode implementation risk.

## Attack 11 — “The deterministic test keys model operational key management”

### Finding

The keys are deliberate TEST-ONLY fixtures. They make results reproducible and allow wrong-key controls.

The study does not evaluate HSMs, certificate chains, issuer onboarding, revocation, rotation, compromise response, trust-anchor distribution or key-custody separation.

### Verdict

**Algorithmic fixture evidence only.** No operational identity or key-management assurance.

## Attack 12 — “TLS and encryption at rest protect the exchange”

### Finding

The reference pipeline does not open a hospital-to-hospital network connection. Build-system HTTPS and terminology-server traffic are not evidence about the proposed healthcare exchange. No database or storage encryption configuration is executed.

### Verdict

**Not evaluated.** The manuscript must describe TLS and at-rest encryption only as deployment controls, not as measured TrustEvidence properties.

## Attack 13 — “Closed schema means future extensions are safe”

### Finding

Unknown critical fields are rejected by the exact profile. This prevents silent interpretation of unexpected fields in the current version.

It does not define version negotiation, backward compatibility, extension governance or safe processing of future profiles.

### Verdict

**Exact-version admission only.** No future-version interoperability claim.

## Attack 14 — “The mutation corpus is a penetration test”

### Finding

The corpus targets declared semantic, cryptographic and state relations. It does not test parser memory safety, denial of service, timing side channels, dependency compromise, operating-system hardening, API authentication, network attacks or human workflow abuse.

### Verdict

**Property-specific mutation testing, not penetration testing or production security assessment.**

## Consolidated hostile verdict

C4 materially improves the article because it replaces the original manuscript's seven broad tamper/receipt statements with an inspectable, case-level decision corpus and makes negative results first-class evidence. The most important finding is not that 67 rows match the amended registry. It is that the first run falsified an over-strong tree-size expectation and forced a narrower interpretation of receipt assurance.

C4 is defensible when reported as follows:

> Under the exact synthetic profile and deterministic test trust configuration, the final 67-case registry contained 54 expected rejections, 11 expected acceptances and two expected-absence checks. All final registered decisions were reproduced, rejected state cases did not advance the retained checkpoint and six accepted cases explicitly delimited authorised-signer truth, backend honesty, stateless split-view and replay limitations. The first hosted run's falsified tree-size expectation is retained separately and disclosed.

C4 is not defensible if reduced to:

```text
all attacks blocked
secure and immutable
complete audit trail
backend honesty proven
replay prevented
encryption implemented
```

## Gate condition

The scientific decision corpus is complete. Final Gate C4 closure additionally requires a clean repository tree, current integrity manifests, passing result contracts, deterministic regeneration and one all-green hosted `make release-check` after removal of temporary materialisation machinery.
