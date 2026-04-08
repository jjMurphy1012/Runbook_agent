from rag.hybrid import hybrid_search


async def search_runbooks(query: str, top_k: int = 3) -> dict:
    """Search runbook knowledge base using hybrid RAG (pgvector + tsvector + RRF)."""
    try:
        results = await hybrid_search(query, top_k=top_k)
        return {
            "tool": "knowledge_search",
            "query": query,
            "matches": results,
        }
    except Exception as e:
        return {
            "tool": "knowledge_search",
            "query": query,
            "matches": [],
            "error": str(e),
        }
