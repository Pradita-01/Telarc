from pathlib import Path
from typing import TypedDict

import pymupdf


class TextBlock(TypedDict):
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    block_number: int


class PageData(TypedDict):
    page: int
    text: str
    blocks: list[TextBlock]


def load_pdf(pdf_path: str | Path) -> list[PageData]:
    """
    Extract text from every page of a PDF.

    Each page contains:
    - a 1-based page number
    - complete extracted page text
    - individual PyMuPDF text blocks

    Text blocks preserve basic positional information so that
    downstream chunking can make better decisions about
    document structure.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file, got: {pdf_path.suffix}"
        )

    pages: list[PageData] = []

    document = pymupdf.open(pdf_path)

    try:
        for page_number, page in enumerate(
            document,
            start=1,
        ):

            # Keep the complete page text exactly as before.
            text = page.get_text("text").strip()

            # Extract structured text blocks.
            raw_blocks = page.get_text("blocks")

            blocks: list[TextBlock] = []

            for block_number, block in enumerate(
                raw_blocks,
                start=1,
            ):
                # Standard text block structure:
                # x0, y0, x1, y1, text, block_no, block_type, ...
                if len(block) < 5:
                    continue

                block_text = str(block[4]).strip()

                # Ignore empty blocks.
                if not block_text:
                    continue

                blocks.append(
                    {
                        "text": block_text,
                        "x0": float(block[0]),
                        "y0": float(block[1]),
                        "x1": float(block[2]),
                        "y1": float(block[3]),
                        "block_number": block_number,
                    }
                )

            pages.append(
                {
                    "page": page_number,
                    "text": text,
                    "blocks": blocks,
                }
            )

    finally:
        document.close()

    return pages