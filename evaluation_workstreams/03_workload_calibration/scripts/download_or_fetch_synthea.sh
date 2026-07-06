
#!/usr/bin/env bash
set -euo pipefail
mkdir -p external
if [ ! -d external/synthea ]; then
  git clone --depth 1 https://github.com/synthetichealth/synthea.git external/synthea
fi
