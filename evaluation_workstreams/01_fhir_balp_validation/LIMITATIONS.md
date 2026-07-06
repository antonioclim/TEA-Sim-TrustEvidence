# FHIR/BALP artefact workstream limitations

1. The current kit is a research validation artefact, not a conformance package.
2. IG Publisher was not executed in the FHIR/BALP artefact workstream runtime because `publisher.jar` was absent and could not be downloaded.
3. HL7 FHIR Validator CLI was not executed in the FHIR/BALP artefact workstream runtime because `validator_cli.jar` was absent and could not be downloaded.
4. SUSHI compilation is useful but is not a substitute for IG Publisher QA or HL7 FHIR Validator example validation.
5. The examples are synthetic and do not contain clinical deployment evidence, patient intervention data or legal compliance evidence.
