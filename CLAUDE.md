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
- No A2A in MVP; keep orchestration inside LangGraph until the baseline is proven

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

1. Infrastructure and data: Docker Compose, schema, PostgreSQL, Redis, seed scripts
2. Redis layer: diagnosis cache, rate limiter, Redis Streams for cross-service event passing
3. Retrieval and tools: embeddings, hybrid search, MCP tool layer
4. Agent workflow: triage, diagnostic, postmortem, then remediation (LangGraph StateGraph)
5. Streaming: Redis Streams → SSE bridge, Java SSE proxy for frontend
6. Product layer: dashboard, stream viewer, runbook review, auth polish
7. Evaluation and polish: RAG test script, latency checks, LangSmith traces
8. A2A spike only after the LangGraph baseline is stable and measurable

## Redis Strategy

Redis serves three distinct roles in this project. All three should be wired early because they underpin cross-service communication and agent performance.

### 1. Diagnosis Cache

Cache LLM diagnostic results keyed by alert fingerprint (rule_name + labels hash). When the same alert fires again within TTL, return cached diagnosis instead of re-running the full agent pipeline. This saves LLM cost and reduces latency for repeat incidents.

- Module: `backend-python/cache/diagnosis_cache.py`
- Key pattern: `diag:{alert_fingerprint}`
- TTL: configurable, default 30 minutes

### 2. Rate Limiter

Token-bucket or sliding-window rate limiter on LLM API calls to prevent cost blowout during burst alert scenarios.

- Module: `backend-python/cache/rate_limiter.py`
- Key pattern: `ratelimit:llm:{window}`

### 3. Redis Streams (Cross-Service Event Bus)

This is the most important Redis role. Redis Streams connect the Python agent service to the Java API layer:

- Python agent publishes step-by-step events (triage started, diagnostic tool called, postmortem generated) to a Redis Stream
- Java backend consumes the stream and proxies events to the frontend via SSE
- This decouples agent execution from the API layer — the agent does not need to know about SSE or frontend connections

Flow: `LangGraph node → Redis Stream → Java StreamController → SSE → Frontend`

- Publisher: `backend-java/RedisStreamPublisher.java` (Java→Redis) and `backend-python/workers/stream_consumer.py` (Python→Redis)
- Stream key: `alerts:{alert_id}:events`
- Consumer group: `runbook-api-group`

### When to Wire Redis

Redis should be set up in **Step 1-2** of the delivery plan, not deferred. Reasons:

- SSE streaming depends on Redis Streams as the transport layer between Python and Java
- Diagnosis cache must be in place before agent pipeline testing to get realistic latency numbers
- Rate limiter should be active before any LLM calls go live to avoid accidental cost spikes

## A2A Adoption Plan

A2A should be treated as a phase-two experiment, not a foundation requirement. The project should first prove that one FastAPI service can run the full LangGraph workflow reliably. Introducing A2A earlier would add protocol and coordination complexity before the baseline behavior is understood.

### When to Prompt for A2A

Explicitly raise the A2A question when all of these conditions are true:

- LangGraph runs end to end for at least 3 alert scenarios without manual intervention
- Redis Streams and SSE show complete node-level traces across the workflow
- At least one integration test passes for `alert -> diagnosis -> remediation or postmortem -> runbook draft`
- Tool boundaries are stable enough that specialist agents would have clean responsibilities
- Basic latency and token usage have been measured, so A2A overhead can be compared against a known baseline

### What the A2A Spike Should Test

- Whether diagnostic, remediation, and runbook review agents benefit from explicit agent-to-agent handoffs
- Whether A2A improves modularity more than it hurts latency and implementation complexity
- Whether cross-agent contracts are clearer than the current shared-state LangGraph design

If the trigger conditions are met, that is the point to remind you to try A2A. Before that point, the correct default is: keep the workflow in LangGraph and avoid introducing another orchestration layer.

## Recommendation

Proceed with the project, but keep the first milestone narrow. If the MVP works reliably for 3 scenarios with visible agent traces and reviewable runbook output, it is already strong enough to document and demo.
