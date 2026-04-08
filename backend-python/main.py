import os

from fastapi import FastAPI

from agents.graph import run_alert_workflow
from config import settings
from streaming.sse import router as sse_router

# LangSmith reads LANGCHAIN_TRACING_V2 / LANGCHAIN_API_KEY from the process env.
# We only export these when a real lsv2_ key is configured; otherwise tracing
# stays off regardless of what .env says.
if settings.langsmith_enabled:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
else:
    os.environ.pop("LANGCHAIN_TRACING_V2", None)
    os.environ.pop("LANGCHAIN_API_KEY", None)

app = FastAPI(title="RunbookAgent Python Service", version="0.1.0")
app.include_router(sse_router)


@app.get("/health")
async def health() -> dict[str, str | int | bool]:
    return {
        "status": "ok",
        "service": "backend-python",
        "port": settings.fastapi_port,
        "langsmith_enabled": settings.langsmith_enabled,
    }


@app.post("/agent/run")
async def run_agent(alert: dict) -> dict:
    """Trigger the full agent workflow for an alert.

    Called by Java backend via sync HTTP. Agent publishes step events
    to Redis Stream asynchronously during execution.
    """
    return await run_alert_workflow(alert)
