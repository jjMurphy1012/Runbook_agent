-- RunbookAgent initial schema.
-- Java (Flyway) is the sole schema owner. Python reads and writes data via
-- SQLAlchemy but never runs DDL or owns schema changes.

CREATE TABLE users (
    id            UUID PRIMARY KEY,
    username      VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE alerts (
    id           UUID PRIMARY KEY,
    fingerprint  VARCHAR(128) NOT NULL,
    rule_name    VARCHAR(100) NOT NULL,
    category     VARCHAR(30)  NOT NULL,
    severity     VARCHAR(10)  NOT NULL,
    status       VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    message      TEXT,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_fingerprint ON alerts (fingerprint);
CREATE INDEX idx_alerts_status_created_at ON alerts (status, created_at DESC);

CREATE TABLE runbooks (
    id          UUID PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    root_cause  VARCHAR(500),
    version     INTEGER      NOT NULL DEFAULT 1,
    status      VARCHAR(20)  NOT NULL DEFAULT 'DRAFT',
    content     TEXT,
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_runbooks_status ON runbooks (status);
