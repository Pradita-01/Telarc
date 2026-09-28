from typing import TypedDict
import re

import tiktoken


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


class ChunkData(TypedDict):
    chunk_id: str
    document: str
    page: int
    chunk_index: int
    text: str
    token_count: int


def _get_encoder():
    """Return the tokenizer used for measuring chunk size."""
    return tiktoken.get_encoding("cl100k_base")


def _is_footer_or_navigation(block: TextBlock) -> bool:
    """
    Identify obvious repeated PDF furniture.

    We remove only elements that are clearly headers,
    footers, page numbers, or navigation labels.
    """

    text = block["text"].strip()

    if not text:
        return True

    # Repeated Airtel report footer/header.
    if "Bharti Airtel Limited Integrated Report" in text:
        return True

    # Standalone page-number blocks.
    if re.fullmatch(r"\d{1,4}", text):
        return True

    # Navigation labels appearing vertically on the page.
    navigation_labels = {
        "Overview and Performance",
        "Strategic Review",
        "Capital Wise Performance",
        "Statutory Reports",
        "Financial Statements",
    }

    if text in navigation_labels:
        return True

    return False


def _get_content_blocks(
    blocks: list[TextBlock],
) -> list[TextBlock]:
    """
    Keep meaningful text blocks while removing obvious
    PDF furniture such as repeated headers and page numbers.

    Blocks are sorted approximately in reading order.
    """

    content_blocks = [
        block
        for block in blocks
        if not _is_footer_or_navigation(block)
    ]

    # Sort by vertical position first and horizontal position second.
    #
    # This gives us a deterministic reading order while
    # preserving the original block text.
    content_blocks.sort(
        key=lambda block: (
            round(block["y0"], 1),
            round(block["x0"], 1),
        )
    )

    return content_blocks


def _split_into_sentences(
    text: str,
) -> list[str]:
    """
    Lightweight sentence splitting.

    Used only when a single PDF block is too large
    to fit naturally inside a chunk.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+(?=[A-Z0-9₹(])",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def _split_large_block(
    text: str,
    encoder,
    chunk_size: int,
) -> list[str]:
    """
    Split an unusually large block.

    Priority:
        sentence boundaries
        ↓
        token boundaries as final fallback
    """

    sentences = _split_into_sentences(text)

    pieces: list[str] = []

    for sentence in sentences:

        tokens = encoder.encode(sentence)

        if len(tokens) <= chunk_size:
            pieces.append(sentence)
            continue

        # Final fallback for an extremely large sentence.
        for start in range(
            0,
            len(tokens),
            chunk_size,
        ):
            end = min(
                start + chunk_size,
                len(tokens),
            )

            piece = encoder.decode(
                tokens[start:end]
            ).strip()

            if piece:
                pieces.append(piece)

    return pieces


def _prepare_units(
    blocks: list[TextBlock],
    encoder,
    chunk_size: int,
) -> list[str]:
    """
    Convert PDF blocks into semantic units.

    Normal blocks remain intact.

    Very large blocks are split into sentences,
    with token splitting used only as a last resort.
    """

    units: list[str] = []

    for block in blocks:

        text = block["text"].strip()

        if not text:
            continue

        token_count = len(
            encoder.encode(text)
        )

        if token_count <= chunk_size:
            units.append(text)
        else:
            units.extend(
                _split_large_block(
                    text,
                    encoder,
                    chunk_size,
                )
            )

    return units


def chunk_pages(
    pages: list[PageData],
    document_name: str,
    chunk_size: int = 500,
    chunk_overlap: int = 75,
) -> list[ChunkData]:
    """
    Create block-aware semantic chunks.

    Chunking hierarchy:

        PDF text block
              ↓
        sentence fallback
              ↓
        token fallback

    Chunks never cross page boundaries.
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if chunk_overlap < 0:
        raise ValueError(
            "chunk_overlap cannot be negative"
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    encoder = _get_encoder()

    chunks: list[ChunkData] = []

    for page_data in pages:

        page_number = page_data["page"]
        blocks = page_data["blocks"]

        if not blocks:
            continue

        content_blocks = _get_content_blocks(
            blocks
        )

        units = _prepare_units(
            content_blocks,
            encoder,
            chunk_size,
        )

        if not units:
            continue

        current_units: list[str] = []
        current_tokens: list[int] = []

        chunk_index = 1

        for unit in units:

            unit_tokens = encoder.encode(unit)

            # Keep the complete semantic unit if it fits.
            if (
                current_tokens
                and len(current_tokens)
                + len(unit_tokens)
                <= chunk_size
            ):
                current_units.append(unit)
                current_tokens.extend(
                    unit_tokens
                )
                continue

            # Start a new chunk.
            if not current_tokens:
                current_units = [unit]
                current_tokens = list(
                    unit_tokens
                )
                continue

            # Save the current chunk.
            chunk_text = "\n\n".join(
                current_units
            ).strip()

            chunks.append(
                {
                    "chunk_id": (
                        f"{document_name}"
                        f"_page_{page_number}"
                        f"_chunk_{chunk_index}"
                    ),
                    "document": document_name,
                    "page": page_number,
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "token_count": len(
                        current_tokens
                    ),
                }
            )

            chunk_index += 1

            # Semantic overlap:
            #
            # Instead of blindly copying 75 tokens,
            # retain complete previous units from the
            # end of the chunk until the overlap target
            # is approximately reached.
            overlap_units: list[str] = []
            overlap_token_count = 0

            for previous_unit in reversed(
                current_units
            ):

                previous_tokens = encoder.encode(
                    previous_unit
                )

                if (
                    overlap_token_count
                    + len(previous_tokens)
                    > chunk_overlap
                ):
                    break

                overlap_units.insert(
                    0,
                    previous_unit,
                )

                overlap_token_count += len(
                    previous_tokens
                )

            current_units = overlap_units + [
                unit
            ]

            current_tokens = []

            for overlap_unit in current_units:
                current_tokens.extend(
                    encoder.encode(
                        overlap_unit
                    )
                )

        # Save final chunk.
        if current_tokens:

            chunk_text = "\n\n".join(
                current_units
            ).strip()

            chunks.append(
                {
                    "chunk_id": (
                        f"{document_name}"
                        f"_page_{page_number}"
                        f"_chunk_{chunk_index}"
                    ),
                    "document": document_name,
                    "page": page_number,
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "token_count": len(
                        current_tokens
                    ),
                }
            )

    return chunks