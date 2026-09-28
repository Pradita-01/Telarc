from app.retrieval.reranker import Reranker


def test_reranker_returns_top_k():
    reranker = Reranker()

    results = [
        {
            "chunk_id": "1",
            "text": "Airtel has a large 5G customer base.",
            "document": "airtel.pdf",
            "page": 9,
            "score": 0.8,
        },
        {
            "chunk_id": "2",
            "text": "The company operates several data centres.",
            "document": "airtel.pdf",
            "page": 20,
            "score": 0.7,
        },
        {
            "chunk_id": "3",
            "text": "Airtel expanded its 5G network significantly.",
            "document": "airtel.pdf",
            "page": 10,
            "score": 0.75,
        },
    ]

    reranked = reranker.rerank(
        "What is Airtel's 5G customer base?",
        results,
        top_k=2,
    )

    assert len(reranked) == 2
    assert "rerank_score" in reranked[0]
    assert reranked[0]["rerank_score"] >= reranked[1]["rerank_score"]


def test_reranker_handles_empty_results():
    reranker = Reranker()

    assert reranker.rerank(
        "test question",
        [],
        top_k=5,
    ) == []