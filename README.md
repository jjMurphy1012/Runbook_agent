# RunbookAgent

**An AI-powered AIOps platform that automates incident diagnosis through multi-agent collaboration and turns resolutions into reusable runbooks.**

`LangGraph` `Spring Boot 3` `FastAPI` `React 18` `pgvector` `Redis Streams` `GPT-4o-mini` `Flyway` `Docker Compose`

When an infrastructure alert fires, RunbookAgent runs a full pipeline — triage, evidence collection, root-cause diagnosis, remediation planning, and runbook generation — with live-streamed reasoning visible to the on-call engineer. The system learns from past incidents and improves over time.

---

## Why I Built This

I wanted to demonstrate **end-to-end system design across multiple services and languages** — not just a single-service CRUD app. AIOps is a domain where AI agents genuinely add value: incident response is time-pressured, evidence is scattered across logs/metrics/runbooks, and institutional knowledge lives in people's heads rather than in code.

This project demonstrates:
- **Polyglot microservice architecture** — Java API gateway + Python agent service + TypeScript frontend, communicating via HTTP, Redis Streams, and SSE
- **AI agent orchestration** — LangGraph StateGraph with conditional routing, reflection loops, and tool-calling, not just a chain of prompt wrappers
- **Cross-service integration** — schema ownership strategy, event streaming, cache coherence, and dual-mode deployment
- **Deliberate architectural trade-offs** — each major decision has a documented alternative and rationale (see [Design Decisions](#design-decisions-and-trade-offs))

## Architecture

```
┌──────────────┐    ┌─────────────────────┐    ┌──────────────────────────────┐
│   Frontend   │    │   Spring Boot API   │    │    FastAPI Agent Service      │
│  React + TS  │◄──►│   (Java 17)         │───►│    (Python + LangGraph)      │
│  Tailwind    │SSE │                     │HTTP│                              │
└──────────────┘    │  • JWT Auth         │    │  • Triage Agent              │
                    │  • Alert CRUD       │    │  • Diagnostic (Reflection)   │
                    │  • Runbook Review   │    │  • Remediation Agent         │
                    │  • SSE Proxy        │    │  • Postmortem Agent          │
                    │  • Flyway Migrations│    │  • RAG Hybrid Search         │
                    └────────┬────────────┘    │  • MCP Tool Adapters         │
                             │                 └─────────────┬────────────────┘
                             │                               │
                    ┌────────▼────────┐           ┌──────────▼──────────┐
                    │     Redis       │◄──────────│   PostgreSQL        │
                    │  • Diag Cache   │  Streams  │   • pgvector        │
                    │  • Rate Limiter │           │   • tsvector (FTS)  │
                    │  • Event Bus    │           │   • Incident Memory │
                    └─────────────────┘           └─────────────────────┘
```

**Data flow**: Java API receives alert → calls Python `/agent/run` → LangGraph pipeline executes → each node publishes events to Redis Stream → Java consumes stream, proxies to frontend via SSE → user sees live reasoning in real time.

**Schema ownership**: Java owns all DDL via Flyway migrations. Python reads and writes data but never creates or alters tables. This prevents migration conflicts in a polyglot setup.

## Key Technical Highlights

### 1. Diagnostic Reflection Mode (Analyzer ↔ Critic Loop)

Instead of a single LLM call for diagnosis, high-severity alerts go through an **iterative Analyzer / Critic debate**:

```
Evidence → Analyzer → Critic → (converged?) → Finalizer
              ↑___________________|
                  loop, max 3 rounds
```

**Why not preset debate positions?** A "bull vs bear" pattern requires hardcoding opposing stances per alert type. If the correct root cause isn't one of the preset positions, the system can never find it. Reflection avoids this — the Critic can challenge from *any* direction, including ones the Analyzer never considered.

**Convergence**: Loop exits when (a) Critic reports no major issues, (b) two consecutive rounds produce the same analysis, or (c) `max_rounds=3` is reached.

**Anti-sycophancy guardrails**:
- Analyzer *may reject* Critic feedback with justification → prevents blind acceptance
- Critic minor issues don't block convergence → prevents infinite nitpicking
- Critic must cite specific evidence for alternatives → prevents hand-waving

> [`agents/reflection.py`](backend-python/agents/reflection.py)

### 2. Hybrid RAG with Reciprocal Rank Fusion

Runbook retrieval combines two strategies and fuses results:

| Strategy | Mechanism | Strength |
|----------|-----------|----------|
| **pgvector** cosine similarity | Semantic search via text-embedding-3-small | Finds conceptually similar content even with different wording |
| **PostgreSQL tsvector** | Full-text search with `ts_rank` scoring | Catches exact technical terms that semantic search may dilute |
| **RRF fusion** | `score = Σ 1/(k + rank)` across both lists | Combines rankings without score normalization issues |

Both searches run **concurrently** via `asyncio.gather`, then RRF merges and re-ranks.

> [`rag/hybrid.py`](backend-python/rag/hybrid.py) · [`rag/reranker.py`](backend-python/rag/reranker.py)

### 3. Incident Memory with Anchoring Prevention

The system builds long-term semantic memory from past incidents:

- **Write path**: After Postmortem, the incident is stored with `human_verified=false`. When an engineer approves the runbook, the record flips to `true`.
- **Read path**: Before the first Analyzer round, top-3 similar *verified* incidents are retrieved via pgvector cosine similarity on `alert_payload` embeddings.
- **Anchoring prevention**: Memory is injected *only* into the Analyzer (never the Critic), marked as "reference only". The Analyzer must explain divergence from history. The Critic sees only raw evidence — keeping its challenges independent.

> [`agents/memory.py`](backend-python/agents/memory.py)

### 4. Cross-Service Event Streaming

Agent execution is decoupled from the API layer via Redis Streams:

```
LangGraph node → emit_event() → Redis Stream → Java StreamController → SSE → Frontend
```

Each node (triage, evidence collection, diagnostic, each reflection round, remediation, postmortem) emits a typed event. The frontend renders these as a **live trace** — the user watches the agent think in real time, including the Analyzer/Critic back-and-forth.

> [`agents/utils.py`](backend-python/agents/utils.py) · [`StreamController.java`](backend-java/src/main/java/com/runbookagent/controller/StreamController.java)

### 5. MCP Tool Adapters (Simulated)

Tool adapters following the Model Context Protocol pattern. All infrastructure commands are **simulated** with deterministic responses — demonstrating the decision-making pipeline without touching real infrastructure:

| Tool | Purpose |
|------|---------|
| `log_query` | Read simulated incident logs per scenario |
| `metrics_query` | Read simulated time-series metrics |
| `knowledge_search` | Hybrid RAG search over runbook corpus |
| `execute_command` | Return predefined responses for infrastructure commands |

> [`mcp_local/tools/`](backend-python/mcp_local/tools/)

## Tech Stack

| Layer | Technology | Why this choice |
|-------|-----------|----------------|
| Agent orchestration | **LangGraph** StateGraph | Explicit graph with conditional edges, typed state, and support for cycles (reflection loop) — not just a linear chain |
| LLM | **GPT-4o-mini** | Cost-efficient for multi-round reflection (6+ LLM calls per high-severity alert) |
| Embeddings | **text-embedding-3-small** | 1536-dim, best quality/cost ratio for RAG at this scale |
| Vector search | **pgvector** (HNSW index) | No separate vector DB — lives alongside relational data in one PostgreSQL instance |
| Full-text search | **PostgreSQL tsvector** | Native FTS, zero external dependencies, combines with pgvector in same query |
| Event bus | **Redis Streams** | Persistent, consumer-group capable, lighter than Kafka for this scale |
| Cache + Rate limit | **Redis** | Diagnosis cache with TTL + sliding-window rate limiter on LLM calls |
| API gateway | **Spring Boot 3.3** | Stateless JWT auth, Flyway migrations, SSE proxy, WebClient for async HTTP |
| Agent service | **FastAPI** | Async-native Python, pairs naturally with LangGraph's `ainvoke` |
| Frontend | **React 18** + TypeScript + Tailwind | SSE via `EventSource`, real-time trace rendering |
| Schema management | **Flyway** | Single DDL owner (Java) — Python never runs migrations, preventing polyglot conflicts |
| Containerization | **Docker Compose** | `pgvector/pgvector:pg16` + Redis 7 + both backends in one `docker-compose up` |

## Design Decisions and Trade-offs

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Reflection loop over preset debate | Bull-vs-bear with hardcoded positions | Preset positions create selection bias — the correct root cause may fall outside chosen stances |
| Hybrid RAG (pgvector + tsvector + RRF) | Cohere reranker, HyDE | No external API dependency; RRF is simple, effective, and explainable |
| Redis Streams over direct SSE | Python SSE straight to frontend | Decouples agent execution from HTTP lifecycle; Java can proxy with auth + reconnection |
| Stateless JWT over Spring Session | Spring Session + Redis | Redis reserved for cache and streams only; simpler security model |
| Java owns schema (Flyway) | Python Alembic, or dual migrations | Single migration owner eliminates DDL conflicts in polyglot setup |
| GPT-4o-mini over GPT-4o | GPT-4o, Claude | Reflection = 6+ LLM calls per alert — cost efficiency is a real constraint |
| HNSW index over IVFFlat | IVFFlat (faster build, lower recall) | IVFFlat requires existing rows to build; HNSW works on empty tables at migration time |

## Challenges and Solutions

### Cross-Service Schema Consistency
**Problem**: Two backends (Java + Python) sharing one PostgreSQL database — who owns the schema?
**Solution**: Java + Flyway as the sole DDL owner. Python SQLAlchemy models mirror the schema for reads/writes but never run DDL. Hibernate `ddl-auto: validate` catches entity-vs-migration drift at startup, failing fast before data corruption.

### Agent Sycophancy in Reflection
**Problem**: The Analyzer tends to accept all Critic feedback uncritically, converging on whatever the Critic last suggested.
**Solution**: Prompt guardrail requiring a `response_to_critic` field — the Analyzer must explicitly accept or reject each Critic point with justification. This forces reasoning rather than capitulation.

### Memory Anchoring Bias
**Problem**: Historical incident context can anchor the Analyzer toward past diagnoses, even when the current situation has a different root cause.
**Solution**: Asymmetric information design — memory is visible *only* to the Analyzer and labeled "reference only". The Critic never sees it, so its challenges remain evidence-driven. The Analyzer must state why its diagnosis diverges from (or aligns with) history.

### Long-Running Workflows and SSE Reliability
**Problem**: Agent workflows take 30–60s. Direct SSE from Python couples execution to the HTTP connection lifecycle — if the connection drops, the work is lost.
**Solution**: Events go to Redis Streams (persistent, ordered). Java polls the stream and proxies via SSE with a 2-minute timeout. Clients can reconnect and resume from the last event ID without losing any steps.

## Demo Scenarios

Three end-to-end alert scenarios, each with simulated logs, metrics, seed runbooks, and command responses:

| Scenario | Category | Incident Chain |
|----------|----------|----------------|
| `mysql_pool_exhausted` | Database | Slow queries → connection starvation → cascading 503s |
| `cpu_high_load` | Compute | Thread contention → GC pressure → health check failure |
| `disk_space_critical` | Storage | WAL bloat + log growth → disk full → database crash |

## Project Structure

```
.
├── backend-java/           # Spring Boot API (Java 17)
│   ├── config/             # Security, Redis, CORS, JWT filter
│   ├── controller/         # Auth, Alert, Runbook, Stream (SSE)
│   ├── dto/                # Request/response records
│   ├── model/              # JPA entities with Flyway-aligned annotations
│   ├── service/            # Business logic + Python HTTP client
│   └── db/migration/       # Flyway V1–V3 (schema, embeddings, memory)
├── backend-python/         # FastAPI Agent Service (Python 3.11)
│   ├── agents/             # LangGraph nodes, graph wiring, reflection, memory
│   ├── cache/              # Redis diagnosis cache + sliding-window rate limiter
│   ├── db/                 # Async SQLAlchemy engine + models
│   ├── mcp_local/          # MCP tool adapters (log, metrics, knowledge, command)
│   ├── rag/                # Hybrid search: pgvector + tsvector + RRF
│   ├── streaming/          # SSE fallback endpoint
│   └── workers/            # Redis Stream event publisher
├── frontend/               # React 18 + TypeScript + Tailwind CSS
│   ├── pages/              # Login, Dashboard, AgentPanel, RunbookReview
│   ├── components/         # AlertCard, SSELogViewer
│   └── hooks/              # useSSE (typed EventSource hook)
├── data/                   # Simulated logs, metrics, runbooks, commands
├── scripts/                # Seed data, seed runbooks, seed incidents, RAG eval
└── docker-compose.yml      # PostgreSQL (pgvector), Redis, Java, Python
```

## Quick Start

```bash
# 1. Clone and configure
git clone <repo-url> && cd Runbook_agent
cp .env.example .env
# Edit .env — set OPENAI_API_KEY to a real key

# 2. Start infrastructure
docker-compose up -d postgres redis

# 3. Java API (Flyway migrations run automatically on startup)
cd backend-java && mvn spring-boot:run

# 4. Python agent service (separate terminal)
cd backend-python && pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 5. Seed demo data
docker-compose exec backend-python python scripts/seed_data.py
docker-compose exec backend-python python scripts/seed_runbooks.py
docker-compose exec backend-python python scripts/seed_incidents.py

# 6. Frontend (separate terminal)
cd frontend && npm install && npm run dev
# Open http://localhost:3000
```

## Status

This is a **demo-grade portfolio project**, not a production incident system. All remediation commands are simulated. The value is the end-to-end architecture: alert intake → multi-agent diagnosis → simulated remediation → runbook generation → human review, with live-streamed reasoning and learning from past incidents.
