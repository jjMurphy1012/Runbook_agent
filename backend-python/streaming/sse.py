import asyncio
import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from workers.stream_consumer import read_events

router = APIRouter(prefix="/agent", tags=["stream"])


@router.get("/stream/{alert_id}")
async def stream_alert(alert_id: str) -> EventSourceResponse:
    """SSE endpoint that reads from the Redis Stream for a given alert.

    This is the Python-side fallback SSE endpoint. The primary path is
    Java consuming the stream and proxying via its own SSE controller.
    """

    async def event_generator():
        last_id = "0-0"
        idle_count = 0
        max_idle = 60  # Stop after 60 idle polls (~2 min)

        while idle_count < max_idle:
            events = await read_events(alert_id, last_id=last_id, count=20)
            if events:
                idle_count = 0
                for event in events:
                    last_id = event["id"]
                    yield {
                        "event": event["stage"],
                        "data": json.dumps(event["data"]),
                    }
                    # Check for terminal event
                    if event["stage"] == "complete":
                        return
            else:
                idle_count += 1
                await asyncio.sleep(0.5)

        yield {"event": "timeout", "data": "Stream idle timeout reached"}

    return EventSourceResponse(event_generator())
