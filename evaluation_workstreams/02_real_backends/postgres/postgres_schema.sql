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
CREATE INDEX IF NOT EXISTS idx_te_backend ON trust_evidence(backend_type);
