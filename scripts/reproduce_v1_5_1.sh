#!/usr/bin/env bash
set -euo pipefail
OUT_DIR="${1:-outputs/v1_5_1_reproduction}"
python -m teasim reproduce-v1 --output-dir "$OUT_DIR"
