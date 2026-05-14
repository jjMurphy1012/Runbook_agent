from sqlalchemy import text

from db.database import get_session


async def bm25_search(query: str, top_k: int = 5) -> list[dict]:
    """Full-text search using the persisted tsvector column + GIN index."""
    sql = text("""
        SELECT re.id, re.runbook_id, re.chunk_text,
               ts_rank(re.search_vector,
                       plainto_tsquery('english', :query)) AS score
        FROM runbook_embeddings re
        WHERE re.search_vector @@ plainto_tsquery('english', :query)
        ORDER BY score DESC
        LIMIT :top_k
    """)
    async with get_session() as session:
        result = await session.execute(sql, {"query": query, "top_k": top_k})
        rows = result.all()
    return [
        {
            "id": str(row.id),
            "runbook_id": str(row.runbook_id),
            "chunk_text": row.chunk_text,
            "score": float(row.score),
            "strategy": "bm25",
        }
        for row in rows
    ]
