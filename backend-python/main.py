from fastapi import FastAPI

from agents.graph import run_alert_workflow
from config import settings
from streaming.sse import router as sse_router

app = FastAPI(title="RunbookAgent Python Service", version="0.1.0")
app.include_router(sse_router)


@app.get("/health")
async def health() -> dict[str, str | int]:
    return {
        "status": "ok",
        "service": "backend-python",
        "port": settings.fastapi_port,
    }


@app.post("/agent/run")
async def run_agent(alert: dict) -> dict:
    return await run_alert_workflow(alert)
