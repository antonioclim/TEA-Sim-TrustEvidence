#!/usr/bin/env bash
set -u -o pipefail
mkdir -p validation_logs tools ig/fsh-generated
{
  echo "RUN UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "node: $(node --version 2>/dev/null || echo missing)"
  echo "npm: $(npm --version 2>/dev/null || echo missing)"
  echo "java: $(java -version 2>&1 | head -1 || echo missing)"
  echo "sushi: $(sushi --version 2>/dev/null || echo missing)"
} | tee validation_logs/tool_versions.log

if ! command -v sushi >/dev/null; then
  echo "FAILED: SUSHI executable is missing." | tee validation_logs/sushi.log
  SUSHI_STATUS=127
else
  sushi build --snapshot --log-level info --out ig/fsh-generated ig > validation_logs/sushi.log 2>&1
  SUSHI_STATUS=$?
fi
echo "SUSHI_EXIT=${SUSHI_STATUS}" | tee validation_logs/sushi_exit_status.log

if [ -f tools/publisher.jar ]; then
  (cd ig && java -Xmx4g -jar ../tools/publisher.jar -ig ig.ini) > validation_logs/ig_publisher.log 2>&1
  PUBLISHER_STATUS=$?
else
  echo "SKIPPED: tools/publisher.jar not present; IG Publisher was not executed." > validation_logs/ig_publisher.log
  PUBLISHER_STATUS=127
fi
echo "IG_PUBLISHER_EXIT=${PUBLISHER_STATUS}" | tee validation_logs/ig_publisher_exit_status.log

if [ -f tools/validator_cli.jar ]; then
  java -Xmx4g -jar tools/validator_cli.jar examples/*.json \
    -version 4.0.1 \
    -ig hl7.fhir.r4.core#4.0.1 \
    -ig ihe.iti.balp#1.1.4 \
    -ig ig/fsh-generated/fsh-generated/resources \
    -output-style compact > validation_logs/fhir_validator.log 2>&1
  VALIDATOR_STATUS=$?
else
  echo "SKIPPED: tools/validator_cli.jar not present; HL7 FHIR Validator was not executed." > validation_logs/fhir_validator.log
  VALIDATOR_STATUS=127
fi
echo "FHIR_VALIDATOR_EXIT=${VALIDATOR_STATUS}" | tee validation_logs/fhir_validator_exit_status.log

if [ "${SUSHI_STATUS}" -eq 0 ] && [ "${PUBLISHER_STATUS}" -eq 0 ] && [ "${VALIDATOR_STATUS}" -eq 0 ]; then
  echo "FHIR_BALP_WORKSTREAM_OFFICIAL_VALIDATION_STATUS=PASS" | tee validation_logs/official_validation_status.log
  exit 0
else
  echo "FHIR_BALP_WORKSTREAM_OFFICIAL_VALIDATION_STATUS=PARTIAL_OR_NOT_EXECUTED" | tee validation_logs/official_validation_status.log
  exit 1
fi
