# C3 IG Publisher warning adjudication

## Status

**Pre-materialisation audit.** The successful hosted C3 toolchain run at commit `e77bbc03bb487cfb4a1fc6074fb9596193e8988e` completed with:

```text
IG Publisher errors:       0
IG Publisher warnings:    47
IG Publisher information: 16
Broken links:              0
Suppressed warnings:       0
Suppressed hints:          0
```

All warnings were retained. No ignore rule converted a warning into an apparent pass. Four declared positive units subsequently had zero FHIR Validator errors, and two declared negative units were rejected for their intended failure families.

The warning count is not interpreted as a conformance score. Each family is adjudicated by whether it changes the bounded Route C claim, whether it signals a defect in the positive corpus and whether it requires remediation before the C3 gate.

## Register

| ID | Count in successful pre-materialisation run | Warning family | Interpretation | Action | Gate effect |
|---|---:|---|---|---|---|
| C3-W01 | 14 | Missing `ImplementationGuide.definition.resource.description` for example resources | Documentation metadata was incomplete; the resource instances themselves had no validator errors | Added explicit names, descriptions and `exampleBoolean: true` entries for all fourteen examples in `sushi-config.yaml`; rerun required | Must be rechecked; not accepted as a permanent warning family |
| C3-W02 | 4 | Base-template HTML fragments not included in the generated guide | Generic template fragments were generated but unused by this minimal one-page guide | Retain and document; no scientific or instance-validity effect | Non-blocking if errors and broken links remain zero |
| C3-W03 | 2 | CodeSystem and ValueSet have no OID | IG Publisher recommends OIDs for possible OID-based terminology ecosystems such as CDA | Do not invent or imply an assigned OID for a bounded research artefact; retain canonical URLs and document the omission | Non-blocking; no OID interoperability claim |
| C3-W04 | 27 | Synthetic URN identifier systems and local evidence URLs have no published definition | The case intentionally uses non-operational synthetic namespaces and a local Binary relation; the publisher cannot resolve them as public canonical definitions | Retain synthetic identifiers; require local reference checks, exact source-identifier checks, no dangling relative clinical reference and zero positive Validator errors | Non-blocking for the exact synthetic corpus; prohibits operational identifier-resolution claims |

The expected final count after the C3 description remediation is therefore lower than 47, but the actual count must be read from the retained final `ig_publisher_summary.json`. This document will be updated with that count before Gate C3 is closed.

## Detailed adjudication

### C3-W01 — example descriptions

The warning affected fourteen generated example resources:

- two Organisations;
- one Patient;
- one Practitioner;
- one PractitionerRole;
- two Devices;
- one Consent;
- two AuditEvents;
- one Provenance;
- one Binary;
- one DocumentReference;
- one Bundle.

The warning did not assert that the resources were structurally invalid. Nevertheless, it was avoidable and affected the usability of the generated artefact list. Each example now has an explicit description in `sushi-config.yaml`. C3 will not treat this family as adjudicated until a hosted rerun demonstrates the outcome.

### C3-W02 — unused base-template fragments

The minimal guide uses a single home page and a small profile set. The base template reports that several optional fragments are not referenced in the rendered guide. These are presentation artefacts rather than FHIR instance or profile failures. The gate still requires:

```text
IG Publisher errors = 0
broken links = 0
suppressed warnings = 0
suppressed hints = 0
```

A future publication-grade hosted IG may adopt a richer menu and use more template fragments. Route C does not need to simulate a production documentation site to establish the bounded validator result.

### C3-W03 — absent OIDs

The project CodeSystem and ValueSet use canonical URLs. No registered object identifier has been allocated. Assigning an arbitrary OID merely to silence the publisher would create false interoperability metadata. The warning is retained and the manuscript will not claim CDA/OID ecosystem integration.

### C3-W04 — synthetic namespaces and local evidence relations

The synthetic case deliberately avoids operational identifiers. Identifier systems such as the following are test namespaces:

```text
urn:te:evidence-bundle
urn:te:token-system:hie-fixture-v1
urn:te:organisation-token
urn:te:service-token
urn:te:actor-token
urn:te:policy-authority:hospital-a
urn:te:policy-token:hie-disclosure
urn:te:evidence-id
urn:trustevidence:identifier:source-resource
```

They are not public terminology definitions. The absence of a resolvable public definition is therefore expected, but it creates a clear claim boundary: the case does not establish operational identifier governance or cross-enterprise namespace resolution.

The clinical source resource is not represented by a dangling relative reference. It is identified by resource type and a versioned identifier, while the source Bundle remains outside the portable Bundle. The local semantic checker requires:

- no unresolved `DiagnosticReport/.../_history/2` relative reference;
- the source identifier in the Consent derivative;
- the source identifier in the privacy-disclosure AuditEvent;
- the source identifier in Provenance;
- no DiagnosticReport or Observation resource in the positive portable Bundle;
- exact signed-envelope bytes in Binary.

The DocumentReference attachment URL identifies the Binary within the supplied evidence package. The exact bytes are also checked directly, so the local relation is not used as a substitute for byte integrity.

## Warnings that would be blocking

C3 treats any of the following as a stop-the-line condition:

- an error or fatal issue in a positive FHIR Validator unit;
- an IG Publisher error;
- a broken link reported by the final publisher summary;
- a warning suppression or hint suppression;
- an unresolved clinical-resource reference disguised as a portable local resource;
- an unknown-code warning caused by an invented clinical or security CodeSystem;
- acceptance of the missing-recipient negative AuditEvent;
- acceptance of the Observation-containing negative portable Bundle;
- a negative example rejected only for malformed JSON or another unintended reason.

## Allowed wording

After a successful final rerun, the retained warnings permit only bounded wording:

> The exact C3 guide and example corpus completed the declared SUSHI, IG Publisher and HL7 FHIR Validator pathway with zero publisher errors, zero broken links, no suppressed findings and zero errors in the four declared positive validation units. Remaining publisher warnings concerned documented example, template, OID or synthetic-namespace limitations and are reported in the archive.

The warning adjudication does not permit:

- “warning-free implementation guide”;
- “FHIR compliant” without exact profile and corpus qualification;
- “IHE certified”;
- operational identifier interoperability;
- production deployment readiness;
- universal BALP conformance.
