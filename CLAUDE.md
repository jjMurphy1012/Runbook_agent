# RunbookAgent Project

## Verdict

Feasible as a demo-grade AIOps portfolio project, not a production incident system. The value is the end-to-end story: alert intake, agent-driven diagnosis, simulated remediation, runbook generation, and human review in one workflow. Main risk is scope — three runtimes, two backends, SSE, Redis Streams, RAG, MCP tools, and evaluation can overwhelm a single developer if built all at once. Keep the first milestone narrow.

## MVP Scope

- 3 alert scenarios
- LangGraph pipeline: Triage → Diagnostic (Reflection mode) → Postmortem, then Remediation
- PostgreSQL runbook storage with hybrid retrieval (pgvector + tsvector + RRF)
- SSE stream for visible reasoning
- Manual runbook review page
- All remediation commands simulated

## Architecture

- `frontend/`: React + TypeScript dashboard, agent panel, runbook review
- `backend-java/`: JWT auth (stateless), CRUD, alert lifecycle, SSE proxy
- `backend-python/`: LangGraph workflow, MCP tools, RAG, streaming, workers
- `scripts/`: seed data and evaluation
- `data/`: simulated logs, metrics, runbooks, command responses

## Delivery Plan

1. Infrastructure: Docker Compose, PostgreSQL schema, Redis, seed scripts
2. Retrieval and tools: embeddings, hybrid search, MCP tool layer
3. Agent workflow: triage, diagnostic (reflection), postmortem, remediation
4. Streaming: Redis Streams → Java SSE proxy → frontend
5. Product layer: dashboard, stream viewer, runbook review, auth
6. Evaluation: RAG test script, latency checks, LangSmith traces

## Main Risks

- Cross-service integration (Java ↔ Python ↔ Redis ↔ Postgres)
- RAG quality tuning taking longer than expected
- Redis Streams and SSE consistency during long-running flows

## Redis Strategy

Redis serves three roles. All should be wired in step 1 because they underpin cross-service communication and agent performance.

### 1. Diagnosis Cache

Cache LLM diagnostic results keyed by alert fingerprint (rule_name + labels hash). Same alert within TTL returns cached diagnosis instead of re-running the pipeline.

- Module: `backend-python/cache/diagnosis_cache.py`
- Key: `diag:{alert_fingerprint}`
- TTL: default 30 minutes

### 2. Rate Limiter

Sliding-window limiter on LLM API calls to prevent cost blowout during burst alerts.

- Module: `backend-python/cache/rate_limiter.py`
- Key: `ratelimit:llm:{window}`

### 3. Redis Streams (Event Bus)

Python agent publishes per-step events to a Redis Stream. Java consumes and proxies to frontend via SSE. This decouples agent execution from the API layer.

Flow: `LangGraph node → Redis Stream → Java StreamController → SSE → Frontend`

- Publishers: `backend-java/RedisStreamPublisher.java`, `backend-python/workers/stream_consumer.py`
- Stream key: `alerts:{alert_id}:events`
- Consumer group: `runbook-api-group`

## Diagnostic Reflection Mode

The diagnostic stage uses an Analyzer + Critic loop instead of a single-pass LLM call. This is the project's main differentiator.

A preset "bull vs bear" debate requires hardcoding opposing stances per alert type, does not generalize, and risks excluding the correct root cause. Reflection avoids this: the Analyzer freely diagnoses, and the Critic may point to any alternative direction — including ones the Analyzer never considered.

### Structure

```
Evidence → Analyzer → Critic → (converged?) → Finalizer
              ↑___________________|
                  loop, max 3 rounds
```

- **Analyzer**: Free-form diagnosis. First round unbiased. Later rounds see Critic feedback and may accept, reject, or partially revise.
- **Critic**: Reviews the analysis against the full evidence (not just the analysis text). Flags missed evidence, logic gaps, alternative hypotheses, correlation-vs-causation errors. Severity-graded.
- **Finalizer**: Synthesizes final diagnosis from all rounds after convergence.

### Convergence

Loop ends when any of:

- Critic reports no major or critical issues
- Two consecutive rounds produce substantially identical analyses
- `max_rounds=3` reached

### Prompt Guardrails

- Analyzer may reject Critic feedback with justification (prevents sycophantic collapse)
- Critic minor issues do not block convergence (prevents infinite nitpicking)
- Critic must cite specific evidence when proposing alternatives (prevents hand-waving)

### Cost Control

Reflection mode runs only when Triage flags `severity=HIGH` or `ambiguity_score>0.5`. Other alerts use single-pass diagnostic. Each reflection round's output is pushed as a distinct SSE event so the frontend renders the iteration as a visible conversation.

## Incident Memory

Long-term semantic memory of past incidents. Distinct from Diagnosis Cache (short-term exact-match shortcut) and static Seed Runbooks (hand-curated theoretical knowledge). Memory captures actual past decisions and feeds them to the Analyzer as prior context.

### Schema

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

### Write Path

After Postmortem completes, insert the record with `human_verified=false`. When a reviewer approves the runbook on the review page, flip `human_verified=true`. Both verified and unverified records are stored; retrieval filters by `human_verified=true` only.

### Read Path

Triggered at the start of Diagnostic Reflection, after Evidence Collection and before the first Analyzer round. Retrieves top-3 semantically similar past incidents via pgvector cosine similarity on `alert_payload` embedding. Results are auto-injected into the Analyzer prompt — not exposed as an MCP tool, not shown to the Critic.

### Anchoring Prevention

The Analyzer prompt explicitly marks historical context as "reference only" and requires the Analyzer to state why the current situation differs if its diagnosis diverges from history. Critic never sees memory context — this keeps the Critic's challenges evidence-driven rather than history-driven.

### Cold Start

Seed 3-5 hand-written verified cases (one per MVP scenario) at install time. This gives Memory non-trivial behavior from day one.

## Auth Strategy

Stateless JWT. Spring Session removed; Redis is reserved for cache and streams only.

- Login/register endpoints issue signed JWT tokens
- All API requests carry `Authorization: Bearer <token>`
- Spring Security configured with `SessionCreationPolicy.STATELESS`
- `spring-session-data-redis` removed from pom.xml
