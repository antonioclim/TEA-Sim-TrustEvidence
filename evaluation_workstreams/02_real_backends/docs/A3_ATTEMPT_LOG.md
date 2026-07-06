
# A3 attempt log

created_utc: `2026-07-05T17:46:02Z`

A3 local transparency/ledger-like execution was probed but not executed. The current runtime did not contain Docker, `rekor-cli`, `trillian_log_server` or a Fabric `peer` binary. Go was present, but that alone is insufficient for a local Rekor, Trillian or Fabric service. Public transparency-log submission was not attempted; the adapter produces synthetic hash-commitment envelopes only.

See `benchmark_outputs/probes/a3_probe.json`.
