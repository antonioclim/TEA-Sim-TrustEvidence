# LJI 2.0: decision layer for evidence-storage proportionality

## Purpose

LJI 2.0 replaces the v1 Ledger Justification Index as a structured decision layer for choosing the minimum sufficient TrustEvidence backend. Its question is not whether a blockchain is generally useful. Its question is narrower: given a health-audit workload, threat assumptions, standards duties and available measurements, which evidence-storage backend is proportionate — central audit, append-only hash log, ledger-like replicated backend, or no decision because the evidence-emission boundary is not adequately instrumented?

The v1 fixed thresholds `-0.05` and `+0.10` are retained only as historical information. LJI 2.0 does not publish fixed adoption thresholds without expert calibration and sensitivity analysis.

## Inputs

The decision layer consumes four classes of input:

- `T`: threat and assumption state, including whether witness/gossip support or quorum/finality support is available.
- `D`: property-demand vector over tamper-evidence, append-only consistency, inclusion verifiability, non-equivocation, boundary completeness, freshness and legal traceability.
- `C`: backend capability matrix derived from the formal core, with no credit where the necessary assumption is absent.
- `B`: backend burden vector covering metadata exposure, storage/proof burden, latency/throughput burden, governance complexity, assumption fragility and cryptographic-agility burden.

## Screens before scoring

LJI 2.0 applies mandatory screens before any weighted comparison. If the evidence-emission boundary is incomplete, the procedure returns `NO-DECISION`. If non-equivocation is mandatory, a cheaper backend cannot be selected merely because it has a lower burden score. If replication would expose excessive metadata, the ledger-like option is blocked until minimisation and retention controls are specified.

## Parametric value function

For each eligible backend `b` and scenario `s`:

`U(b | s) = Σ_p alpha_p * demand_p(s) * capability_b,p(T)`

`K(b | s) = Σ_q beta_q * burden_b,q(s) + Σ_r gamma_r * interaction_r(b, s)`

`LJI2(b | s) = U(b | s) - K(b | s)`

The selected backend is the least burdensome backend that passes the mandatory screens and has no unresolved mandatory shortfall. A ledger-like backend may be recommended only if it passes the independent-verification and metadata-minimisation screens and its material advantage over the best non-ledger option exceeds a defensible margin.

## Boundary of the decision claim

The decision layer proves no new cryptographic property, measures no backend cost and asserts no legal compliance. Its claim is narrower: backend choice should be assumption-aware, property-aware, sensitivity-ready and explicit about when simpler audit mechanisms are more proportionate than ledger-like replication.
