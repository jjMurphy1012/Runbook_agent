# Incident Memory

Long-term semantic memory of past incidents. Distinct from Diagnosis Cache (short-term exact-match shortcut) and static Seed Runbooks (hand-curated theoretical knowledge). Memory captures actual past decisions and feeds them to the Analyzer as prior context.

## Schema

```sql
CREATE TABLE incident_history (
  id UUID PRIMARY KEY,
  alert_fingerprint VARCHAR(128),
  rule_name VARCHAR(100),
  category VARCHAR(30),
  severity VARCHAR(10),
  alert_payload JSONB,
  diagnosis TEXT,
  root_cause VARCHAR(200),
  runbook_id UUID REFERENCES runbooks(id),
  outcome VARCHAR(20),        -- resolved | false_positive | escalated | unknown
  human_verified BOOLEAN,
  embedding VECTOR(1536),     -- embedded from alert_payload
  created_at TIMESTAMPTZ
);
```

## Write Path

After Postmortem completes, insert the record with `human_verified=false`. When a reviewer approves the runbook on the review page, flip `human_verified=true`. Both verified and unverified records are stored; retrieval filters by `human_verified=true` only.

## Read Path

Triggered at the start of Diagnostic Reflection, after Evidence Collection and before the first Analyzer round. Retrieves top-3 semantically similar past incidents via pgvector cosine similarity on `alert_payload` embedding. Results are auto-injected into the Analyzer prompt — not exposed as an MCP tool, not shown to the Critic.

## Anchoring Prevention

The Analyzer prompt explicitly marks historical context as "reference only" and requires the Analyzer to state why the current situation differs if its diagnosis diverges from history. Critic never sees memory context — this keeps the Critic's challenges evidence-driven rather than history-driven.

## Cold Start

Seed 3-5 hand-written verified cases (one per MVP scenario) at install time. This gives Memory non-trivial behavior from day one.
