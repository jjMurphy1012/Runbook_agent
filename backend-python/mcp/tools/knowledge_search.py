async def search_runbooks(query: str, mode: str = "diagnostic") -> dict:
    return {"tool": "knowledge_search", "query": query, "mode": mode, "matches": []}
