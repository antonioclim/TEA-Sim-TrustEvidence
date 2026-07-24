#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FHIR="$ROOT/standards/fhir_ig"
VALIDATION="$FHIR/validation"
OUTPUT="$FHIR/output"

mkdir -p "$VALIDATION"
test -f "$OUTPUT/qa.json"
test -f "$OUTPUT/qa.txt"
test -f "$OUTPUT/package.tgz"
test -f "$OUTPUT/package.manifest.json"

cp "$OUTPUT/qa.json" "$VALIDATION/ig-publisher-qa.json"
cp "$OUTPUT/qa.txt" "$VALIDATION/ig-publisher-qa.txt"
cp "$OUTPUT/package.tgz" "$VALIDATION/org.trustevidence.hie-0.1.0.tgz"
cp "$OUTPUT/package.manifest.json" "$VALIDATION/ig-package-manifest.json"

# The rendered IG site, temporary Jekyll tree, downloaded publisher template
# and terminology cache are build products rather than review evidence. Retain
# only the compact package, generated conformance resources, logs, summaries
# and OperationOutcomes required by the offline C3 evidence checker.
rm -rf \
  "$FHIR/output" \
  "$FHIR/temp" \
  "$FHIR/input-cache" \
  "$FHIR/template"

python "$ROOT/experiments/run_hie_hero_case.py" --check
python "$ROOT/scripts/check_c3_retained_evidence.py"

echo "C3-RETAINED-PREP: PASS"
