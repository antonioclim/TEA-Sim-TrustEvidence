# C3 necessity audit for the HIE disclosure case

## Status and purpose

This document records why each fact in the Route C cross-organisational disclosure case is portable, referenced, cryptographically committed or excluded. It is a design-decision audit, not a legal minimisation assessment and not an expert-validation result.

The audit applies only to the synthetic case `HIE-DISCLOSURE-001` and to the accountability questions frozen for the bounded JCIS revision. A field is not retained merely because FHIR, BALP or the JSON Schema can carry it. It is retained only when it answers a declared accountability question and no lower-exposure representation answers that question adequately.

## Frozen case

```text
Synthetic Hospital A
→ DiagnosticReport version 2
→ Synthetic Hospital B
→ purpose: treatment
→ Consent version 3, state active
→ policy version 6
→ authorisation decision D-204
→ signed TrustEvidence envelope
→ project-specific local A2 Merkle receipt
→ verification report
```

The source clinical Bundle contains a synthetic Patient, DiagnosticReport and three laboratory Observations. It is retained under source custody. The portable evidence Bundle contains no DiagnosticReport or Observation resource and no laboratory value.

## Accountability questions

The field selection is governed by nine questions.

1. **Event identity:** Which declared disclosure event is being examined?
2. **Temporal context:** When was the event reported to occur and when was its evidence emitted?
3. **Organisational direction:** Which source organisation issued the evidence and which recipient organisation received the disclosure?
4. **Actor and purpose:** Which role initiated or performed the action and for what declared purpose?
5. **Outcome:** What outcome did the source system record for the event?
6. **Authorisation context:** Which Consent version and state, policy version and authorisation decision were asserted?
7. **Clinical-object identity:** Which versioned clinical resource remained under source custody?
8. **Provenance and byte binding:** Which provenance relation and cryptographic commitment bind the portable evidence to the withheld source representation?
9. **Issuer and backend evidence:** Which key identifiers, signature and local receipt allow the supplied verifier to test the properties claimed by the reference implementation?

These questions do not ask whether the clinical result is true, whether the actor was correctly identity-proofed, whether all events were captured or whether the disclosure was legally sufficient. The Route C artefact therefore does not attempt to answer those questions.

## Decision procedure

For every candidate fact, the following order is used.

1. **Exclude** the fact when it does not answer a frozen accountability question or creates disproportionate disclosure risk.
2. **Reference** the fact when its identity and version are needed but its contents can remain with the source custodian.
3. **Commit** the exact bytes when later integrity comparison is needed but the bytes should not be portable.
4. **Make portable** only the smallest structured representation needed for cross-organisational inspection.
5. **Reject free text** when a controlled value, versioned identifier, digest or typed reference provides the necessary meaning.

The classes are mutually interpretable but not mutually exclusive at object level. For example, the DiagnosticReport is referenced by type and version, while the exact source Bundle containing it is also committed. Its clinical values remain excluded.

## Necessity decisions

### Event identifiers and time

`source_event_id`, `evidence_id`, `event_type`, `occurred_at` and `emitted_at` are portable. Without stable event identity and bounded time context, an auditor cannot distinguish the disputed disclosure from another event or determine which evidence statement is being verified.

The identifiers are synthetic opaque tokens. They are not patient identifiers and do not establish that the event occurred in an operational system. The time-source identifier, precision and maximum declared skew are portable because timestamp comparison is otherwise uninterpretable; they do not prove clock synchronisation.

### Source, recipient and actor

Source and recipient organisation tokens are portable because directionality is central to a cross-organisational disclosure dispute. The evidence carries synthetic organisation identifiers rather than legal names or operational identifiers.

The actor token, role and organisation association are portable. Direct person identity, professional-registration number, e-mail address, address and credentials are excluded. Route C tests role-bound evidence, not operational identity proofing. The FHIR projection therefore uses a pseudonymous Practitioner and PractitionerRole rather than a named clinician.

### Purpose and outcome

The controlled treatment-purpose code and recorded success outcome are portable because they answer different questions: why the system says the disclosure was performed and what result it recorded. Neither value proves legal basis, clinical necessity or actual downstream use.

### Consent, policy and decision

Consent reference, version `3` and active state are portable. The full Consent record remains represented only by a minimised derivative and source-system custody; the portable evidence does not copy a complete patient-facing consent document.

Policy reference and version `6` are portable. A policy digest is also portable because it can bind a retrieved policy representation to the version asserted in the event. The complete policy text and institutional interpretation are not portable.

Authorisation decision `D-204` is represented as a distinct versioned decision object and in the authorisation AuditEvent. It is not collapsed into the Consent state, policy version or event outcome because those constructs answer different accountability questions:

```text
Consent state           → recorded patient-choice state
policy version          → rule artefact asserted by the source system
authorisation decision  → decision instance produced by the decision service
event outcome           → result recorded for the disclosure event
```

A distinct decision identifier is therefore necessary. Route C does not claim that `D-204` was legally correct or that the decision service was operationally trustworthy.

### Clinical resource and source payload

The portable evidence identifies `DiagnosticReport/diagnostic-report-hie-001/_history/2` by resource type and versioned identifier. It does not carry an unresolved relative FHIR reference that implies the clinical resource is present in the portable Bundle.

The source clinical Bundle is committed using the declared `sha256-nonce-v1` profile, the representation profile `application/fhir+json-rfc8785-v1`, the context `diagnostic-report-source-v1` and a test-only nonce retained outside portable artefacts. This permits the supplied verifier to detect changes when it is later given the exact candidate bytes and nonce.

The following remain under source custody or are excluded from the portable layer:

- DiagnosticReport content;
- Observation resources and values;
- narrative conclusion;
- patient name, date of birth and address;
- operational medical-record identifiers;
- source-system access tokens and credentials;
- commitment nonce;
- private signing keys.

A hash is not encryption. The commitment supplies a bounded integrity comparison under the declared inputs; it does not provide confidentiality, clinical meaning or proof of correctness.

### Provenance

A provenance reference is portable because the case must distinguish the source clinical resource, the generated audit resources and the exact signed-envelope Binary. The portable FHIR Provenance identifies the source DiagnosticReport by typed, versioned identifier and links the generated AuditEvents and Binary. It does not copy the source resource.

### Signature and receipt

The issuer key identifier and Ed25519 signature are portable because the supplied verifier must know which configured public key to use and which bytes are authenticated. The signature authenticates the evidence statement under the test trust configuration. It does not prove clinical truth, legal non-repudiation, identity proofing or post-compromise security.

The project-specific local A2 receipt is portable because the study evaluates receipt binding, inclusion and retained-checkpoint consistency. It contains the backend and log identifiers, core digest, leaf hash, leaf index, tree size, root digest, inclusion material, issue time and backend signature. It is deliberately labelled a local A2 receipt rather than a SCITT or RFC 9942 receipt.

## FHIR projection decision

FHIR R4 and applicable IHE Basic Audit Log Patterns provide the healthcare audit representation substrate. The Route C projection contains:

- a BALP-facing consent-authorisation AuditEvent;
- a BALP-facing privacy-disclosure AuditEvent;
- a Consent derivative;
- Provenance;
- pseudonymous Patient, Practitioner and PractitionerRole context;
- source and recipient Organisations;
- evidence and authorisation service Devices;
- a Binary containing the exact canonical signed-envelope bytes;
- a DocumentReference pointing to the Binary and related evidence resources;
- a profiled collection Bundle.

The structured projection is inspectable by FHIR tooling, while the Binary preserves the exact bytes whose signature and receipt are verified. A FHIR reserialisation is not treated as the signed source of truth.

The portable Bundle profile closes `entry.resource` to the evidence-resource types required by the case. Observation and DiagnosticReport are not admitted. The deliberate negative Bundle appends an Observation and must fail the declared official validator toolchain for that reason.

## Backward-compatibility decision

The HIE case uses separate input and envelope schemas and the minimisation profile `TE-HIE-Min-1`. It does not relabel a DiagnosticReport as a personal-monitoring summary and does not remove the v2.1 personal-monitoring vocabulary. This keeps the Route C extension additive while allowing a future release decision to determine whether the combined change remains appropriate for `v2.2.0`.

## Falsification conditions

The C3 boundary must be narrowed or rejected if any of the following occurs:

- a frozen accountability question cannot be answered without copying a clinical value;
- a portable field has no traceable accountability purpose;
- the DiagnosticReport or an Observation appears in the positive portable Bundle;
- the Binary does not preserve the exact canonical signed-envelope bytes;
- a source-resource link is represented as a dangling local reference;
- the positive case fails an undeferred official-validator error;
- a declared negative example is accepted or fails only for an unrelated reason;
- the Consent, policy, decision or resource versions drift across the envelope and FHIR projection;
- the retained reports cannot be reproduced from the checked-in source.

## Claim ceiling after a successful C3 gate

A successful C3 gate permits the following bounded statement:

> The complete synthetic disclosure case traversed the Route C input, minimisation, signed-envelope, FHIR R4/BALP-facing projection, local A2 receipt and verification path. The four declared positive validation units passed the specified SUSHI, IG Publisher and HL7 FHIR Validator toolchain, and two negative units were rejected for their intended failure families.

It does not permit:

- FHIR compliance in general;
- IHE certification;
- universal BALP conformance;
- clinical validation;
- operational hospital deployment;
- event completeness;
- privacy guarantee;
- legal compliance;
- production performance;
- SCITT or RFC 9942 conformance.
