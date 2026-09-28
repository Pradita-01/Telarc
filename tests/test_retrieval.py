from pathlib import Path

from app.retrieval.vector_store import VectorStore


INDEX_DIR = Path("data/indexes")


def load_store():
    store = VectorStore()
    store.load(INDEX_DIR)
    return store


def test_index_loads():
    store = load_store()

    assert store.index is not None
    assert store.index.ntotal == len(store.chunks)
    assert store.index.ntotal > 0


def test_index_and_metadata_match():
    store = load_store()

    assert store.index.ntotal == len(store.chunks)


def test_search_returns_results():
    store = load_store()

    results = store.search(
        "What is Airtel's 5G customer base?",
        top_k=5,
    )

    assert len(results) == 5


def test_search_result_has_required_metadata():
    store = load_store()

    results = store.search(
        "What is Airtel's 5G customer base?",
        top_k=1,
    )

    result = results[0]

    assert "chunk_id" in result
    assert "document" in result
    assert "page" in result
    assert "chunk_index" in result
    assert "text" in result
    assert "token_count" in result
    assert "score" in result


def test_search_respects_top_k():
    store = load_store()

    for top_k in [1, 3, 5]:
        results = store.search(
            "5G network security",
            top_k=top_k,
        )

        assert len(results) == top_k


def test_results_have_valid_scores():
    store = load_store()

    results = store.search(
        "network architecture",
        top_k=5,
    )

    for result in results:
        assert isinstance(result["score"], float)
        assert -1.0 <= result["score"] <= 1.0


def test_multiple_documents_are_retrievable():
    store = load_store()

    queries = [
        "Airtel 5G customers",
        "Cisco network troubleshooting",
        "Ericsson 5G security",
        "GSMA IR.21 roaming",
    ]

    expected_documents = [
        "Bharti Airtel IAR 2024-25.pdf",
        "Cisco_Troubleshooting.pdf",
        "Ericsson_5G_Security.pdf",
        "GSMA_IR21.pdf",
    ]

    for query, expected_document in zip(
        queries,
        expected_documents,
    ):
        results = store.search(query, top_k=5)

        documents = [
            result["document"]
            for result in results
        ]

        assert expected_document in documents