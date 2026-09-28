from pathlib import Path

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.chunker import chunk_pages


def main():
    pdf_path = Path("data/raw/Bharti Airtel IAR 2024-25.pdf")

    pages = load_pdf(pdf_path)

    chunks = chunk_pages(
        pages,
        document_name=pdf_path.name,
        chunk_size=500,
        chunk_overlap=75,
    )

    print(f"Pages: {len(pages)}")
    print(f"Chunks: {len(chunks)}")

    print("\nFIRST 20 CHUNKS")
    print("=" * 80)

    for chunk in chunks[:20]:
        print(f"\nChunk ID: {chunk['chunk_id']}")
        print(f"Page: {chunk['page']}")
        print(f"Chunk index: {chunk['chunk_index']}")
        print(f"Token count: {chunk['token_count']}")
        print("-" * 80)
        print(chunk["text"])


if __name__ == "__main__":
    main()