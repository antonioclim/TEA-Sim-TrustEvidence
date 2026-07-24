# C4 protocol deviation: authorised tree-size assertion

## Status

This document records a falsified preregistered expectation from the first hosted C4 execution. The failed result is retained as evidence; it is not relabelled as a successful rejection.

## Initial expectation

Case `RSIG-005` changed both:

```text
backend_receipt.tree_size
backend_receipt.inclusion_proof.tree_size
```

from six to seven, recomputed the proof digest and re-signed the receipt with the deterministic authorised backend test key. The preregistered expectation was rejection with `TE-E-PROOF-PATH`.

## First hosted observation

```text
workflow run: 30005609826
job: 89200751523
artifact: route-c-c4-security-materialisation
artifact digest: sha256:7e4835bac2606f52dc9e62131aab682c91fe2b65eab1fe4eed4d07d4e53d4799
case count: 67
passed: 66
failed: 1
false accepts under the original registry: 1
failed case: RSIG-005
observed outcome: accepted
```

The materialisation job failed and did not commit the result files.

## Technical interpretation

The inclusion verifier binds the leaf to the supplied root under the supplied index, path and claimed tree size. It cannot independently establish how many leaves the authorised backend actually used to produce that root. For the supplied left-side path, the same opaque sibling hashes can be interpreted under the alternative claimed size; after the backend re-signs the coherent receipt, no independent log-population evidence is available to the stateless verifier.

This is not evidence that an unauthorised party can alter the receipt: a stale signature or wrong key remains rejected. It is evidence that an authorised or compromised backend can make a false but internally admissible tree-size assertion. A receipt signature authenticates the backend statement; it does not prove operational honesty, event completeness or the actual population of the log.

Retained prior state can detect rollback and same-size divergent roots, and a valid consistency proof is required before local advancement. It still does not transform an authorised backend signature into proof of truthful event capture.

## Protocol amendment

The case is renamed:

```text
LIM-BACKEND-002 — validly signed alternative tree-size assertion
```

and is now preregistered as an **expected limitation acceptance**, not an expected rejection. The total case count remains 67. The expected-rejection count decreases by one, the expected-acceptance count increases by one and the limitation-acceptance count increases by one.

This amendment was made after observing the first result and before the retained final C4 corpus was materialised. The original failed artifact and digest above preserve the sequence of evidence.

## Consequent claim narrowing

C4 may claim that unauthorised receipt changes, malformed paths, identity substitutions, rollback, verifier-visible forks and invalid consistency proofs are rejected under the declared configuration. It may not claim that:

- a valid receipt proves the truthful tree size;
- a valid receipt proves event completeness;
- the backend remained honest after key compromise;
- inclusion proves all relevant events were logged;
- a stateless verifier detects split views;
- the local design provides public transparency or global non-equivocation.
