import asyncio

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/agent", tags=["stream"])


@router.get("/stream/{alert_id}")
async def stream_alert(alert_id: str) -> EventSourceResponse:
    async def event_generator():
        steps = ["Triage", "Diagnostic", "Remediation", "Postmortem", "Complete"]
        for step in steps:
            yield {"event": "message", "data": f"[{step}] alert={alert_id}"}
            await asyncio.sleep(0.1)

    return EventSourceResponse(event_generator())
