# FHIR/BALP validation kit — FHIR/BALP artefact workstream controlled artefact

This directory contains the FHIR/BALP artefact workstream TrustEvidence FHIR R4/BALP-facing validation artefacts: FHIR Shorthand profiles/extensions, a minimal IG skeleton, twelve JSON examples, validation scripts and preserved logs.

## Claim boundary

The current FHIR/BALP artefact workstream run compiled the draft IG with SUSHI and loaded the local FHIR R4 core and IHE BALP packages, but it did **not** complete IG Publisher or HL7 FHIR Validator execution because `publisher.jar` and `validator_cli.jar` were unavailable in the runtime. Therefore this kit supports only a demoted claim: *draft FHIR R4/BALP-facing artefacts compiled by SUSHI with local structural smoke checks; IG Publisher and HL7 FHIR Validator validation pending*.

Forbidden wording: *FHIR compliant*, *BALP conformant*, *IHE certified*, *HL7 validated*, *production-ready*, *clinical validation* or equivalent conformance/certification wording.

## Re-run commands

```bash
bash scripts/download_fhir_tools.sh
bash scripts/run_validation.sh
python scripts/local_json_integrity_lint.py
python scripts/summarise_validation_logs.py
```

A full pass requires `SUSHI_EXIT=0`, `IG_PUBLISHER_EXIT=0` and `FHIR_VALIDATOR_EXIT=0`.
