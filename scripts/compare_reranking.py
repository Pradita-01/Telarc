from pathlib import Path

from app.retrieval.vector_store import VectorStore
from app.retrieval.reranker import Reranker


INDEX_DIR = Path("data/indexes")


QUESTIONS = [
    "What is Airtel's 5G customer base?",
    "What is described in the 3GPP network architecture?",
    "What is the current ratio formula?",
    "How can network connectivity problems be troubleshot?",
    "What is Airtel's satellite internet revenue in 2035?",
]


def main():
    store = VectorStore()
    store.load(INDEX_DIR)

    reranker = Reranker()

    for question in QUESTIONS:
        print("\n" + "=" * 90)
        print(f"QUESTION: {question}")

        candidates = store.search(
            question,
            top_k=20,
        )

        print("\nFAISS TOP 5")
        for rank, result in enumerate(candidates[:5], start=1):
            print(
                f"{rank}. "
                f"{result['score']:.4f} | "
                f"page={result['page']} | "
                f"{result['document']}"
            )

        reranked = reranker.rerank(
            question,
            candidates,
            top_k=5,
        )

        print("\nRERANKED TOP 5")
        for rank, result in enumerate(reranked, start=1):
            print(
                f"{rank}. "
                f"{result['rerank_score']:.4f} | "
                f"page={result['page']} | "
                f"{result['document']}"
            )


if __name__ == "__main__":
    main()