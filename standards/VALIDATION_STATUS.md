# Standards validation status

## Route C C3 status

The exact synthetic HIE corpus and local implementation-guide package retained under `standards/fhir_ig/` were executed in the hosted Route C toolchain. This status applies only to the recorded resources, package versions, tool versions, terminology endpoint and JAR digests. It is not an IHE certification or a universal conformance statement.

| Layer | Executed status | Permitted wording |
|---|---|---|
| Project HIE JSON schemas | Positive hero-case input and signed envelope accepted by the closed project schemas; declared missing-decision and payload-leakage inputs rejected | closed project schemas for the reported Route C case |
| Semantic/privacy projection checks | Exact Binary bytes preserved; no `Observation` or `DiagnosticReport` in the positive portable Bundle; no declared clinical-value path or dangling local source reference | the inspected Route C portable artefacts excluded the declared clinical payload fields |
| FHIR R4 source and projection | Four declared positive validation units contained zero fatal or error findings under FHIR R4 4.0.1, the local IG package and applicable BALP 1.1.4 profiles | the exact reported examples passed the declared validation pathway |
| IHE BALP 1.1.4 | The authorisation and privacy-disclosure AuditEvents were validated against the applicable BALP profiles used by the corpus | BALP-facing projection; applicable BALP-profile validation for the exact AuditEvents |
| SUSHI | SUSHI v3.20.0 generated four profiles, one CodeSystem and one ValueSet with zero errors and zero warnings | compiled by the recorded SUSHI toolchain |
| IG Publisher | Retained QA reports zero errors, 33 adjudicated warnings, 16 informational findings, zero broken links and zero suppressed findings | the exact minimal IG completed the recorded publisher pathway with zero errors |
| HL7 FHIR Validator | Four positive units passed without fatal/error findings; two negative units were rejected for their registered failure families | four positive units and two intended negative rejections under the recorded validator pathway |
| IHE certification | Not performed and not claimed | no certification wording |
| Operational interoperability | Not evaluated | no production, deployment or cross-enterprise namespace-resolution claim |

## Recorded environment

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

The official JAR SHA-256 values, complete tool versions, positive and negative OperationOutcomes, SUSHI log, IG Publisher log, QA files and compact package are retained in `standards/fhir_ig/validation/`.

## Public claim boundary

Allowed:

> The exact Route C hero-case resources completed the declared SUSHI, IG Publisher and HL7 FHIR Validator pathway against FHIR R4 4.0.1, the local 0.1.0 IG package and the applicable IHE BALP 1.1.4 profiles. Four positive units contained no fatal or error findings, and two negative units were rejected for their intended constraints.

Not allowed:

- FHIR compliant without exact corpus and profile qualification;
- universally BALP conformant;
- HL7 or IHE certified;
- production-ready standards implementation;
- clinical interoperability proven;
- operational namespace governance established.
