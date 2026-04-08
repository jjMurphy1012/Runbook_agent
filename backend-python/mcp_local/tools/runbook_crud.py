import uuid
from datetime import datetime, timezone

from db.database import get_session
from db.models import Runbook


async def upsert_runbook(
    title: str,
    content: str,
    root_cause: str | None = None,
    runbook_id: str | None = None,
) -> dict:
    """Create or update a runbook in the database."""
    async with get_session() as session:
        if runbook_id:
            runbook = await session.get(Runbook, uuid.UUID(runbook_id))
            if runbook:
                runbook.title = title
                runbook.content = content
                runbook.root_cause = root_cause
                runbook.version += 1
                runbook.updated_at = datetime.now(timezone.utc)
                return {
                    "tool": "runbook_crud",
                    "action": "updated",
                    "runbook_id": str(runbook.id),
                    "version": runbook.version,
                }

        runbook = Runbook(
            id=uuid.uuid4(),
            title=title,
            content=content,
            root_cause=root_cause,
            status="DRAFT",
            version=1,
            updated_at=datetime.now(timezone.utc),
        )
        session.add(runbook)
        return {
            "tool": "runbook_crud",
            "action": "created",
            "runbook_id": str(runbook.id),
            "version": 1,
        }


async def get_runbook(runbook_id: str) -> dict | None:
    """Read a runbook by ID."""
    async with get_session() as session:
        runbook = await session.get(Runbook, uuid.UUID(runbook_id))
        if not runbook:
            return None
        return {
            "id": str(runbook.id),
            "title": runbook.title,
            "content": runbook.content,
            "root_cause": runbook.root_cause,
            "status": runbook.status,
            "version": runbook.version,
        }
