def reciprocal_rank_fusion(
    result_lists: list[list[dict]], k: int = 60
) -> list[dict]:
    """Reciprocal Rank Fusion (RRF) to combine multiple ranked lists.

    RRF score = sum over lists of 1 / (k + rank_in_list).
    """
    scores: dict[str, float] = {}
    docs: dict[str, dict] = {}

    for result_list in result_lists:
        for rank, doc in enumerate(result_list):
            doc_id = doc["id"]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
            if doc_id not in docs:
                docs[doc_id] = doc

    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    return [
        {**docs[doc_id], "rrf_score": scores[doc_id], "strategy": "hybrid"}
        for doc_id in sorted_ids
    ]
