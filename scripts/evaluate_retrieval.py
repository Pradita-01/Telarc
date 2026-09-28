from pathlib import Path

from app.retrieval.vector_store import VectorStore


INDEX_DIR = Path("data/indexes")


QUESTIONS = [
    {
        "question": "What is Airtel's 5G customer base?",
        "expected_document": "Bharti Airtel IAR 2024-25.pdf",
    },
    {
        "question": "What are the key features of 5G network security?",
        "expected_document": "Ericsson_5G_Security.pdf",
    },
    {
        "question": "What is described in the 3GPP network architecture?",
        "expected_document": "3GPP_Network_Architecture.pdf",
    },
    {
        "question": "What is the purpose of IR.21 in mobile roaming?",
        "expected_document": "GSMA_IR21.pdf",
    },
    {
        "question": "How can network connectivity problems be troubleshot?",
        "expected_document": "Cisco_Troubleshooting.pdf",
    },
    {
        "question": "What is the current ratio formula?",
        "expected_document": "Reliance_Jio_Infocomm_Limited-2024-25.pdf",
    },
    {
        "question": "What is Airtel's satellite internet revenue in 2035?",
        "expected_document": None,
    },
]


def main():
    store = VectorStore()
    store.load(INDEX_DIR)

    print(f"\nLoaded {store.index.ntotal} vectors.\n")
    print("=" * 80)

    for number, item in enumerate(QUESTIONS, start=1):
        question = item["question"]
        expected_document = item["expected_document"]

        results = store.search(question, top_k=5)

        documents = [
            result["document"]
            for result in results
        ]

        print(f"\nQUESTION {number}")
        print(question)

        print("\nTOP 5 RESULTS:")

        for rank, result in enumerate(results, start=1):
            print(
                f"{rank}. "
                f"score={result['score']:.4f} | "
                f"page={result['page']} | "
                f"{result['document']}"
            )

        if expected_document:
            found = expected_document in documents
            print(
                f"\nEXPECTED DOCUMENT FOUND: "
                f"{'YES' if found else 'NO'}"
            )
        else:
            print(
                "\nEXPECTED: "
                "Question should not have sufficient evidence."
            )

        print("-" * 80)


if __name__ == "__main__":
    main()