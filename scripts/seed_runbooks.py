"""Seed runbooks and their embeddings into the database.

Idempotent: re-running skips runbooks whose title already exists.
Usage: docker-compose exec backend-python python scripts/seed_runbooks.py
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
for _candidate in (_root / "backend-python", _root):
    if (_candidate / "db").is_dir():
        sys.path.insert(0, str(_candidate))
        break

from sqlalchemy import select

from db.database import get_session
from db.models import Runbook, RunbookEmbedding
from rag.embeddings import embed_texts

SEED_RUNBOOKS_DIR = Path(__file__).resolve().parents[1] / "data" / "seed_runbooks"


async def main() -> None:
    runbook_files = list(SEED_RUNBOOKS_DIR.glob("*.md"))
    if not runbook_files:
        print("No seed runbooks found in data/seed_runbooks/")
        return

    runbooks_data: list[dict] = []
    for f in runbook_files:
        content = f.read_text()
        title = content.split("\n")[0].lstrip("# ").strip()
        runbooks_data.append({"title": title, "content": content})

    async with get_session() as session:
        existing_titles = set((await session.scalars(
            select(Runbook.title)
        )).all())
        to_insert = [r for r in runbooks_data if r["title"] not in existing_titles]
        skipped = len(runbooks_data) - len(to_insert)

        if not to_insert:
            print(f"Seeded runbooks: inserted=0 skipped={skipped}")
            return

        texts = [r["content"] for r in to_insert]
        try:
            embeddings = await embed_texts(texts)
        except Exception as e:
            print(f"Embedding generation failed (API key may be placeholder): {e}")
            print("Seeding runbooks without embeddings.")
            embeddings = [None] * len(texts)

        for i, data in enumerate(to_insert):
            runbook_id = uuid.uuid4()
            session.add(Runbook(
                id=runbook_id,
                title=data["title"],
                content=data["content"],
                root_cause=None,
                version=1,
                status="APPROVED",
                updated_at=datetime.now(timezone.utc),
            ))
            if embeddings[i] is not None:
                session.add(RunbookEmbedding(
                    id=uuid.uuid4(),
                    runbook_id=runbook_id,
                    chunk_text=data["content"],
                    embedding=embeddings[i],
                    created_at=datetime.now(timezone.utc),
                ))

    print(f"Seeded runbooks: inserted={len(to_insert)} skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(main())
