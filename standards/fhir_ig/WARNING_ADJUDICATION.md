# C3 IG Publisher warning adjudication

## Final status

The retained C3 evidence was produced by the hosted Route C materialisation run `30000259599` and committed as `5aac6c946eecadc697a9ec455ca45d1e7ab640b6`. The retained `ig_publisher_summary.json` and `ig-publisher-qa.txt` report:

```text
IG Publisher errors:        0
IG Publisher warnings:     33
IG Publisher information:  16
Broken links:               0
Suppressed warnings:        0
Suppressed hints:           0
```

The same materialisation run retained four positive HL7 FHIR Validator units with zero fatal or error findings and two negative units rejected for their preregistered failure families. All publisher warnings and validator findings remain visible in the archive; no ignore rule converted a warning into an apparent pass.

The warning count is not interpreted as a conformance score. Each family is adjudicated by whether it changes the bounded Route C claim, signals a defect in the positive corpus or requires remediation before Gate C3.

## Final register

| ID | Final count | Warning family | Interpretation | Action | Gate effect |
|---|---:|---|---|---|---|
| C3-W01 | 0 | Missing `ImplementationGuide.definition.resource.description` for example resources | The first successful run exposed incomplete example metadata | Added explicit names, descriptions and `exampleBoolean: true` entries for all fourteen examples; the final run removed the family | Closed |
| C3-W02 | 4 | Base-template HTML fragments not included in the generated guide | Generic optional fragments are unused by the minimal one-page guide | Retained and documented | Non-blocking because errors and broken links are zero |
| C3-W03 | 2 | CodeSystem and ValueSet have no OID | IG Publisher recommends OIDs for possible OID-based terminology ecosystems such as CDA | No fictitious OID was assigned; canonical URLs are retained | Non-blocking; no OID/CDA interoperability claim |
| C3-W04 | 27 | Synthetic identifier namespaces and local evidence URLs have no published definition | The case intentionally uses non-operational namespaces and a local Binary relation, which the publisher cannot resolve as public canonical definitions | Retained; bounded by local reference checks, exact source-identifier checks, no dangling clinical reference and zero positive Validator errors | Non-blocking for the exact synthetic corpus; prohibits operational namespace-resolution claims |

The final warning count is therefore:

```text
0 remediated example-description warnings
+ 4 base-template warnings
+ 2 OID recommendations
+ 27 synthetic namespace/local URL warnings
= 33 retained warnings
```

## Detailed adjudication

### C3-W01 — example descriptions: closed

The initial warning affected fourteen generated example resources:

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

Each example now has an explicit name, description and `exampleBoolean: true` entry in `sushi-config.yaml`. The final hosted publisher run no longer reports this warning family.

### C3-W02 — unused base-template fragments

The minimal guide uses a single home page and a small profile set. The base template reports that four optional fragments are not referenced in the rendered guide:

- `ip-statements.xhtml`;
- one of the cross-version-analysis fragments;
- one of the dependency-table fragments;
- `globals-table.xhtml`.

These are presentation-template findings rather than FHIR instance or profile failures. Gate C3 nevertheless requires:

```text
IG Publisher errors = 0
broken links = 0
suppressed warnings = 0
suppressed hints = 0
```

A later publication-grade hosted IG may adopt a richer menu. Route C does not simulate a production documentation site merely to eliminate unused generic fragments.

### C3-W03 — absent OIDs

The project CodeSystem and ValueSet use canonical HTTPS URLs, but no registered object identifiers have been allocated. Assigning arbitrary OIDs merely to silence the publisher would create false interoperability metadata. The warning is retained and the manuscript will not claim CDA/OID ecosystem integration.

### C3-W04 — synthetic namespaces and local evidence relations

The synthetic case deliberately avoids operational identifiers. Test namespaces include:

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

They are not public terminology definitions. The absence of a resolvable public definition is expected, but creates a strict claim boundary: the case does not establish operational identifier governance or cross-enterprise namespace resolution.

The clinical source resource is not represented by a dangling relative reference. It is identified by resource type and a versioned identifier while the source Bundle remains outside the portable Bundle. The semantic checker requires:

- no unresolved `DiagnosticReport/.../_history/2` relative reference;
- the source identifier in the Consent derivative;
- the source identifier in the privacy-disclosure AuditEvent;
- the source identifier in Provenance;
- no DiagnosticReport or Observation resource in the positive portable Bundle;
- exact signed-envelope bytes in Binary.

The DocumentReference attachment URL identifies the Binary within the supplied evidence package. Exact bytes are checked directly, so the local relation is not used as a substitute for byte integrity.

## FHIR Validator warnings

The positive privacy-disclosure AuditEvent and the positive portable Bundle each retain one terminology warning for `iso-21089-lifecycle#disclose` under the declared validation environment. Neither positive unit contains a fatal or error issue. The warning is not interpreted as certification, and the manuscript must describe the resources as the exact validated corpus against the stated FHIR R4/local-IG/applicable-BALP toolchain, not as universally conformant implementations.

## Blocking findings

C3 treats any of the following as a stop-the-line condition:

- an error or fatal issue in a positive FHIR Validator unit;
- an IG Publisher error;
- a broken link reported by the publisher summary;
- any warning or hint suppression;
- an unresolved clinical-resource reference disguised as a portable local resource;
- an unknown-code error caused by an invented clinical or security CodeSystem;
- acceptance of the missing-recipient negative AuditEvent;
- acceptance of the Observation-containing negative portable Bundle;
- a negative example rejected only for malformed JSON or another unintended reason;
- retention of rendered-site, template or cache residue in the distributed package.

## Permitted wording

The retained evidence permits the following bounded statement:

> The exact C3 guide and example corpus completed the declared SUSHI, IG Publisher and HL7 FHIR Validator pathway with zero publisher errors, zero broken links, no suppressed findings and zero fatal or error findings in the four declared positive validation units. Two negative units were rejected for their intended profile constraints. Thirty-three retained publisher warnings concerned documented base-template, OID and synthetic-namespace limitations.

The warning adjudication does not permit:

- “warning-free implementation guide”;
- “FHIR compliant” without exact profile, corpus and toolchain qualification;
- “IHE certified”;
- operational identifier interoperability;
- production deployment readiness;
- universal BALP conformance.
