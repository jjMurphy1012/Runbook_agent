import uuid

from sqlalchemy import select, text

from db.database import get_session
from db.models import RunbookEmbedding


async def vector_search(
    query_embedding: list[float], top_k: int = 5
) -> list[dict]:
    embedding_literal = f"[{','.join(str(x) for x in query_embedding)}]"
    stmt = (
        select(
            RunbookEmbedding.id,
            RunbookEmbedding.runbook_id,
            RunbookEmbedding.chunk_text,
            text(
                f"1 - (embedding <=> '{embedding_literal}'::vector) AS similarity"
            ),
        )
        .order_by(text(f"embedding <=> '{embedding_literal}'::vector"))
        .limit(top_k)
    )
    async with get_session() as session:
        result = await session.execute(stmt)
        rows = result.all()
    return [
        {
            "id": str(row.id),
            "runbook_id": str(row.runbook_id),
            "chunk_text": row.chunk_text,
            "score": float(row.similarity),
            "strategy": "vector",
        }
        for row in rows
    ]
