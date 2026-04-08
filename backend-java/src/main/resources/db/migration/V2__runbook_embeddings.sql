-- Runbook embeddings for RAG hybrid search (pgvector + tsvector).
-- Requires pgvector extension to be enabled on the database.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE runbook_embeddings (
    id          UUID PRIMARY KEY,
    runbook_id  UUID NOT NULL REFERENCES runbooks(id),
    chunk_text  TEXT NOT NULL,
    embedding   VECTOR(1536),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_runbook_embeddings_runbook ON runbook_embeddings (runbook_id);
CREATE INDEX idx_runbook_embeddings_vector ON runbook_embeddings USING hnsw (embedding vector_cosine_ops);
