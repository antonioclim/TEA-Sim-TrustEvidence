# Route C C4 HIE security results

These files are deterministic retained evidence for the synthetic `HIE-DISCLOSURE-001` case.

- `hie_security_mutation_results.csv` contains one decision row per positive, negative or limitation case.
- `hie_security_mutation_run.json` contains aggregate counts and the final claim boundary.
- `hie_security_case_evidence.jsonl` contains candidate/proof digests, observed codes and retained-state snapshots.

Generate:

```bash
python experiments/run_hie_security_mutations.py \
  --output-dir results_expected/cmpb_reference/c4_hie_security
```

Verify without writing:

```bash
python experiments/run_hie_security_mutations.py --check
```

Expected limitation acceptances are not false accepts. They document what the implemented cryptography does not establish: authorised-signer truth, stateless split-view detection and duplicate-replay rejection.
