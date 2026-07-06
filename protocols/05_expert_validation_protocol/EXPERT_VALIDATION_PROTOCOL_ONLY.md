# Expert validation protocol only

## Protocol status

This is a planned expert-validation protocol for future institutional review and subsequent expert-panel execution. It is not an expert-validation report. The current corpus contains protocol scaffolding and toy/sample material only; it does not contain ethics approval, a documented waiver, genuine anonymised expert responses, response-rate records, controlled-feedback outputs or a real consensus matrix.

## Objective

The future study will assess whether independent experts consider the TrustEvidence boundary, backend proportionality logic and Ledger Justification Index coherent, adequately delimited and useful for information-systems governance of auditable health information exchange.

## Design

The proposed design is a two-round anonymous Delphi/RAND-style structured appropriateness panel. Round 1 collects independent 1-9 ratings and free-text comments. Round 2 provides controlled anonymised feedback from Round 1 and asks panellists to re-rate retained or revised items. The panel evaluates governance and information-systems plausibility; it does not validate clinical safety, legal compliance, software security, FHIR/BALP conformance or production readiness.

## Ethics boundary

No recruitment may occur until an institutional ethics committee, IRB or equivalent research-governance body has issued approval, exemption or waiver. The study must not collect patient records, clinical cases, raw audit logs, system secrets, employer-confidential incidents or legal advice. Contact details must be stored separately from response data. Public deposits must not contain identifiable participant-level data.

## Panel composition

Target completed panel: 18-24 experts. Minimum credible pilot-level analysed panel: 12 experts completing both rounds. The panel should cover health informatics/HIE, FHIR/HL7/IHE implementation, information security/audit, information systems governance/enterprise architecture, legal/ethics/data-protection governance and research software/reproducibility.

## Eligibility

Eligible participants should have at least five years of relevant professional/research experience or a recognised standards, governance or implementation role. Direct artefact authors, dependent supervisees/employees and participants with unmanageable conflicts should not contribute ratings.

## Consensus criteria

All core items use a 1-9 scale. Criteria are fixed before recruitment:

- endorsement consensus: median >= 7, IQR <= 2 and at least 70% of ratings in the 7-9 band;
- rejection consensus: median <= 3, IQR <= 2 and at least 70% of ratings in the 1-3 band;
- no consensus: all other patterns;
- stability: absolute median shift <= 1 between rounds.

An item may be called stable endorsement only if Round 2 satisfies endorsement consensus and the Round 1 to Round 2 median shift is <= 1.

## Analysis

For each item and round, report n, median, Q1, Q3, IQR, percentage in 1-3, percentage in 4-6, percentage in 7-9, missingness and decision. For two-round items, report median shift and stability. Free-text responses should be summarised thematically and anonymised; direct quotations require explicit consent and ethics approval.

## Manuscript consequence

Unless the future panel is completed under ethics approval/waiver with at least 12 two-round completers and pre-specified consensus criteria, the manuscript may state only that a protocol is provided. The manuscript must not present expert-validation results, consensus-backed LJI thresholds or expert-endorsed backend selection.
