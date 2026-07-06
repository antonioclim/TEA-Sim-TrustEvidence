# SUSHI / IG Publisher / HL7 FHIR Validator log summary

Run timestamp: 2026-07-05T16:30:37Z

## Tool availability

```text
RUN UTC: 2026-07-05T16:28:16Z
node: v22.16.0
npm: 10.9.2
java: openjdk version "21.0.10" 2026-01-20
sushi: SUSHI v3.20.0 (implements FHIR Shorthand specification v3.0.0)
```

## Official validation pathway status

| Component | Status | Evidence file | Interpretation |
|---|---|---|---|
| SUSHI | PASS_WITH_WARNINGS | `validation_logs/sushi.log` | SUSHI compiled the draft IG resources. The log reports 3 warning(s) and no SUSHI error. SUSHI compilation is not full FHIR/BALP validation. |
| FHIR R4 core package | LOADED | `validation_logs/sushi.log` | The SUSHI log loaded `hl7.fhir.r4.core#4.0.1`. |
| IHE BALP package | LOADED | `validation_logs/sushi.log` | The SUSHI log loaded `ihe.iti.balp#1.1.4`. |
| IG Publisher | SKIPPED_JAR_ABSENT | `validation_logs/ig_publisher.log` | `tools/publisher.jar` was absent after the download attempt; IG Publisher did not run. |
| HL7 FHIR Validator CLI | SKIPPED_JAR_ABSENT | `validation_logs/fhir_validator.log` | `tools/validator_cli.jar` was absent after the download attempt; validator did not run. |
| Local JSON/resource-family lint | PASS | `validation_logs/local_json_integrity_lint.csv` | Supplementary structural smoke check only; not official FHIR/BALP validation. |

## SUSHI log tail

```text
warn  Failed to load automatically-provided hl7.fhir.uv.tools.r4#latest
warn  Failed to load automatically-provided hl7.terminology.r4#latest
info  Loaded ihe.iti.balp#1.1.4 with 38 resources
info  Loaded hl7.fhir.r4.core#4.0.1 with 11351 resources
warn  Failed to load automatically-provided hl7.fhir.uv.extensions.r4#latest
info  Loaded virtual package sushi-local#LOCAL with 12 resources
info  Converting FSH to FHIR resources...
info  Converted 8 FHIR StructureDefinitions.
info  Converted 1 FHIR CodeSystems.
info  Converted 1 FHIR ValueSets.
info  Converted 1 FHIR instances.
info  Exporting FHIR resources as JSON...
info  Exported 11 FHIR resources as JSON.
info  Assembling Implementation Guide sources...
info  Generated ImplementationGuide-te.trustevidence.json
info  Assembled Implementation Guide sources; ready for IG Publisher.
info  The _build script hosted at https://github.com/HL7/ig-publisher-scripts is useful for downloading and running the IG Publisher.

========================= SUSHI RESULTS ===========================
|  -------------------------------------------------------------  |
| |    Profiles   |  Extensions  |   Logicals   |   Resources   | |
| |-------------------------------------------------------------| |
| |       4       |      4       |      0       |       0       | |
|  -------------------------------------------------------------  |
|  -------------------------------------------------------------  |
| |      ValueSets     |    CodeSystems    |     Instances      | |
| |-------------------------------------------------------------| |
| |         1          |         1         |         1          | |
|  -------------------------------------------------------------  |
|                                                                 |
===================================================================
| Keep swimming, Dory.                   0 Errors      3 Warnings |
===================================================================

```

## Validation decision

The FHIR/BALP artefact workstream evidence-supported acceptance criterion was **not fully met**. SUSHI compilation succeeded and loaded the FHIR R4 core and BALP packages, and twelve synthetic examples passed local structural lint. However, the IG Publisher and HL7 FHIR Validator stages were not executed. The evidence therefore supports only a demoted statement: draft FHIR R4/BALP-facing artefacts compiled by SUSHI with local structural smoke checks; full IG Publisher and HL7 FHIR Validator validation remains pending.
