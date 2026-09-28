from pathlib import Path

from app.retrieval.vector_store import VectorStore


PROCESSED_DIR = Path("data/processed")
INDEX_DIR = Path("data/indexes")


def main():
    print("Building Telarc vector index...")

    store = VectorStore()

    store.build(PROCESSED_DIR)

    store.save(INDEX_DIR)

    print("\nVector index saved successfully!")


if __name__ == "__main__":
    main()