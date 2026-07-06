#!/usr/bin/env bash
set -euo pipefail
mkdir -p vendor
TRILLIAN_REF="${TRILLIAN_REF:-v1.7.3}"
REKOR_REF="${REKOR_REF:-main}"
FABRIC_SAMPLES_REF="${FABRIC_SAMPLES_REF:-main}"
clone_or_update() {
  local url="$1" dest="$2" ref="$3"
  if [ ! -d "$dest/.git" ]; then
    git clone --depth 1 --branch "$ref" "$url" "$dest"
  else
    git -C "$dest" fetch --depth 1 origin "$ref"
    git -C "$dest" checkout FETCH_HEAD
  fi
}
clone_or_update https://github.com/google/trillian.git vendor/trillian "$TRILLIAN_REF"
clone_or_update https://github.com/sigstore/rekor.git vendor/rekor "$REKOR_REF"
clone_or_update https://github.com/hyperledger/fabric-samples.git vendor/fabric-samples "$FABRIC_SAMPLES_REF"
echo "vendor_baselines: TRILLIAN_REF=$TRILLIAN_REF REKOR_REF=$REKOR_REF FABRIC_SAMPLES_REF=$FABRIC_SAMPLES_REF"
