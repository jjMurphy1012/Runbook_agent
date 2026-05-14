# RunbookAgent Plan

> Source of truth for project-level progress. Read at session start and update when finishing a stage.
> Last updated: 2026-05-14 (P0 + P1 + P2 + P3 done. Verified: smoke ALL PASS, Java 7/7, Python 11/11, Frontend 11/11, Flyway V5 applied, healthchecks gating depends_on.)

## Current state (audited)

Main pipeline is wired end-to-end in code, but local verification has gaps: frontend build is broken, Java test harness depends on a dev Postgres role that doesn't exist, Docker daemon isn't running, and several efficiency/security follow-ups (rate limiter not invoked, SSE permitAll, non-persistent tsvector, non-idempotent seeds) are still open.

### Verifications I ran

- ✅ `mvn -q -DskipTests compile` — pass
- ✅ `python3 -m compileall backend-python scripts` — pass
- ❌ `npm run build` — `tsconfig.node.json` missing Node/ES lib config; `package.json` missing `@types/node`
- ❌ `mvn -q test` — Spring context test fails on `role "postgres" does not exist`
- ⚠️ `python3 -m pytest backend-python/tests -q` — pytest not installed locally; not executed
- ❌ `docker compose ps` — Docker daemon unreachable

## Stage 1 — Core wiring ✅ (in code)

- [x] Java AlertService: create / labels / fingerprint / trigger Python workflow / status update / Runbook approval (`backend-java/src/main/java/com/runbookagent/service/AlertService.java:57`)
- [x] Python LangGraph: triage → evidence → diagnostic / reflection → remediation → postmortem (`backend-python/agents/graph.py:28`)
- [x] Fingerprint unified (Java/Python both hash `rule_name + sorted labels`; parity test passes)
- [x] Redis Streams event publish + Java SSE forward
- [x] RAG hybrid search (BM25 + vector), but BM25 is query-time `to_tsvector(...)` — see Stage 6
- [x] Seed scripts run but **not idempotent** — every run inserts new UUIDs (`scripts/seed_data.py:46`)

## P0 (block real demo)

- [x] **Fix frontend build** — `tsconfig.node.json` got `target`/`lib`/`skipLibCheck`/`types`; `@types/node` added. `npm run build` ✅
- [x] **Local runtime** — Docker Desktop up; `docker compose up -d` all four containers healthy
- [x] **End-to-end smoke** — `scripts/smoke.sh` ran ALL PASS: register/login/create/trigger/SSE/RESOLVED. Real LLM (gpt model) drove triage → reflection → postmortem. Fingerprint at runtime matched parity test (`d596a9b8951d249f6a59167d61135183`).
- [x] **Java test isolation** — `RunbookAgentApplicationTests` uses pgvector Testcontainer + redis:7-alpine GenericContainer. `mvn test` ✅ (4/4 tests, Flyway V1–V4 applied in container).

## P1 (security + correctness)

- [x] Wire `rate_limiter.allow_request()` in front of all LLM calls — added `agents/llm.py:llm_invoke()` wrapper; replaced 8 `_llm.ainvoke()` sites in triage / diagnostic / reflection (analyzer+critic+finalizer) / remediation / postmortem. Backs off 1s and retries up to 60s, then raises `LLMRateLimitExceeded`. Smoke re-run still ALL PASS (and incidentally verified triage cache-hit branch — second run hit `cache_hit: true`).
- [x] Replace SSE `permitAll` with a short-lived stream token. `POST /api/stream/token/{alertId}` (JWT-protected) issues a 5-minute token bound to the alertId via an `aid` claim. `GET /api/stream/{alertId}?token=...` validates the token before opening the SSE. SecurityConfig now allows only `GET /api/stream/*`; the token POST falls into `anyRequest().authenticated()`. Frontend `AgentPanel` fetches the stream token then builds the EventSource URL. Smoke still ALL PASS. Per-connection thread/polling rewrite still deferred — separate work.
- [x] Make seed scripts idempotent — `seed_data` skips on existing fingerprint; `seed_runbooks` skips on existing title; `seed_incidents` skips on existing `root_cause` (fingerprint not unique for two mysql seeds). Verified twice in container: first run inserted=3/4/4, second run skipped=3/4/4. Also fixed sys.path so scripts work both in container (`/app/agents`) and on host (`<repo>/backend-python/agents`).
- [x] Minimal test set — Java AlertService (fingerprint + null labels) + RunbookService (approve flips human_verified via native query). Python fingerprint parity (4 cases, hashes match Java FingerprintUtilParityTest), triage cache-hit branch (flattened diagnosis + cache-miss falls through to llm_invoke), RAG fusion (single list order, intersection ranks higher, formula, empty input). Java 7/7 pass; Python 11/11 pass. Frontend test infra not yet set up; deferred as separate task.

## P1 deferred (now done)

- [x] Frontend test set — installed vitest + @testing-library/react + jsdom + user-event. Wrote LoginPage (submit / error / register toggle), DashboardPage (render alerts / empty on error / Run Agent triggers + selects), and useSSE hook (null url skip, open + stage event accumulation, complete closes, error closes, unmount closes). `npm test` 11/11 pass.

## P2 (perf + housekeeping)

- [x] Persist tsvector column + GIN index — Flyway V5 adds `search_vector` as a `GENERATED ALWAYS ... STORED` tsvector column on `runbook_embeddings`, plus a GIN index. `bm25_search.py` now queries the persisted column instead of computing `to_tsvector` per row at query time.
- [x] Docker healthchecks + drop obsolete `version` field — every service has a healthcheck (`pg_isready`, `redis-cli ping`, `/api/auth/health`, `/health`). `depends_on` now uses `condition: service_healthy` so backends only start after infra is ready.
- [x] AGENTS.md `./mvnw` reference removed; clarified that `mvn test` requires Docker daemon for Testcontainers. README had no `mvnw` references.

## P3 cleanup

- [x] `dashboard-screenshot.png` moved from repo root to `docs/assets/dashboard.png` so the UI screenshot is kept as a demo asset without cluttering the project root.
- [x] `.gitignore` extended for frontend tsc/composite-mode outputs (`*.tsbuildinfo`, `vite.config.{d.ts,js}`) so they stop showing up in `git status`.

## Stages 2–5 status snapshot

- Stage 2 Retrieval ✅ core; tsvector persistence deferred (P2)
- Stage 3 Agent workflow ✅ code complete; LLM-dependent smoke blocked on OPENAI_API_KEY
- Stage 4 Streaming ✅ open path verified (SSE no-auth received `alert_created`)
- Stage 5 Product layer ✅ auth + CRUD + dashboard scaffold; runbook review polish pending
- Stage 6 Evaluation — not started (RAG eval script, latency probe, LangSmith traces)

## Recommended execution order

1. Fix frontend build (pure code, no infra dependency)
2. Restore Docker / Postgres / Redis (needs user to start Docker Desktop)
3. Add Java test profile / Testcontainers so `mvn test` works without dev Postgres
4. Write smoke script and run real end-to-end loop
5. P1 security + minimal test set
6. P2 perf + housekeeping

## Decisions log

- 2026-05-14: Diagnostic uses Reflection (Analyzer/Critic loop), not bull/bear — `docs/design/reflection.md`
- 2026-05-14: Auth is stateless JWT; `spring-session-data-redis` removed — `docs/design/auth.md`
- 2026-05-14: Fingerprint canonical form `rule_name + "|" + json(sorted labels, no whitespace)`, SHA-256, first 32 hex. Single-sourced in `FingerprintUtil.java` ↔ `agents/fingerprint.py`. Never change one side without the other — used as Redis cache key and join key against `incident_history`.
- 2026-05-14: SSE `/api/stream/**` is `permitAll` because EventSource cannot send `Authorization`. Marked for replacement by short-lived stream token (P1).
- 2026-05-14: Incident Memory retrieval filters by `human_verified=true` only.

## Known blockers

- **Docker daemon not running** — blocks every infra-dependent verification. User action required: open Docker Desktop.
- **`OPENAI_API_KEY` is `sk-placeholder`** — blocks LLM-dependent smoke (triage / reflection / memory write). Workarounds: real key, mock LLM, or defer LLM-dependent checks.
- **Dev-machine Postgres** has no `postgres` role — blocks `mvn test` until P0 #21 (test isolation) lands or user creates the role locally.

## How to use this file

- **At session start**: Read this file first. Trust it over inferring from git log.
- **When picking a task**: Mirror unchecked P0/P1/P2 items into `TaskCreate` for in-session tracking.
- **When finishing a stage**: Flip checkboxes, append to Decisions log if a non-obvious choice was made, update `Last updated`, then commit.
- **When hitting a new blocker**: Add to Known blockers with workaround options.
