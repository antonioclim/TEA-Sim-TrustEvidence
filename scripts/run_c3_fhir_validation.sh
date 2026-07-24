#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${1:-ephemeral}"
if [[ "$MODE" == "retain" ]]; then
  VALIDATION_DIR="$ROOT/standards/fhir_ig/validation"
else
  VALIDATION_DIR="${RUNNER_TEMP:-/tmp}/route-c-c3-validation"
fi
TOOLS_DIR="${RUNNER_TEMP:-/tmp}/route-c-fhir-tools"
TX_SERVER="${FHIR_TX_SERVER:-https://tx.fhir.org/r4}"
mkdir -p "$VALIDATION_DIR/positive" "$VALIDATION_DIR/negative" "$TOOLS_DIR"
rm -f "$VALIDATION_DIR"/positive/*.json "$VALIDATION_DIR"/negative/*.json
rm -rf standards/fhir_ig/output standards/fhir_ig/temp standards/fhir_ig/fsh-generated

python experiments/run_hie_hero_case.py --write
python scripts/check_hie_fhir_projection.py --output "$VALIDATION_DIR/semantic_validation.json"

sushi standards/fhir_ig 2>&1 | tee "$VALIDATION_DIR/sushi.log"

PUBLISHER_JAR="$TOOLS_DIR/publisher.jar"
VALIDATOR_JAR="$TOOLS_DIR/validator_cli.jar"
PUBLISHER_URL="https://github.com/HL7/fhir-ig-publisher/releases/latest/download/publisher.jar"
VALIDATOR_URL="https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar"
if [[ ! -s "$PUBLISHER_JAR" ]]; then
  echo "Downloading IG Publisher from $PUBLISHER_URL"
  curl --fail-with-body --location --retry 4 --retry-all-errors --output "$PUBLISHER_JAR" "$PUBLISHER_URL"
fi
if [[ ! -s "$VALIDATOR_JAR" ]]; then
  echo "Downloading FHIR Validator from $VALIDATOR_URL"
  curl --fail-with-body --location --retry 4 --retry-all-errors --output "$VALIDATOR_JAR" "$VALIDATOR_URL"
fi
sha256sum "$PUBLISHER_JAR" "$VALIDATOR_JAR" > "$VALIDATION_DIR/tool_sha256.txt"
{
  echo "python=$(python --version 2>&1)"
  echo "java=$(java -version 2>&1 | head -n 1)"
  echo "node=$(node --version)"
  echo "ruby=$(ruby --version)"
  echo "jekyll=$(jekyll --version)"
  echo "sushi=$(sushi --version 2>&1 | tail -n 1)"
  echo "terminology_server=$TX_SERVER"
  echo "publisher_sha256=$(sha256sum "$PUBLISHER_JAR" | cut -d' ' -f1)"
  echo "validator=$(java -jar "$VALIDATOR_JAR" -version 2>&1 | head -n 1 || true)"
} > "$VALIDATION_DIR/tool_versions.txt"

java -jar "$PUBLISHER_JAR" -ig standards/fhir_ig/ig.ini -tx "$TX_SERVER" \
  2>&1 | tee "$VALIDATION_DIR/ig-publisher.log"

test -f standards/fhir_ig/output/qa.json
python scripts/check_ig_publisher_qa.py \
  --qa standards/fhir_ig/output/qa.json \
  --log "$VALIDATION_DIR/ig-publisher.log" \
  --output "$VALIDATION_DIR/ig_publisher_summary.json"

PACKAGE="$ROOT/standards/fhir_ig/output/package.tgz"
test -f "$PACKAGE"
: > "$VALIDATION_DIR/validator_status.tsv"

validate_one() {
  local kind="$1"
  local source="$2"
  local stem
  stem="$(basename "$source" .json)"
  local output="$VALIDATION_DIR/${kind}/${stem}.operationoutcome.json"
  set +e
  java -jar "$VALIDATOR_JAR" "$source" \
    -version 4.0.1 -ig "$PACKAGE" -ig ihe.iti.balp#1.1.4 \
    -tx "$TX_SERVER" -output "$output"
  local status=$?
  set -e
  printf '%s\t%s\t%s\n' "$kind" "$status" "$source" >> "$VALIDATION_DIR/validator_status.tsv"
}

POSITIVE_FILES=(
  standards/fhir_ig/input/resources/Bundle-portable-evidence-bundle-hie-001.json
  data_examples/hie_disclosure/source/source_clinical_bundle.json
  standards/fhir_ig/input/resources/AuditEvent-authorisation-decision-hie-001.json
  standards/fhir_ig/input/resources/AuditEvent-privacy-disclosure-source-hie-001.json
)
for source in "${POSITIVE_FILES[@]}"; do
  validate_one positive "$source"
done
for source in standards/fhir_ig/negative/*.json; do
  validate_one negative "$source"
done

python scripts/summarise_fhir_validation.py \
  --positive-dir "$VALIDATION_DIR/positive" \
  --negative-dir "$VALIDATION_DIR/negative" \
  --output "$VALIDATION_DIR/validator_summary.json"

echo "C3-FHIR: PASS"
