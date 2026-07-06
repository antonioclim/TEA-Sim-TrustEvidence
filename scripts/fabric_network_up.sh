#!/usr/bin/env bash
set -euo pipefail
if [ ! -d vendor/fabric-samples/test-network ]; then
  echo "vendor/fabric-samples missing; run make vendor-baselines first" >&2
  exit 2
fi
pushd vendor/fabric-samples/test-network >/dev/null
./network.sh up createChannel -ca -c te-channel
./network.sh deployCC -c te-channel -ccn trustevidence -ccp ../../../chaincode/trustevidence_fabric -ccl go
popd >/dev/null
echo "Fabric test-network ready on channel te-channel with chaincode trustevidence"
