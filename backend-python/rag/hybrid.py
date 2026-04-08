import asyncio

from rag.bm25_search import bm25_search
from rag.embeddings import embed_text
from rag.reranker import reciprocal_rank_fusion
from rag.vector_search import vector_search


async def hybrid_search(query: str, top_k: int = 5) -> list[dict]:
    """Run pgvector + tsvector searches concurrently, fuse with RRF."""
    query_embedding = await embed_text(query)

    vector_results, bm25_results = await asyncio.gather(
        vector_search(query_embedding, top_k=top_k * 2),
        bm25_search(query, top_k=top_k * 2),
    )

    fused = reciprocal_rank_fusion([vector_results, bm25_results])
    return fused[:top_k]
