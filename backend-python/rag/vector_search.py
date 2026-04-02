def vector_search(query_embedding: list[float]) -> list[dict]:
    return [{"strategy": "vector", "score": 0.0, "payload": {}}]
