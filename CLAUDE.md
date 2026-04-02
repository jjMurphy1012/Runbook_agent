# RunbookAgent Project

## Feasibility Verdict

This project is feasible as a portfolio or resume project if it is treated as a demo-grade AIOps platform, not a production-grade incident automation system. The strongest value is the end-to-end story: alert intake, agent-driven diagnosis, simulated remediation, runbook generation, and human review in one workflow.

The current design is technically coherent. Spring Boot owns business APIs and auth, FastAPI owns agent orchestration and RAG, Redis handles cache and streams, and PostgreSQL stores business data plus pgvector retrieval. That separation makes sense. The main risk is not architecture correctness, but scope. Three runtimes, two backends, SSE streaming, Redis Streams, RAG, MCP tools, and evaluation can become too much if everything is built at once.

## Recommended MVP

Build the first version around one reliable happy path:

- 3 alert scenarios instead of 6
- FastAPI LangGraph pipeline with Triage -> Diagnostic -> Postmortem first
- Simulated remediation only after diagnosis is stable
- PostgreSQL runbook storage with hybrid retrieval
- SSE stream for visible reasoning
- Manual runbook review page

This still demonstrates multi-agent orchestration, tool use, retrieval, and product thinking without forcing full production complexity.

## Suggested Architecture Snapshot

- `frontend/`: React + TypeScript dashboard, agent panel, runbook review
- `backend-java/`: auth, CRUD, session, alert lifecycle, SSE proxy
- `backend-python/`: LangGraph workflow, MCP tools, RAG, streaming, workers
- `scripts/`: seed data and evaluation scripts
- `data/`: simulated logs, metrics, runbooks, command responses

Keep all remediation commands simulated. That keeps the system safe while still showing agent decision quality.

## Main Delivery Risks

- Integration overhead across Java, Python, Redis, PostgreSQL, and frontend
- Unclear boundaries between business API and agent service
- RAG quality tuning taking longer than expected
- Redis Streams and SSE consistency bugs during long-running flows
- Evaluation scope expanding beyond the core demo

## Delivery Plan

1. Infrastructure and data: Docker Compose, schema, Redis, seed scripts
2. Retrieval and tools: embeddings, hybrid search, MCP tool layer
3. Agent workflow: triage, diagnostic, postmortem, then remediation
4. Product layer: dashboard, stream viewer, runbook review, auth polish
5. Evaluation and polish: RAG test script, latency checks, LangSmith traces

## Recommendation

Proceed with the project, but keep the first milestone narrow. If the MVP works reliably for 3 scenarios with visible agent traces and reviewable runbook output, it is already strong enough to document and demo.
