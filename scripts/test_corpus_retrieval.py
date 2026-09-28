from pathlib import Path

from app.retrieval.vector_store import VectorStore


INDEX_DIR = Path("data/indexes")


TEST_QUERIES = [
    ("Airtel", "What is Airtel's 5G customer base?"),
    ("Jio", "What is Reliance Jio's subscriber base?"),
    ("Ericsson", "What are the key security considerations for 5G networks?"),
    ("Cisco", "What are common network troubleshooting approaches?"),
    ("3GPP", "What are the main components of the 3GPP network architecture?"),
    ("GSMA", "What information is covered by GSMA IR.21?"),
    ("Tata", "What are the key business areas discussed by Tata Communications?"),
    ("ICT", "What are the major areas covered in this ICT document?"),
]


def main():
    print("Loading Telarc vector index...")
    store = VectorStore()
    store.load(INDEX_DIR)

    print(f"\nLoaded {len(store.chunks)} chunks.")
    print("=" * 100)

    for name, query in TEST_QUERIES:
        print(f"\n\n{'#' * 100}")
        print(f"TEST: {name}")
        print(f"QUERY: {query}")
        print(f"{'#' * 100}")

        results = store.search(
            query=query,
            top_k=3,
        )

        for rank, result in enumerate(results, start=1):
            print(f"\nRESULT #{rank}")
            print("-" * 80)
            print(f"Score:    {result['score']:.4f}")
            print(f"Document: {result['document']}")
            print(f"Page:     {result['page']}")
            print(f"Chunk:    {result['chunk_index']}")
            print("\nText:")
            print(result["text"][:800])


if __name__ == "__main__":
    main()