-- Incident history for long-term semantic memory.
-- Written by Python after Postmortem completes; read by Diagnostic Reflection.

CREATE TABLE incident_history (
    id                UUID PRIMARY KEY,
    alert_fingerprint VARCHAR(128),
    rule_name         VARCHAR(100),
    category          VARCHAR(30),
    severity          VARCHAR(10),
    alert_payload     JSONB,
    diagnosis         TEXT,
    root_cause        VARCHAR(200),
    runbook_id        UUID REFERENCES runbooks(id),
    outcome           VARCHAR(20) DEFAULT 'unknown',
    human_verified    BOOLEAN DEFAULT FALSE,
    embedding         VECTOR(1536),
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_incident_history_fingerprint ON incident_history (alert_fingerprint);
CREATE INDEX idx_incident_history_verified ON incident_history (human_verified);
CREATE INDEX idx_incident_history_vector ON incident_history USING hnsw (embedding vector_cosine_ops);
