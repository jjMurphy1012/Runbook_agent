from rag.bm25_search import bm25_search
from rag.vector_search import vector_search


def hybrid_search(query: str, query_embedding: list[float]) -> dict:
    return {
        "query": query,
        "vector": vector_search(query_embedding),
        "bm25": bm25_search(query),
    }
