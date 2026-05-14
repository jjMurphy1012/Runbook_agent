"""Reciprocal Rank Fusion correctness."""

from rag.reranker import reciprocal_rank_fusion


def test_single_list_preserves_order():
    fused = reciprocal_rank_fusion([[{"id": "a"}, {"id": "b"}, {"id": "c"}]])
    assert [d["id"] for d in fused] == ["a", "b", "c"]
    # rank 0 in single list: 1/(60+1) = 0.0163...
    assert fused[0]["rrf_score"] > fused[1]["rrf_score"] > fused[2]["rrf_score"]


def test_documents_appearing_in_both_lists_rank_higher():
    vector = [{"id": "shared"}, {"id": "v_only"}]
    bm25 = [{"id": "b_only"}, {"id": "shared"}]
    fused = reciprocal_rank_fusion([vector, bm25])
    assert fused[0]["id"] == "shared"  # only doc in both lists


def test_rrf_score_formula():
    # rank 0 in both lists -> 2 * 1/(60+1) = 0.0327...
    fused = reciprocal_rank_fusion([[{"id": "x"}], [{"id": "x"}]], k=60)
    assert fused[0]["rrf_score"] == 2 / 61
    assert fused[0]["strategy"] == "hybrid"


def test_empty_input():
    assert reciprocal_rank_fusion([]) == []
    assert reciprocal_rank_fusion([[], []]) == []
