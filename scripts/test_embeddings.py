from pathlib import Path
import json

from sentence_transformers import SentenceTransformer


PROCESSED_DIR = Path("data/processed")


def main():
    json_files = sorted(PROCESSED_DIR.glob("*.json"))

    if not json_files:
        print("No processed JSON files found.")
        return

    first_file = json_files[0]

    with first_file.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    print(f"Document: {first_file.name}")
    print(f"Chunks: {len(chunks)}")

    first_chunk = chunks[0]

    print("\nFirst chunk:")
    print(first_chunk["text"][:500])

    print("\nLoading embedding model...")

    model = SentenceTransformer("BAAI/bge-small-en-v1.5")

    embedding = model.encode(
        first_chunk["text"],
        normalize_embeddings=True,
    )

    print("\nEmbedding created!")
    print(f"Vector dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")


if __name__ == "__main__":
    main()