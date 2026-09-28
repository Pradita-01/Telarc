from pathlib import Path

import pymupdf

from app.ingestion.financial_chunker import chunk_financial_pages


PDF_PATH = Path(
    "data/raw/Reliance_Jio_Infocomm_Limited-2024-25.pdf"
)

INSPECT_PAGES = {11, 21, 22, 40, 51}


def load_pages(pdf_path: Path) -> list[dict]:
    pages = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):

            blocks = []

            for block in page.get_text("blocks"):
                x0, y0, x1, y1, text, *_ = block

                if not text.strip():
                    continue

                blocks.append(
                    {
                        "text": text,
                        "x0": x0,
                        "y0": y0,
                        "x1": x1,
                        "y1": y1,
                    }
                )

            pages.append(
                {
                    "page": page_number,
                    "text": page.get_text(),
                    "blocks": blocks,
                }
            )

    return pages


def main():
    print("=" * 100)
    print("TELARC — JIO FINANCIAL CHUNK INSPECTION")
    print("=" * 100)

    print(f"\nPDF: {PDF_PATH}")

    pages = load_pages(PDF_PATH)

    print(f"Pages loaded: {len(pages)}")

    chunks = chunk_financial_pages(
        pages,
        document_name=PDF_PATH.name,
        max_tokens=450,
    )

    print(f"Financial chunks created: {len(chunks)}")

    print("\n" + "=" * 100)
    print("CHUNK DISTRIBUTION")
    print("=" * 100)

    narrative = sum(
        1
        for chunk in chunks
        if chunk["content_type"] == "narrative"
    )

    tables = sum(
        1
        for chunk in chunks
        if chunk["content_type"] == "table"
    )

    print(f"Narrative chunks : {narrative}")
    print(f"Table chunks     : {tables}")

    print("\n" + "=" * 100)
    print("SELECTED PAGE CHUNKS")
    print("=" * 100)

    for page_number in sorted(INSPECT_PAGES):

        page_chunks = [
            chunk
            for chunk in chunks
            if chunk["page"] == page_number
        ]

        print(
            f"\n{'#' * 100}\n"
            f"PAGE {page_number} — "
            f"{len(page_chunks)} CHUNKS\n"
            f"{'#' * 100}"
        )

        for chunk_number, chunk in enumerate(
            page_chunks,
            start=1,
        ):

            print("\n" + "-" * 100)

            print(
                f"Chunk {chunk_number} | "
                f"ID: {chunk['chunk_id']}"
            )

            print(
                f"Type: {chunk['content_type']} | "
                f"Tokens: {chunk['token_count']}"
            )

            print(
                f"Note: {chunk['note'] or 'N/A'} | "
                f"Section: {chunk['section'] or 'N/A'}"
            )

            print(
                f"Unit: {chunk['unit'] or 'N/A'}"
            )

            print(
                f"Table ID: "
                f"{chunk['table_id'] or 'N/A'}"
            )

            print("\nTEXT:")
            print(chunk["text"])


if __name__ == "__main__":
    main()