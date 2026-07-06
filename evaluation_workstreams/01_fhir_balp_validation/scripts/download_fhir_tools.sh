#!/usr/bin/env bash
set -u -o pipefail
mkdir -p tools validation_logs
LOG=validation_logs/tool_download_attempt.log
{
  echo "Download start UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "This kit does not bundle publisher.jar or validator_cli.jar. The commands below use official latest-release endpoints."
  echo "Attempting IG Publisher download."
  curl -L --connect-timeout 10 --max-time 30 --retry 1 -o tools/publisher.jar https://github.com/HL7/fhir-ig-publisher/releases/latest/download/publisher.jar
  echo "publisher_exit=$?"
  ls -lh tools/publisher.jar 2>/dev/null || true
  sha256sum tools/publisher.jar 2>/dev/null || true
  echo "Attempting HL7 FHIR Validator CLI download."
  curl -L --connect-timeout 10 --max-time 30 --retry 1 -o tools/validator_cli.jar https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar
  echo "validator_exit=$?"
  ls -lh tools/validator_cli.jar 2>/dev/null || true
  sha256sum tools/validator_cli.jar 2>/dev/null || true
  echo "Download end UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$LOG" 2>&1
