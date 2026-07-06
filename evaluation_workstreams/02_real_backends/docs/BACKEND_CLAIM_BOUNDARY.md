# Backend claim boundary

| Backend | backend-evaluation workstream status | Allowable wording | Forbidden wording |
|---|---|---|---|
| A1 PostgreSQL | Schema and adapter present; Docker/`psql`/DSN unavailable in current runtime | PostgreSQL pathway specified and probed; execution unavailable in this runtime | PostgreSQL benchmark, PostgreSQL measured, production database performance |
| A2 Merkle | Executed locally with tests, tamper checks and reference benchmark | Local reference-implementation execution for the Merkle backend | production benchmark, full cryptographic proof, deployment evidence |
| A3 Rekor/Trillian/Fabric | Adapter/protocol scaffolding only; no local service executed | adapter/protocol artefact, not executed backend evidence | local transparency-log execution, blockchain benchmark, Fabric execution |
