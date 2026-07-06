# Data licence and access report

Verification date: 2026-07-05.

## Synthea

Synthea was treated as a generator pathway rather than a bundled dataset. The official repository states that it is a synthetic patient population simulator and lists FHIR R4 among its output formats. The software repository presents an Apache-2.0 licence. The workload-calibration workstream runtime could not clone or execute Synthea because direct shell DNS/network access was unavailable. The kit therefore supplies maintainer-run scripts and does not claim Synthea-generated workload extraction.

## BIG IDEAs PhysioNet glycaemic/wearable dataset

The verified public source was BIG IDEAs Lab Glycemic Variability and Wearable Device Data v1.1.3 on PhysioNet, DOI 10.13026/aw6y-fc44. The page reports open file access subject to the Open Data Commons Attribution License v1.0, 16 study participants, 8-10 monitoring days, Dexcom G6 interstitial glucose sampling every 5 minutes and seven wearable/CGM feature files. The page also reports 34.1 GB uncompressed and a 4.7 GB ZIP. These size constraints and the runtime network limitation prevented full in-session extraction. The kit does not redistribute the dataset.

## MIMIC-IV Clinical Database Demo on FHIR

The verified public source was MIMIC-IV Clinical Database Demo on FHIR v2.1.0 on PhysioNet. The page reports open access under the Open Data Commons Open Database License v1.0, a 100-patient subset, compressed NDJSON grouped by FHIR resource type and a 49.5 MB uncompressed size. The full MIMIC-IV on FHIR project, in contrast, requires credentialing, a data-use agreement and CITI training; it is therefore not bundled or treated as available evidence.

## Redistribution boundary

This kit contains no full external patient-level datasets. It includes only source metadata, scripts, toy parser samples and deterministic synthetic TrustEvidence objects/benchmark outputs. Manuscript wording must distinguish metadata-informed workload descriptors from executed external-data extraction.
