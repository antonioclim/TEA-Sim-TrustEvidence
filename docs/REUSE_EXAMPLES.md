# Reuse examples

These examples use the public v2.2.0 reference package. They demonstrate software reuse, not clinical or production validation.

## 1. Reproduce the cross-organisational HIE case

After installing the locked Python 3.13 environment, verify the retained disclosure artefacts:

```bash
python experiments/run_hie_hero_case.py --check
python scripts/check_c3_retained_evidence.py
```

This route checks the declared synthetic DiagnosticReport disclosure, the portable evidence boundary and the retained validation evidence. It does not contact an operational FHIR server.

## 2. Reuse the adversarial corpus

Execute the registered HIE mutation programme:

```bash
python experiments/run_hie_security_mutations.py --check
```

The retained corpus can be reused to compare verifier behaviour across independent implementations. A reuse report should preserve each case identifier, expected decision and intended verification layer. Expected limitation acceptances must not be recoded as successful tamper detection.

## 3. Reproduce the paired local processing experiment

Check the retained B0-B2 corpus and its registered derivations:

```bash
python experiments/run_hie_incremental_overhead.py --check
```

The result is a local reference-pipeline increment for the frozen synthetic W1 case. It is not production-EHR latency, network traffic, database storage or a service-level result.

## 4. Build and verify a candidate archive

```bash
mkdir -p dist
python scripts/audit_public_distribution.py --report dist/public-distribution-audit.json
python scripts/build_release_archives.py --output-dir dist
python scripts/check_release_archive.py \
  --archive dist/TEA-Sim-TrustEvidence-v2.2.0.zip \
  --checksum dist/TEA-Sim-TrustEvidence-v2.2.0.sha256 \
  --extract-dir dist/fresh-extraction \
  --report dist/release-archive-audit.json
```

This route is useful for reproducibility teaching, archival verification and independent package review.

## 5. Develop an independent verifier

Use the JSON schemas, canonical test vectors, signed envelopes, mutation cases and retained checkpoint examples to implement a verifier in another language. Do not reuse the Python verification functions in an implementation claimed to be independent.

The independent implementation should return:

- structural and semantic decision;
- calculated canonical digest;
- issuer-signature decision;
- payload-commitment decision;
- receipt and inclusion decision;
- retained-checkpoint decision;
- failed verification layer.

See `docs/INDEPENDENT_REPRODUCTION_PROTOCOL.md` for the reporting requirements.
