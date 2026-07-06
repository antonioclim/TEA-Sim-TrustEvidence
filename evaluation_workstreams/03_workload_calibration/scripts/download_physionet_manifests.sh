
#!/usr/bin/env bash
set -euo pipefail
mkdir -p data_external/big_ideas data_external/mimic_fhir_demo
printf '%s\n' 'wget -r -N -c -np https://physionet.org/files/big-ideas-glycemic-wearable/1.1.3/ -P data_external/big_ideas' > data_external/BIG_IDEAS_DOWNLOAD_COMMAND.txt
printf '%s\n' 'wget -r -N -c -np https://physionet.org/files/mimic-iv-fhir-demo/2.1.0/ -P data_external/mimic_fhir_demo' > data_external/MIMIC_FHIR_DEMO_DOWNLOAD_COMMAND.txt
