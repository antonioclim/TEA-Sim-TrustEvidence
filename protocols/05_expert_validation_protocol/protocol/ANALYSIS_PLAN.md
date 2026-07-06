# Analysis plan

## Status

Protocol only. Apply this plan only after ethics approval, exemption or waiver and genuine anonymised data collection.

## Input files after execution

- `data/round1_raw_anonymised.csv`
- `data/round2_raw_anonymised.csv`
- `data/participant_strata_anonymised.csv`
- `data/deviations_log.csv`

## Required rating columns

`participant_id`, `round`, `item_id`, `rating`, `comment`, `timestamp_utc`.

## Item statistics

For each item and round: n, median, Q1, Q3, IQR, minimum, maximum, percentage 1-3, percentage 4-6, percentage 7-9, missing count and decision.

## Consensus decision

Endorsement requires median >= 7, IQR <= 2 and agreement_7_9_percent >= 70. Rejection requires median <= 3, IQR <= 2 and agreement_1_3_percent >= 70. All other cases are no consensus.

## Reporting threshold

An expert-validation claim may enter the manuscript only if both rounds are completed, at least 12 eligible participants complete both rounds, response rates and attrition are reported and no material protocol deviation undermines interpretation.
