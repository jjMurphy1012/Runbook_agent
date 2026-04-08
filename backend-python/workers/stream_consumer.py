import json

from cache import redis_client


async def publish_agent_event(
    alert_id: str, stage: str, data: dict
) -> None:
    """Publish an agent step event to the Redis Stream for this alert.

    Java consumes from this stream and proxies to frontend via SSE.
    Stream key pattern: alerts:{alert_id}:events
    """
    stream_key = f"alerts:{alert_id}:events"
    event = {
        "stage": stage,
        "data": json.dumps(data),
    }
    await redis_client.xadd(stream_key, event, maxlen=500)


async def read_events(
    alert_id: str, last_id: str = "0-0", count: int = 50
) -> list[dict]:
    """Read events from a Redis Stream (used by Python SSE fallback)."""
    stream_key = f"alerts:{alert_id}:events"
    entries = await redis_client.xread(
        {stream_key: last_id}, count=count, block=2000
    )
    results = []
    for _stream, messages in entries:
        for msg_id, fields in messages:
            results.append({
                "id": msg_id,
                "stage": fields.get("stage", ""),
                "data": json.loads(fields.get("data", "{}")),
            })
    return results
