"""Seed runbooks and their embeddings into the database.

Usage: docker-compose exec backend-python python scripts/seed_runbooks.py
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend-python"))

from db.database import get_session
from db.models import Runbook, RunbookEmbedding
from rag.embeddings import embed_texts

SEED_RUNBOOKS_DIR = Path(__file__).resolve().parents[1] / "data" / "seed_runbooks"


async def main() -> None:
    runbook_files = list(SEED_RUNBOOKS_DIR.glob("*.md"))
    if not runbook_files:
        print("No seed runbooks found in data/seed_runbooks/")
        return

    # Read all runbook files
    runbooks_data: list[dict] = []
    for f in runbook_files:
        content = f.read_text()
        title = content.split("\n")[0].lstrip("# ").strip()
        runbooks_data.append({
            "title": title,
            "content": content,
            "filename": f.stem,
        })

    # Generate embeddings for all runbook contents
    texts = [r["content"] for r in runbooks_data]
    try:
        embeddings = await embed_texts(texts)
    except Exception as e:
        print(f"Embedding generation failed (API key may be placeholder): {e}")
        print("Seeding runbooks without embeddings.")
        embeddings = [None] * len(texts)

    async with get_session() as session:
        for i, data in enumerate(runbooks_data):
            runbook_id = uuid.uuid4()
            runbook = Runbook(
                id=runbook_id,
                title=data["title"],
                content=data["content"],
                root_cause=None,
                version=1,
                status="APPROVED",
                updated_at=datetime.now(timezone.utc),
            )
            session.add(runbook)

            if embeddings[i] is not None:
                embedding_record = RunbookEmbedding(
                    id=uuid.uuid4(),
                    runbook_id=runbook_id,
                    chunk_text=data["content"],
                    embedding=embeddings[i],
                    created_at=datetime.now(timezone.utc),
                )
                session.add(embedding_record)

    print(f"Seeded {len(runbooks_data)} runbooks with embeddings.")


if __name__ == "__main__":
    asyncio.run(main())
