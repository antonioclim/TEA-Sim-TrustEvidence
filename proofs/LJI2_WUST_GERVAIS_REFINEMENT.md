# Property note: LJI 2.0 as a domain refinement of Wüst–Gervais

## Claim v2.0.0

LJI 2.0 refines, rather than replaces, the Wüst–Gervais blockchain decision procedure for the narrower evidence-storage problem in auditable health information exchange (Wüst and Gervais decision framework).

## Refinement relation

Let `WG(x)` be the high-level Wüst–Gervais decision procedure over an application `x`. Let `LJI2(s)` be the TrustEvidence decision procedure over a health-audit scenario `s`, after the v2.0.0 screens and parametric value function. LJI 2.0 is a refinement if it satisfies both conditions below under the v2.0.0 protocol assumptions:

1. Agreement on rejection: where the Wüst–Gervais logic rejects blockchain because persistence, multi-party distrust or absence of a trusted intermediary is not present, LJI 2.0 must not recommend `BE-A3`.
2. Finer discrimination on admissible cases: where the Wüst–Gervais logic leaves a permissioned blockchain/ledger-like architecture admissible, LJI 2.0 may still choose `BE-A2`, `BE-A3`, or `NO-DECISION` by evaluating evidence-specific properties, legal traceability, metadata minimisation and backend burdens.

## Case argument

Case A — no persistent evidence need. LJI 2.0 returns out-of-scope or `NO-DECISION`, because the TrustEvidence decision object is persistent audit evidence. This agrees with Wüst–Gervais rejection of blockchain where persistence is unnecessary (Wüst and Gervais decision framework).

Case B — trusted central audit maintainer. Screen `G-1` blocks `BE-A3` and compares `BE-A1` with `BE-A2`. This agrees with the Wüst–Gervais central-database direction where a trusted party is sufficient (Wüst and Gervais decision framework). The refinement is that LJI 2.0 can still select a hash log for tamper-evidence without claiming ledger necessity.

Case C — multiple organisations but no split-view or independent-dispute requirement. Wüst–Gervais treats multi-party structure as relevant; LJI 2.0 refuses to treat it as sufficient. The refinement is stricter: organisational multiplicity raises demand signals, but does not pass the non-equivocation screen by itself under the v2.0.0 protocol assumptions.

Case D — no trusted maintainer and an external verifier must detect inconsistent histories. LJI 2.0 blocks unaided `BE-A1`, allows `BE-A2` only with `A7`, and allows `BE-A3` only with `A8`. This preserves the Wüst–Gervais intuition that distrust and absence of a trusted intermediary can motivate ledger-like systems, while adding the v2.0.0 property distinctions under the v2.0.0 protocol assumptions.

Case E — ledger burden violates metadata minimisation or operational feasibility. LJI 2.0 may reject `BE-A3` even when the high-level blockchain decision procedure leaves it admissible. This is a refinement, not contradiction, because it applies health-audit-specific proportionality and metadata constraints that are outside the coarser procedure under the v2.0.0 protocol assumptions.

## Result

The refinement is conservative: LJI 2.0 never uses Wüst–Gervais as a rhetorical citation for ledger adoption. It uses the procedure as a dominance constraint against unjustified ledger use and as a coarse eligibility ancestor that is specialised by TrustEvidence properties, v2.0.0 legal traceability and v2.0.0 measured burdens.
