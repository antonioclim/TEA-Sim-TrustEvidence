# Property-based and bounded executable results

## Run identity

| Item | Value |
|---|---|
| Property run | `cmpb-property-checks-001` |
| Bounded run | `cmpb-bounded-checks-001` |
| Mutation regression | `cmpb-mutation-consistency-001` |
| Software | `teasim-trustevidence 2.1.0` |
| Python | 3.13.5 |
| pytest | 9.1.1 |
| Hypothesis | 6.156.6 |
| RFC 8785 package | 0.1.4 |

Hypothesis used `database=None`, `derandomize=True`, and no deadline. This makes the generated sequence reproducible for the pinned Hypothesis version while retaining shrinking and generated-example exploration.

## Hypothesis results

Eight property tests passed. The test output reported 680 passing generated examples and no failing example.

| Property | Test focus | Reported passing examples | Result |
|---|---|---:|---|
| P1 | Append monotonicity and prefix-root recall | 80 | Pass |
| P2 | Inclusion soundness and changed path/root/index rejection | 80 | Pass |
| P4 | Canonical bytes under recursive key reordering | 100 | Pass |
| P5 | Receipt binding under re-signed coherent-looking mutations | 80 | Pass |
| P6 | Payload commitment and evidence-only verification without payload/nonce | 100 | Pass |
| P7 | Same-size verifier-visible root divergence | 80 | Pass |
| P8a | Consistency-path soundness and mutation rejection | 80 | Pass |
| P8b | Retained-checkpoint extension with mandatory consistency proof | 80 | Pass |

The generated examples are finite test evidence. They are not a proof over every JSON object, key state, tree size, or adversarial strategy.

## Bounded exploration

The finite model enumerated a three-symbol input domain over all ordered histories of length zero through five.

| Metric | Executed value |
|---|---:|
| Histories enumerated | 364 |
| Append transitions | 1,641 |
| Inclusion proofs | 1,641 |
| Consistency proofs | 1,278 |
| Admissible finite JSON objects | 729 |
| Verifier-level checkpoint advances | 16 |
| Same-size divergent-history pairs | 4,059 |
| Total checks | 29,105 |
| Failures | 0 |

The model cross-checked recursive Merkle roots against an independently coded stack calculation. It exercised valid inclusion and consistency paths, changed roots, changed indices for position-distinguished leaves, missing/short/long/changed consistency paths, equal-size root comparison, re-signed receipt-root mutation, and public-field minimisation.

## Larger-checkpoint consistency

The consistency implementation closes the prior local limitation in which any valid larger receipt was accepted against a retained smaller checkpoint without proving prefix extension.

The verifier now requires a `TE-A2-Consistency-1` object whenever `current_tree_size > retained_tree_size`. The object binds:

- backend and log identifiers;
- retained and current sizes;
- retained and current roots;
- the ordered consistency hash path.

The updated deterministic mutation matrix contains 57 passing rows. Five consistency controls establish that:

1. no proof is rejected with `TE-E-CONSISTENCY-MISSING`;
2. a valid proof is accepted;
3. a one-bit path mutation is rejected with `TE-E-CONSISTENCY-PATH`;
4. a declared earlier-root mismatch is rejected with `TE-E-CONSISTENCY-ROOT`;
5. a declared earlier-size mismatch is rejected with `TE-E-CONSISTENCY-SIZE`.

These checks establish local extension between one retained signed state and one current signed state. They do not establish that isolated verifiers received the same states.

## Duplicate-leaf observation

The first Hypothesis design assumed that changing a leaf index must always invalidate an inclusion proof. Hypothesis reduced the counterexample to two identical leaves. In that symmetric case, the same leaf hash and sibling hash can verify at either position.

The final tests therefore distinguish two questions:

- **index binding for position-distinguished leaf inputs**, which passed;
- **occurrence uniqueness for identical leaf material**, which is not established by inclusion alone.

The receipt signature still binds the declared index, but the current local log does not reject duplicate core digests. Public wording must not claim that a Merkle inclusion proof demonstrates that identical evidence material occurs only once.

## Claim boundary

The executed evidence supports:

- property-based tests over generated examples;
- finite bounded executable checks;
- local inclusion and consistency-path verification;
- retained-state rollback and same-size-root comparison;
- evidence-only verification without raw monitoring payload or nonce.

It does not support:

- formal proof or theorem;
- global non-equivocation;
- split-view detection without checkpoint exchange;
- witness cosigning or gossip;
- security after compromise of an authorised signing key;
- operational key lifecycle adequacy;
- production performance or scalability;
- clinical validation, clinical utility, or legal compliance.

## Falsifiers

The reported property result would be falsified within its declared scope by any reproducible case in which:

- a valid generated inclusion or consistency path is rejected;
- an altered path reconstructs the declared roots;
- a larger checkpoint is accepted without a proof when retained state is supplied;
- a non-prefix larger history is accepted as an extension of the retained root;
- key reordering changes TE-JCS-1 bytes for an admitted object;
- a re-signed receipt with a changed bound root is accepted;
- evidence-only verification requires disclosure of the payload or nonce;
- a bounded-model counterexample appears within the enumerated domain.

## Verified normative references

| Reference | DOI |
|---|---|
| Laurie, B., Messeri, E., & Stradling, R. (2021). *Certificate Transparency Version 2.0* (RFC 9162). RFC Editor. | https://doi.org/10.17487/RFC9162 |
| Rundgren, A., Jordan, B., & Erdtman, S. (2020). *JSON Canonicalization Scheme (JCS)* (RFC 8785). RFC Editor. | https://doi.org/10.17487/RFC8785 |
| Josefsson, S., & Liusvaara, I. (2017). *Edwards-Curve Digital Signature Algorithm (EdDSA)* (RFC 8032). RFC Editor. | https://doi.org/10.17487/RFC8032 |
