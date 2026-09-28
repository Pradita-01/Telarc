from pathlib import Path

from app.ingestion.pipeline import process_pdf


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def main():
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/raw/")
        return

    print(f"Found {len(pdf_files)} PDF files.\n")

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")

        output_path = process_pdf(
            pdf_path,
            PROCESSED_DIR,
            chunk_size=500,
            chunk_overlap=75,
        )

        print(f"  -> {output_path}")

    print("\nIngestion complete.")


if __name__ == "__main__":
    main()