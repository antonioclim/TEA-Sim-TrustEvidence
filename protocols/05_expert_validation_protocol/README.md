# Expert validation protocol kit

Date prepared: 2026-07-05.  
Status: **protocol only; no expert-validation claim**.

This kit prepares an ethics-sensitive two-round Delphi/RAND-style expert-panel protocol for future assessment of the TrustEvidence boundary and Ledger Justification Index (LJI). It contains no institutional ethics approval, no ethics waiver, no genuine anonymised expert responses and no consensus result. Any toy or synthetic files are script smoke-test material only and must never be cited as expert evidence.

## Public wording boundary

Allowed now: `A structured expert-validation protocol is supplied for subsequent evaluation. The LJI remains an exploratory decision-support heuristic.`

Forbidden now: `expert validated`, `Delphi consensus`, `RAND/UCLA consensus`, `expert-reviewed LJI`, `content validated`, `validated decision framework`, `expert-endorsed thresholds`, `generalisable expert agreement` or equivalent wording.

## Directory map

- `protocol/`: protocol, ethics determination template, analysis plan and data-management plan.
- `instruments/`: participant information/consent text and two-round questionnaire instruments.
- `recruitment/`: sampling frame, eligibility and conflict controls and invitation template.
- `reporting/`: consensus status, CREDES/DELPHISTAR/RAND mapping and claim boundary.
- `scripts/`: future analysis script for real ethics-cleared anonymised data.
- `examples/`: synthetic toy data for smoke testing the script only.
- `references/`: verified methodological references used to construct the protocol.

## Smoke test

```bash
python scripts/analyse_expert_panel.py --round1 examples/toy_non_evidence_round1.csv --round2 examples/toy_non_evidence_round2.csv --out examples/toy_non_evidence_consensus.csv
```

The resulting CSV is not a consensus matrix and must not be treated as human-subject data.
