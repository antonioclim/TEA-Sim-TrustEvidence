
# A1 PostgreSQL unavailable status

created_utc: `2026-07-05T17:46:02Z`

A1 PostgreSQL execution was attempted only to the point of prerequisite probing. The runtime contained no Docker executable, no `psql`, no `TEA_POSTGRES_DSN` and no Python PostgreSQL driver. The PostgreSQL schema and adapter remain in the kit for maintainer-side execution, but backend-evaluation workstream generated no PostgreSQL timing or verification measurements.

See `benchmark_outputs/probes/postgres_probe.json`.
