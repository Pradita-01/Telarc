from pathlib import Path

from app.retrieval.vector_store import VectorStore


INDEX_DIR = Path("data/indexes")


def main():
    print("Loading Telarc vector index...")

    store = VectorStore()

    store.load(INDEX_DIR)

    query = "What is Airtel's 5G customer base?"

    print("\n")
    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    results = store.search(
        query=query,
        top_k=5,
    )

    for rank, result in enumerate(results, start=1):
        print("\n")
        print(f"RESULT #{rank}")
        print("-" * 80)

        print(f"Score:    {result['score']:.4f}")
        print(f"Document: {result['document']}")
        print(f"Page:     {result['page']}")
        print(f"Chunk:    {result['chunk_index']}")

        print("\nText:")
        print(result["text"])


if __name__ == "__main__":
    main()