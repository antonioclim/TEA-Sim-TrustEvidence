# Sensitivity analysis plan for LJI 2.0

Status: pre-execution plan. No sensitivity result is reported in v2.0.0.

## Objective

The sensitivity analysis tests whether backend selection is robust to uncertainty in property-demand weights, burden weights, interaction terms, thresholds, legal interpretations, witness/finality availability and v2.0.0 measured-cost normalisers.

## Planned analyses

The machine-readable plan in `tables/lji2_sensitivity_plan.csv` contains twelve factors [computed:v2.0.0-lji2]. It includes simplex-based weight variation, additive-versus-interaction model comparison, legal/minimisation scenario variants, witness/finality availability cases and v2.0.0 measurement-normaliser uncertainty.

## Outputs after execution

The executed analysis will report backend rank acceptability, A3 eligibility frequency, decision reversal rate, legal/minimisation block frequency and workload-class stability. These outputs remain `[external validation required:v2.0.0-external-services]` until the analysis is run with validated v2.0.0 and v2.0.0 inputs.

## Anti-overclaim rule

If sensitivity shows that A3 eligibility changes materially under reasonable weights or legal interpretations, the manuscript must report the result as decision instability rather than choosing the most favourable parameterisation.
