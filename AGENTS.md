# Repository Guidelines

## Project Structure & Module Organization

This repository is planned as a three-service application plus shared data. Keep Spring Boot code in `backend-java/`, FastAPI and LangGraph code in `backend-python/`, and the React UI in `frontend/`. Put seed and evaluation utilities in `scripts/`, and keep simulated fixtures under `data/` (`simulated_logs/`, `simulated_metrics/`, `seed_runbooks/`, `commands/`). In Java, preserve `controller/`, `service/`, `repository/`, and `model/` separation. In Python, group by domain (`agents/`, `mcp_local/`, `rag/`, `streaming/`, `cache/`, `workers/`, `db/`). The directory is named `mcp_local/` (not `mcp/`) to avoid shadowing the external `mcp` PyPI package if it is later added as a dependency.

## Build, Test, and Development Commands

Use `docker compose up -d` to start the full local stack. Run Java tests with `cd backend-java && mvn test` (requires Docker daemon for Testcontainers). Run Python tests with `docker compose exec backend-python pytest -v`. Run frontend tests with `cd frontend && npm test`. Seed demo data with `docker-compose exec backend-python python scripts/seed_data.py`, `docker-compose exec backend-python python scripts/seed_runbooks.py`, and `docker-compose exec backend-python python scripts/seed_incidents.py`. Check retrieval quality with `docker-compose exec backend-python python scripts/test_rag.py`. Start the frontend locally with `cd frontend && npm run dev`.

## Coding Style & Naming Conventions

Use 4 spaces in Java and Python. Keep TypeScript formatting aligned with the project formatter once added. Java packages should stay under `com.runbookagent`, with `PascalCase` classes and `camelCase` members. React components use `PascalCase.tsx`; hooks use `useX.ts`; Python modules use `snake_case.py`. Prefer explicit DTOs, typed request/response models, and small service classes with one clear responsibility.

## Testing Guidelines

Name Java tests `*Test.java`, Python tests `test_*.py`, and frontend tests `*.test.tsx`. Add tests for service logic, MCP tools, RAG ranking changes, and any alert-state transitions. Changes to retrieval weights, prompts, or Redis stream consumers should include at least one regression test or evaluation note.

## Commit & Pull Request Guidelines

Use Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`). PRs should describe the affected service, list setup or env changes, link the issue when available, and include screenshots for dashboard or SSE updates.

## Architecture & Redis

Agent orchestration uses LangGraph StateGraph inside `backend-python/`. All agents (triage, diagnostic, remediation, postmortem) run as graph nodes with shared state flowing through edges.

A2A is deferred until the LangGraph baseline is stable. Contributors should not introduce an A2A layer until the repo has an end-to-end LangGraph flow for at least 3 alert scenarios, stable Redis Stream to SSE tracing, and one passing integration path from alert intake to runbook draft.

Redis is a core infrastructure dependency, not an optional add-on. It serves three roles:

1. **Diagnosis Cache** (`cache/diagnosis_cache.py`): caches LLM results by alert fingerprint to avoid redundant agent runs
2. **Rate Limiter** (`cache/rate_limiter.py`): sliding-window limiter on LLM API calls to control cost
3. **Redis Streams** (`workers/stream_consumer.py`): event bus between Python agent service and Java API layer — agent publishes step events to a stream, Java consumes and proxies to frontend via SSE

Redis is NOT used for session storage. API auth is stateless JWT — no Spring Session dependency.

When contributing, document any new Redis key pattern in the PR that introduces it. See `CLAUDE.md` for detailed key patterns and the full Redis strategy.

## Agent Workflow Notes

When the Codex context window indicator drops to roughly 30%, compact the conversation context before continuing. Preserve the current goal, decisions already made, files changed, open bugs, validation results, and the next concrete steps so the next turn can resume without re-discovery.

## Security & Configuration Tips

Never commit `.env`, OpenAI keys, JWT secrets, or LangSmith credentials. Keep command execution simulated; do not introduce unrestricted shell execution into the agent tool layer. Document every new Redis key, database table, and MCP tool in the same PR that adds it.
