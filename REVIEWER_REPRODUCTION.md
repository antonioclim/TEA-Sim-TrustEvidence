# Reviewer reproduction

## One-command route

After installation, run:

```bash
make release-check
```

Expected high-level outcomes are:

- all unit/regression tests pass;
- all mandatory Hypothesis tests pass with no skips;
- the finite bounded state space completes without a counterexample;
- schema, canonicalisation and mutation reference outputs regenerate byte-for-byte;
- the quick workload produces the expected event/receipt/mutation decisions;
- five figures regenerate byte-for-byte;
- retained result CSVs satisfy their Draft 2020-12 contracts;
- the result-level reproducibility manifest is current;
- manifests, checksums, metadata and repository identity pass.

## Full workload route

The retained workload reference run can be regenerated with:

```bash
python experiments/run_workload_passage.py \
  --output-dir results_local/full_workload \
  --tree-sizes 128 512 2048 \
  --repetitions 12 \
  --verification-samples 32
python experiments/analyse_cmpb_results.py \
  --input-dir results_local/full_workload \
  --output-dir results_local/full_workload
```

This route may take materially longer than `--quick`. Timing values will differ by host. Decisions, event counts, sample counts and mutation outcomes should agree.

## Expected claim boundary

Successful execution supports local reproducibility of the reference implementation. It does not establish clinical utility, production readiness, standards conformance, legal compliance, global non-equivocation or resistance after compromise of an authorised key.
