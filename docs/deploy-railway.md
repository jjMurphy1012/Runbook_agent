# Deploying RunbookAgent on Railway

This walks through deploying the four runtime services on [railway.app](https://railway.app). Expect ~30 minutes total. Cost: free trial credit covers a few days; ~\$5–15/month after that depending on usage.

## Topology

```
GitHub repo ──▶ Railway project
                 ├── Postgres (with pgvector)   [private]
                 ├── Redis                      [private]
                 ├── backend-java   (public)    /api/*
                 ├── backend-python (private)   FastAPI
                 └── frontend       (public)    Vite static site
```

The Java backend is the only public ingress for API traffic. Python is reached only by Java over Railway's internal network. Frontend is its own static deploy that calls `backend-java` via the public URL configured at build time.

## 1. Create the project

1. Sign in at railway.app with GitHub.
2. **New Project → Deploy from GitHub repo** → pick `Runbook_agent`. Railway scans the repo and may auto-suggest services; ignore and add them manually.

## 2. Provision Postgres with pgvector

Railway's stock Postgres image does not include pgvector. Use one of:

### Option A — Postgres template with pgvector
- **+ New → Database → "Postgres + pgvector"** template if available in your Railway dashboard.

### Option B — Custom Docker service
- **+ New → Empty Service → Settings → Source → Docker Image** → `pgvector/pgvector:pg16`
- **Variables** tab: set `POSTGRES_DB=runbook_agent`, `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=<strong>`.
- **Volumes**: add a volume mounted at `/var/lib/postgresql/data` so data survives restarts.
- **Networking → Private Networking**: keep it private; do NOT expose a public port.

Note the service's internal name (e.g. `postgres`) — Java will reference it via `${{Postgres.PGHOST}}` style variable references.

## 3. Provision Redis

- **+ New → Database → Redis** (managed).
- Note the service name (e.g. `Redis`).

## 4. Deploy `backend-java`

- **+ New → GitHub Repo → Runbook_agent** (a second deploy from the same repo).
- **Settings → Source**:
  - Root Directory: `/`
  - Dockerfile path: `backend-java/Dockerfile`
- **Settings → Networking → Generate Domain** to make this service public.
- **Variables** (use Railway's reference syntax for cross-service values):

  ```
  POSTGRES_HOST=${{Postgres.PGHOST}}
  POSTGRES_PORT=${{Postgres.PGPORT}}
  POSTGRES_DB=${{Postgres.PGDATABASE}}
  POSTGRES_USER=${{Postgres.PGUSER}}
  POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
  REDIS_HOST=${{Redis.REDISHOST}}
  REDIS_PORT=${{Redis.REDISPORT}}
  PYTHON_SERVICE_URL=http://${{backend-python.RAILWAY_PRIVATE_DOMAIN}}:8000
  JWT_SECRET=<generate a 32+ char random string>
  APP_CORS_ORIGINS=https://<your-frontend-domain>.up.railway.app
  ```

  Substitute `Postgres` / `Redis` / `backend-python` with the actual service names Railway shows you.

  The CORS origin must match the frontend's Railway domain exactly; you can fill it in **after** step 6 once the frontend is deployed.

## 5. Deploy `backend-python`

- **+ New → GitHub Repo → Runbook_agent** (third deploy).
- **Settings → Source**:
  - Root Directory: `/`
  - Dockerfile path: `backend-python/Dockerfile`
- **Networking**: leave private — no public domain. Java reaches it on the internal network.
- **Variables**:

  ```
  POSTGRES_HOST=${{Postgres.PGHOST}}
  POSTGRES_PORT=${{Postgres.PGPORT}}
  POSTGRES_DB=${{Postgres.PGDATABASE}}
  POSTGRES_USER=${{Postgres.PGUSER}}
  POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
  REDIS_HOST=${{Redis.REDISHOST}}
  REDIS_PORT=${{Redis.REDISPORT}}
  OPENAI_API_KEY=sk-<your real key>
  LANGSMITH_TRACING=false
  ```

## 6. Deploy `frontend`

- **+ New → GitHub Repo → Runbook_agent** (fourth deploy).
- **Settings → Source**:
  - Root Directory: `frontend`
  - Build Command: `npm install && npm run build`
  - Start Command (for `vite preview`): `npm run preview -- --host 0.0.0.0 --port $PORT`
- Or set it up as a Railway **Static Site** pointing to `frontend/dist` after build.
- **Variables**:

  ```
  VITE_API_BASE_URL=https://<your-backend-java-domain>.up.railway.app
  ```

  Vite inlines `VITE_*` at build time, so this must be set **before** Railway runs the build.

- **Generate Domain** to make it public.
- Go back to `backend-java` variables and set `APP_CORS_ORIGINS` to this frontend domain (with `https://` prefix, no trailing slash). Redeploy `backend-java`.

## 7. Seed verified incidents (optional but recommended)

Memory retrieval is empty until you seed cold-start verified incidents:

```
railway run --service backend-python python scripts/seed_incidents.py
```

Run from your local machine after `railway login` and `railway link`.

## 8. Smoke test the deployment

From your local machine:

```
JAVA_URL=https://<your-backend-java-domain>.up.railway.app \
PY_URL=https://<not-applicable-private>      # smoke.sh tests python health locally,
                                              # skip that block or comment it out
bash scripts/smoke.sh
```

For Railway, Python is private. Either temporarily expose it for smoke or edit `smoke.sh` to skip the Python `/health` check (the create→trigger flow still exercises Python via Java).

## Environment variable cheat sheet

| Service | Variable | Source | Notes |
|---|---|---|---|
| backend-java | `POSTGRES_*` | `${{Postgres.PG*}}` | Auto-references |
| backend-java | `REDIS_*` | `${{Redis.REDIS*}}` | Auto-references |
| backend-java | `PYTHON_SERVICE_URL` | private DNS | `http://${{backend-python.RAILWAY_PRIVATE_DOMAIN}}:8000` |
| backend-java | `JWT_SECRET` | manual | 32+ random chars; rotate periodically |
| backend-java | `APP_CORS_ORIGINS` | manual | Frontend Railway domain, `https://` prefix |
| backend-python | `POSTGRES_*` / `REDIS_*` | references | Same as Java |
| backend-python | `OPENAI_API_KEY` | manual | Real key, never commit |
| frontend | `VITE_API_BASE_URL` | manual | backend-java public URL; build-time only |

## Known gotchas

- **pgvector**: Railway's stock Postgres template does **not** include the `vector` extension. Flyway V2 will fail on first boot with `ERROR: extension "vector" is not available`. Use the pgvector image (Option B above).
- **CORS mismatch**: any trailing slash or http/https mismatch in `APP_CORS_ORIGINS` will silently drop preflight requests.
- **VITE_* is build-time**: changing `VITE_API_BASE_URL` requires a full frontend redeploy, not just a restart.
- **SSE through Railway proxy**: long-lived connections are fine but check Railway's proxy timeout (currently ~10min); on disconnect the frontend reconnects via `useSSE` cleanup logic.
- **Free trial credit**: Railway gives a few dollars of trial credit. Postgres + Redis + 3 services + bandwidth typically exhaust it in 5–10 days; budget around \$5–15/month once trial ends.
