-- Persist the tsvector that BM25 search currently computes at query time.
-- Generated column lets PostgreSQL maintain it on inserts/updates without
-- application-side trigger logic; GIN index makes @@ tsquery lookups fast.

ALTER TABLE runbook_embeddings
    ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (to_tsvector('english', chunk_text)) STORED;

CREATE INDEX idx_runbook_embeddings_search_vector
    ON runbook_embeddings USING GIN (search_vector);
