#!/usr/bin/env bash
set -euo pipefail
if [ ! -d vendor/trillian ]; then
  echo "vendor/trillian missing; run make vendor-baselines first" >&2
  exit 2
fi
mkdir -p src/trustevidence/trillian_generated
python -m grpc_tools.protoc \
  -I vendor/trillian \
  --python_out=src/trustevidence/trillian_generated \
  --grpc_python_out=src/trustevidence/trillian_generated \
  vendor/trillian/trillian_log_api.proto vendor/trillian/trillian.proto
# The generated files are intentionally not committed in external-service integration;  CI should pin and regenerate them.
