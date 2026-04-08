import json
import logging

logger = logging.getLogger(__name__)


def parse_llm_json(text: str, fallback: dict | None = None) -> dict:
    """Parse JSON from LLM response, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse LLM JSON: %.200s", text)
        return fallback or {}


async def emit_event(state: dict, stage: str, data: dict) -> None:
    """Publish a stage event to Redis Stream if alert_id is present."""
    alert_id = state.get("alert_id")
    if not alert_id:
        return
    try:
        from workers.stream_consumer import publish_agent_event
        await publish_agent_event(alert_id, stage, data)
    except Exception:
        logger.debug("Stream publish failed for %s/%s", alert_id, stage)
