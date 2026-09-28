from pathlib import Path
import json

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.chunker import chunk_pages
from app.ingestion.financial_chunker import chunk_financial_pages
from app.ingestion.document_classifier import classify_document


def process_pdf(
    pdf_path: str | Path,
    output_dir: str | Path,
    chunk_size: int = 500,
    chunk_overlap: int = 75,
):
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Load PDF pages
    # ---------------------------------------------------------

    pages = load_pdf(pdf_path)

    # ---------------------------------------------------------
    # Identify document type
    # ---------------------------------------------------------

    document_type = classify_document(
        pdf_path,
        pages,
    )

    print(
        f"Document: {pdf_path.name}"
    )

    print(
        f"Document type: {document_type}"
    )

    # ---------------------------------------------------------
    # Select appropriate chunker
    # ---------------------------------------------------------

    if document_type == "financial":

        chunks = chunk_financial_pages(
            pages,
            document_name=pdf_path.name,
            max_tokens=chunk_size,
        )

    else:

        chunks = chunk_pages(
            pages,
            document_name=pdf_path.name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    # ---------------------------------------------------------
    # Save processed chunks
    # ---------------------------------------------------------

    output_path = (
        output_dir
        / f"{pdf_path.stem}.json"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"Chunks created: {len(chunks)}"
    )

    print(
        f"Saved to: {output_path}"
    )

    return output_path