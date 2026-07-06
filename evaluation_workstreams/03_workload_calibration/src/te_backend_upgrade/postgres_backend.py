from __future__ import annotations

from typing import Any, Dict

from .canonical import canonical_hash, validate_evidence_hash

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS trust_evidence (
  evidence_id UUID PRIMARY KEY,
  evidence_type TEXT NOT NULL,
  subject_ref_token TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  consent_state TEXT NOT NULL,
  actor_role TEXT NOT NULL,
  organisation_ref TEXT NOT NULL,
  backend_type TEXT NOT NULL DEFAULT 'A1_POSTGRES',
  created_at TIMESTAMPTZ NOT NULL,
  canonical_hash TEXT NOT NULL,
  canonical_json JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_te_subject_time ON trust_evidence(subject_ref_token, created_at);
CREATE INDEX IF NOT EXISTS idx_te_policy ON trust_evidence(policy_version);
CREATE INDEX IF NOT EXISTS idx_te_consent_state ON trust_evidence(consent_state);
"""


class PostgresBackend:
    def __init__(self, dsn: str):
        import psycopg2
        import psycopg2.extras
        self.psycopg2 = psycopg2
        self.extras = psycopg2.extras
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True

    def init_schema(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)

    def append(self, obj: Dict[str, Any]) -> Dict[str, str]:
        if not validate_evidence_hash(obj):
            raise ValueError("canonical_hash does not bind evidence object")
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO trust_evidence
                (evidence_id, evidence_type, subject_ref_token, payload_hash, policy_version,
                 consent_state, actor_role, organisation_ref, backend_type, created_at,
                 canonical_hash, canonical_json)
                VALUES (%(evidence_id)s, %(evidence_type)s, %(subject_ref_token)s,
                        %(payload_hash)s, %(policy_version)s, %(consent_state)s,
                        %(actor_role)s, %(organisation_ref)s, %(backend_type)s,
                        %(created_at)s, %(canonical_hash)s, %(canonical_json)s)
                ON CONFLICT (evidence_id) DO UPDATE SET
                  canonical_hash = EXCLUDED.canonical_hash,
                  canonical_json = EXCLUDED.canonical_json
                """,
                {**obj, "canonical_json": self.extras.Json(obj)},
            )
        return {"backend": "A1_POSTGRES", "evidence_id": obj["evidence_id"], "canonical_hash": canonical_hash(obj)}

    def verify_hash(self, evidence_id: str, expected_hash: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("SELECT canonical_hash FROM trust_evidence WHERE evidence_id = %s", (evidence_id,))
            row = cur.fetchone()
        return bool(row and row[0] == expected_hash)
