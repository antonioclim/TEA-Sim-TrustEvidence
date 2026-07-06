
#!/usr/bin/env bash
set -euo pipefail
PATIENTS="${1:-1000}"
SEED="${2:-12345}"
cd external/synthea
./run_synthea -p "$PATIENTS" -s "$SEED" --exporter.fhir.export=true --exporter.fhir.bulk_data=false
