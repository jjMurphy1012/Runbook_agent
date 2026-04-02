# RunbookAgent

RunbookAgent is a scaffold for an AI-powered AIOps platform that processes alerts through a multi-agent pipeline and turns incident resolutions into reusable runbooks. The repository is organized around three services:

- `backend-java/`: Spring Boot API for auth, alert CRUD, session management, and stream proxying
- `backend-python/`: FastAPI service for agent orchestration, RAG, MCP tools, and SSE streaming
- `frontend/`: React + TypeScript dashboard for alerts, live agent traces, and runbook review

## Current Scope

This initial commit sets up the project structure, service entry points, configuration placeholders, and sample data directories. It is a scaffold intended to accelerate development, not a finished production system.

## Architecture

```text
Frontend (React + TypeScript) -> Spring Boot API -> FastAPI Agent Service
                                      |                    |
                                      v                    v
                                   Redis             PostgreSQL + pgvector
```

Planned agent flow:

1. Triage classifies the alert and checks cache.
2. Diagnostic queries logs, metrics, and runbooks.
3. Remediation proposes or simulates recovery actions.
4. Postmortem creates or updates a runbook for review.

For the first milestone, all coordination stays inside LangGraph. A2A (Agent-to-Agent) is intentionally deferred until the baseline workflow is stable.

## Repository Layout

```text
.
├── backend-java/
├── backend-python/
├── frontend/
├── scripts/
├── data/
├── docker-compose.yml
├── AGENTS.md
└── CLAUDE.md
```

## Local Development

1. Copy `.env.example` to `.env` and fill in secrets.
2. Start infrastructure with `docker-compose up -d postgres redis`.
3. Run the Java API: `cd backend-java && mvn spring-boot:run`
4. Run the agent service: `cd backend-python && uvicorn main:app --reload --port 8000`
5. Run the frontend: `cd frontend && npm install && npm run dev`

To bring up all services via containers, use:

```bash
docker-compose up --build
```

## Next Milestones

- Implement database schema and migrations
- Add LangGraph orchestration and MCP tools
- Wire Redis Streams and SSE end to end
- Build alert dashboard and runbook review workflow
- Add integration tests and seeded demo scenarios

## A2A Adoption Gate

A2A should be evaluated only after the LangGraph baseline is working. The point to explicitly prompt for an A2A spike is when all of the following are true:

- The LangGraph pipeline runs end to end for at least 3 alert scenarios
- Redis Streams and SSE show stable step-by-step agent traces
- At least one integration test covers `alert -> diagnosis -> postmortem -> runbook draft`
- Agent boundaries are clear enough to split into separate contracts, such as diagnostic specialist, remediation specialist, and runbook reviewer

When these conditions are met, open an A2A experiment branch and compare two designs:

- current single-service LangGraph orchestration
- A2A handoff between specialized agents with explicit message contracts

Until then, keep the architecture simpler and finish the LangGraph baseline first.
