# LJI 2.0 as a domain refinement of Wüst–Gervais

## Claim

LJI 2.0 refines, rather than replaces, the Wüst–Gervais blockchain decision procedure for the narrower evidence-storage problem in auditable health information exchange.

## Refinement relation

Let `WG(x)` be the high-level Wüst–Gervais decision procedure over an application `x`. Let `LJI2(s)` be the TrustEvidence decision procedure over a health-audit scenario `s` after screening and parametric comparison. LJI 2.0 is a refinement when it satisfies two conditions.

1. Agreement on rejection: where the Wüst–Gervais logic rejects blockchain because persistence, multi-party distrust or absence of a trusted intermediary is not present, LJI 2.0 does not recommend the ledger-like backend.
2. Finer discrimination on admissible cases: where the Wüst–Gervais logic leaves a permissioned blockchain or ledger-like architecture admissible, LJI 2.0 may still choose a hash log, a ledger-like backend or no decision by evaluating evidence-specific properties, traceability needs, metadata minimisation and backend burdens.

## Case argument

Case A — no persistent evidence need. LJI 2.0 returns out of scope or no decision because the TrustEvidence decision object is persistent audit evidence. This agrees with Wüst–Gervais rejection of blockchain where persistence is unnecessary.

Case B — trusted central audit operator. The single-authority screen blocks the ledger-like backend and compares central audit with append-only hash logging. This agrees with the Wüst–Gervais central-database branch where a trusted party is sufficient. The refinement is that LJI 2.0 can still select a hash log for tamper-evidence without claiming ledger necessity.

Case C — multiple organisations but no split-view or independent-dispute requirement. LJI 2.0 refuses to treat organisational multiplicity as sufficient. The refinement is stricter: multiplicity raises demand signals but does not pass the non-equivocation screen by itself.

Case D — no trusted log operator and an external verifier must detect inconsistent histories. LJI 2.0 blocks unaided central audit, allows append-only hash logging only with witness or checkpoint-comparison support and allows ledger-like replication only with a concrete finality or quorum assumption.

Case E — ledger burden violates metadata minimisation or operational feasibility. LJI 2.0 may reject the ledger-like backend even when the high-level blockchain decision procedure leaves it admissible. This is a refinement because health-audit proportionality and metadata constraints are outside the coarser procedure.

## Result

The refinement is conservative. LJI 2.0 uses the Wüst–Gervais procedure as a constraint against unjustified ledger use and specialises it through TrustEvidence properties, traceability requirements and measured or declared backend burdens.
