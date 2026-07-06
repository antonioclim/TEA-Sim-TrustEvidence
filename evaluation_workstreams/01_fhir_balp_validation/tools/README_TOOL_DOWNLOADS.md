# External validation binaries

The FHIR/BALP artefact workstream clean kit does not bundle `publisher.jar` or `validator_cli.jar`. Use `scripts/download_fhir_tools.sh` to fetch them from the official release endpoints, then re-run `scripts/run_validation.sh`.

The FHIR/BALP artefact workstream execution environment could not resolve the GitHub download host, so these binaries were not available and the IG Publisher/HL7 FHIR Validator steps were skipped. This is preserved in `validation_logs/tool_download_attempt.log`, `validation_logs/ig_publisher.log` and `validation_logs/fhir_validator.log`.
