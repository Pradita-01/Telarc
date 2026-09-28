from app.retrieval.vector_store import VectorStore


def main():

    store = VectorStore()
    store.load("data/indexes")

    questions = [
        "What was Reliance Jio's revenue for FY2024-25?",
        "What was Reliance Jio's profit for FY2024-25?",
        "What was Reliance Jio's total income for FY2024-25?",
    ]

    for question in questions:

        print("\n")
        print("=" * 90)
        print(question)
        print("=" * 90)

        results = store.search(
            query=question,
            top_k=15,
        )

        for rank, result in enumerate(
            results,
            start=1,
        ):

            print("\n----------------------------------------")

            print(f"RANK: {rank}")
            print(f"SCORE: {result['score']:.4f}")
            print(f"DOCUMENT: {result['document']}")
            print(f"PAGE: {result['page']}")
            print(f"CHUNK: {result['chunk_id']}")

            print("\nTEXT:")
            print(
                result["text"][:700]
            )


if __name__ == "__main__":
    main()