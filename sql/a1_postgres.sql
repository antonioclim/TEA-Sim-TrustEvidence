create table if not exists trustevidence_a1_audit_log (
    sequence_id bigserial primary key,
    artefact_id text not null unique,
    event_id text not null unique,
    core_hash_b64 text not null,
    envelope_json jsonb not null,
    receipt_json jsonb not null,
    inserted_at timestamptz not null default now(),
    revoked_at timestamptz null,
    constraint trustevidence_a1_no_empty_core_hash check (length(core_hash_b64) > 0),
    constraint trustevidence_a1_no_update_delete_marker check (revoked_at is null)
);
create index if not exists trustevidence_a1_event_idx on trustevidence_a1_audit_log (event_id);
-- deployment role grants INSERT and SELECT only; UPDATE, DELETE and TRUNCATE are not granted to the application role.
