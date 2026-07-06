#!/usr/bin/env bash
set -euo pipefail
if ! command -v node >/dev/null; then
  echo "Node.js is required. Install Node.js 22 LTS before running SUSHI." >&2
  exit 1
fi
npm install -g fsh-sushi
sushi --version | tee validation_logs/sushi_version.log
