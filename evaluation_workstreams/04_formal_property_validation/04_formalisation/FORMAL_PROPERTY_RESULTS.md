# FORMAL_PROPERTY_RESULTS.md

created_utc: `2026-07-05T19:05:13Z`  
stage: formal/property validation workstream - Formal/property validation  
scope: A2 Merkle local reference backend only.

## Executed evidence

formal/property validation workstream executed property-based tests and a bounded executable model against the A2 Merkle reference backend. It did not test A1 PostgreSQL, A3 Rekor/Trillian/Fabric, FHIR/BALP artefacts, clinical deployment, legal compliance or production security.

## Receipt-verification correction

The formal/property validation workstream kit uses a stricter receipt-verification contract than the earlier backend evidence. Receipts include a zero-based `leaf_index`, `tree_size`, checkpoint `root_hash`, proof material with sibling ranges and a `receipt_digest` over the receipt material. Verification recomputes the evidence leaf, verifies the digest, checks the proof against the declared leaf index and tree size and may be supplied with an expected tree-size checkpoint. This is a local reference-implementation correction. `receipt_digest` is not a digital signature, notarisation or external witness.

## Hypothesis property tests

Command recorded in `hypothesis.log`: `python -m pytest -q 04_formalisation/hypothesis_tests/test_merkle_properties.py --hypothesis-show-statistics -p no:cacheprovider`.

Result: **PASS; 8/8 tests passed**, including the seven required property families plus a root-frontier/reference-root invariant. Each property family used 30 passing generated examples.

Required property families tested:

1. append monotonicity;
2. inclusion soundness;
3. tamper rejection;
4. canonicalisation determinism;
5. receipt self-consistency/path binding with checkpointed tree-size rejection;
6. prefix consistency by recomputation;
7. verifier-visible same-size fork/root comparison.

## Bounded executable model

The bounded model enumerated domain `(0, 1, 2)` up to sequence length `4`.

| Counter | Value |
|---|---:|
| sequences_checked | 121 |
| inclusion_receipts_checked | 426 |
| tamper_rejections_checked | 852 |
| prefix_roots_checked | 547 |
| fork_pairs_checked | 10 |
| failures | 0 |

Result: **PASS; zero failures**.

## TLA+ and Alloy status

TLA+ and Alloy specification files are included as formal scaffolding. TLC and Alloy were not available in the runtime, so no TLC model-checking or Alloy-checking result is claimed.

## Allowable public wording

The local A2 Merkle reference implementation is accompanied by property-based tests and bounded executable checks for append-only, inclusion-verification, tamper-rejection, deterministic canonicalisation, receipt self-consistency/path-binding, checkpointed tree-size rejection, prefix-consistency and verifier-visible same-size root-comparison assumptions under stated local-reference conditions.

## Forbidden public wording

Do not claim formal verification, cryptographic proof, guaranteed non-equivocation, production security, FHIR/BALP conformance, legal compliance, clinical validation or externally witnessed integrity.
