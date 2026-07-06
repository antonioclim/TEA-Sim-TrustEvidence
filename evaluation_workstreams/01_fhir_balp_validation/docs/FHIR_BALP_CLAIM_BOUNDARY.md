# FHIR/BALP claim boundary after FHIR/BALP artefact workstream

## Allowed internal evidence statement

The FHIR/BALP artefact workstream artefact set contains draft FHIR R4/BALP-facing profiles, extensions, a minimal IG skeleton, a field-to-FHIR mapping table and twelve JSON examples. SUSHI compiled the draft IG resources and loaded local `hl7.fhir.r4.core#4.0.1` and `ihe.iti.balp#1.1.4` package resources. The examples also passed local structural linting.

## Disallowed public claim

The package **must not** claim FHIR/BALP validation, BALP conformance, HL7/IHE certification or production readiness. IG Publisher and the HL7 FHIR Validator CLI did not run because `publisher.jar` and `validator_cli.jar` were absent and could not be downloaded in the runtime.

## Public wording permitted for later manuscript drafts

> We prepared draft FHIR R4/BALP-facing artefacts and compiled the draft IG with SUSHI under the declared runtime. The examples passed local structural checks, but IG Publisher QA and HL7 FHIR Validator validation remain pending and are not claimed.

## Public wording forbidden unless a later maintainer run supplies successful logs

- FHIR compliant
- BALP conformant
- IHE certified
- HL7 validated
- validated FHIR/BALP examples
- production-ready FHIR/BALP implementation
- clinical validation
- legal compliance or certification

## Remediation required before a evidence-supported FHIR/BALP claim

Place verified `publisher.jar` and `validator_cli.jar` in `tools/`, ensure access to `hl7.fhir.r4.core#4.0.1` and `ihe.iti.balp#1.1.4`, then re-run:

```bash
bash scripts/run_validation.sh
python scripts/summarise_validation_logs.py
```

Only after zero SUSHI errors, completed IG Publisher output and successful HL7 FHIR Validator execution may the claim be upgraded.
