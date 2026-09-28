from app.ingestion.pdf_loader import load_pdf


PDF_PATH = "data/raw/Bharti Airtel IAR 2024-25.pdf"


def main():
    pages = load_pdf(PDF_PATH)

    print(f"Pages: {len(pages)}")
    print()

    # Inspect the pages that showed interesting chunking behavior.
    pages_to_inspect = {2, 3, 5, 6, 9}

    for page in pages:

        if page["page"] not in pages_to_inspect:
            continue

        print("=" * 100)
        print(f"PAGE {page['page']}")
        print(f"Total blocks: {len(page['blocks'])}")
        print("=" * 100)

        for block in page["blocks"]:

            text = (
                block["text"]
                .replace("\n", " ")
                .replace("\r", " ")
            )

            if len(text) > 300:
                text = text[:300] + "..."

            print(
                f'\nBlock {block["block_number"]}'
                f' | x0={block["x0"]:.1f}'
                f' y0={block["y0"]:.1f}'
                f' x1={block["x1"]:.1f}'
                f' y1={block["y1"]:.1f}'
            )

            print(f"Text: {text}")

        print()


if __name__ == "__main__":
    main()