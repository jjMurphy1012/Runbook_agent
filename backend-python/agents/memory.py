import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text

from agents.state import AgentState
from db.database import get_session
from db.models import IncidentHistory
from rag.embeddings import embed_text


async def read_similar_incidents(
    alert_payload: dict, top_k: int = 3
) -> list[dict]:
    """Retrieve top-k semantically similar past incidents (verified only)."""
    try:
        payload_text = json.dumps(alert_payload, sort_keys=True)
        embedding = await embed_text(payload_text)
    except Exception:
        return []

    embedding_literal = f"[{','.join(str(x) for x in embedding)}]"
    stmt = (
        select(
            IncidentHistory.id,
            IncidentHistory.rule_name,
            IncidentHistory.category,
            IncidentHistory.severity,
            IncidentHistory.diagnosis,
            IncidentHistory.root_cause,
            IncidentHistory.outcome,
            text(
                f"1 - (embedding <=> '{embedding_literal}'::vector) AS similarity"
            ),
        )
        .where(IncidentHistory.human_verified.is_(True))
        .order_by(text(f"embedding <=> '{embedding_literal}'::vector"))
        .limit(top_k)
    )
    try:
        async with get_session() as session:
            result = await session.execute(stmt)
            rows = result.all()
    except Exception:
        return []

    return [
        {
            "id": str(row.id),
            "rule_name": row.rule_name,
            "category": row.category,
            "severity": row.severity,
            "diagnosis": row.diagnosis,
            "root_cause": row.root_cause,
            "outcome": row.outcome,
            "similarity": float(row.similarity),
        }
        for row in rows
    ]


async def memory_read_node(state: AgentState) -> dict:
    """Inject historical incidents before the first Analyzer round."""
    alert = state["alert"]
    incidents = await read_similar_incidents(alert, top_k=3)
    return {"similar_incidents": incidents}


async def write_incident(
    alert: dict,
    fingerprint: str,
    diagnosis: str,
    root_cause: str,
    runbook_id: str | None = None,
    outcome: str = "unknown",
) -> None:
    """Write a new incident to history after Postmortem completes."""
    try:
        payload_text = json.dumps(alert, sort_keys=True)
        embedding = await embed_text(payload_text)
    except Exception:
        embedding = None

    record = IncidentHistory(
        id=uuid.uuid4(),
        alert_fingerprint=fingerprint,
        rule_name=alert.get("rule_name", ""),
        category=alert.get("category", ""),
        severity=alert.get("severity", "MEDIUM"),
        alert_payload=alert,
        diagnosis=diagnosis,
        root_cause=root_cause,
        runbook_id=uuid.UUID(runbook_id) if runbook_id else None,
        outcome=outcome,
        human_verified=False,
        embedding=embedding,
        created_at=datetime.now(timezone.utc),
    )
    async with get_session() as session:
        session.add(record)
