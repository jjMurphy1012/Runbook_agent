# RunbookAgent Project Overview

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
