# LJI 2.0: Axiomatic decision layer for evidence-storage proportionality


## 1. Purpose

LJI 2.0 replaces the v1 Ledger Justification Index as a decision layer for choosing the minimum sufficient TrustEvidence backend. Its decision object is not “whether blockchain is good”. Its decision object is: given a stated health-audit workload, threat model, legal/standards duties and measurement evidence, which evidence-storage backend is proportionate: `BE-A1` central audit, `BE-A2` append-only hash log, `BE-A3` ledger-like replicated backend, or `NO-DECISION` because the emission boundary is not instrumented.

The v1 LJI is not inherited as an adoption rule. The v1 fixed thresholds `-0.05` and `+0.10` are retained only as archived v1 history [ASSUMED:v1-history]. LJI 2.0 has no fixed adoption thresholds in v2.0.0. Thresholds and weights are parameters until Delphi calibration and sensitivity reporting Delphi calibration required.

## 2. Inputs

The model consumes four classes of input:

- `T`: v2.0.0 threat and assumption state, including adversaries and whether `A7` witness/gossip or `A8` quorum/finality are satisfied [ASSUMED:v2.0.0-protocol].
- `D`: property-demand vector over tamper-evidence, append-only consistency, inclusion verifiability, non-equivocation, boundary completeness, freshness and legal traceability, normalised to the unit interval [ASSUMED:v2.0.0-protocol].
- `C`: backend capability matrix derived from the v2.0.0 formal core, with zero credit where the required assumption is absent [ASSUMED:v2.0.0-protocol].
- `B`: backend burden vector covering metadata exposure, storage/proof burden, latency/throughput burden, governance complexity, assumption fragility and cryptographic-agility burden [ASSUMED:v2.0.0-protocol]. Measurement-dependent burden components remain `external measurement required`.

## 3. Lexicographic screens before scoring

LJI 2.0 is intentionally not a raw weighted sum. The screens in `tables/lji2_screening_rules.csv` execute first [computed:v2.0.0-lji2]. They implement non-compensability: if an in-scope workload requires non-equivocation, a cheaper backend cannot be selected merely because its burden score is lower. If the evidence-emission boundary is incomplete, the procedure returns `NO-DECISION`; no backend can prove events that were never emitted.

## 4. Parametric value function

For each eligible backend `b`, define:

`U(b | s) = Σ_p alpha_p * demand_p(s) * capability_b,p(T)`.

`K(b | s) = Σ_q beta_q * burden_b,q(s) + Σ_r gamma_r * interaction_r(b, s)`.

`LJI2(b | s) = U(b | s) - K(b | s)`.

The selected backend is the least burdensome backend that passes the mandatory screens and has no unresolved mandatory shortfall. `BE-A3` may be recommended only if it passes the independent-verification and metadata-minimisation screens and its material advantage over the best non-ledger backend exceeds a Delphi-validated margin Delphi calibration required. If that margin is not validated, the manuscript reports only a sensitivity surface, not a categorical recommendation.

## 5. Axioms

The axiom register contains nine rows [computed:v2.0.0-lji2]. The most important are: evidence-boundary limitation, assumption fidelity, dominance, minimal sufficiency, non-compensability of mandatory properties, scale invariance after normalisation, declared interaction discipline, legal interpretability boundary and validation humility. These axioms prevent the old failure mode in which a single unvalidated scalar made ledger-like replication appear justified.

## 6. Registered interactions

The additive form is permitted only after preferential independence is accepted by the Delphi panel. Before that, the following interactions are registered explicitly [ASSUMED:v2.0.0-protocol]:

- no mutually trusted audit maintainer × non-equivocation demand;
- legal traceability demand × third-party verification demand;
- metadata exposure × organisational multiplicity;
- freshness/notification demand × verifier-state reliability.

Unregistered interactions are not allowed to enter the manuscript under rhetorical language.

## 7. Boundary of the v2.0.0 claim

v2.0.0 proves no new cryptographic property, measures no backend cost and asserts no legal compliance. Its claim is narrower: the decision layer is now axiomatic, assumption-aware, Wüst–Gervais-compatible, sensitivity-ready and Delphi-ready. Scenario-specific recommendations remain blocked until external-service measurements, v2.0.0 legal traceability and Delphi calibration are available.
