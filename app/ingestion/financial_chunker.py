from __future__ import annotations

import re
from pathlib import Path
from typing import TypedDict

import tiktoken


class FinancialChunkData(TypedDict):
    chunk_id: str
    document: str
    page: int
    chunk_index: int
    text: str
    token_count: int
    note: str
    section: str
    content_type: str
    table_id: str
    unit: str


NUMBERED_SECTION_PATTERN = re.compile(
    r"(?m)^\s*(\d+\.\d+(?:\.\d+)?)\s+"
)

NOTE_PATTERN = re.compile(
    r"(?i)^\s*note\s+(\d{1,2})(?:\s*[:.-]|\s+)"
)

UNIT_PATTERN = re.compile(
    r"(?i)(?:₹|rs\.?|inr)\s*(?:in\s+)?"
    r"(?:million|billion|crore|lakh|thousand)?"
)

TABLE_START_PHRASES = (
    "particulars",
    "particular",
    "description",
    "as at",
    "as of",
    "year ended",
    "year ending",
    "gross block",
    "net block",
    "opening balance",
    "closing balance",
    "capital work-in-progress",
    "ageing schedule",
    "spectrum under development",
    "related parties",
    "related party",
    "formulae",
    "formula",
    "ratio",
)

TABLE_TERMINATORS = (
    "auditor's report",
    "auditors report",
    "independent auditor",
    "significant accounting",
    "accounting policies",
)


def _clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\u00ad", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _token_count(text: str, encoder) -> int:
    return len(encoder.encode(text))


def _is_noise(text: str) -> bool:
    text = _clean_text(text)

    if not text:
        return True

    if re.fullmatch(r"page\s+\d+", text, re.I):
        return True

    if re.fullmatch(r"\d+", text):
        return True

    return False


def _extract_unit(text: str) -> str:
    match = UNIT_PATTERN.search(text)

    if not match:
        return ""

    return match.group(0).strip()


def _extract_note(text: str) -> str:
    first_line = text.strip().splitlines()[0] if text.strip() else ""

    match = NOTE_PATTERN.match(first_line)

    if match:
        return match.group(1)

    return ""


def _extract_section(text: str) -> str:
    first_line = text.strip().splitlines()[0] if text.strip() else ""

    match = re.match(
        r"^\s*(\d+\.\d+(?:\.\d+)?)\s+(.+)$",
        first_line,
    )

    if not match:
        return ""

    return f"{match.group(1)} {match.group(2).strip()}"


def _is_numbered_section(text: str) -> bool:
    first_line = text.strip().splitlines()[0] if text.strip() else ""

    return bool(
        re.match(
            r"^\s*\d+\.\d+(?:\.\d+)?(?:\s+|$)",
            first_line,
        )
    )


def _split_numbered_sections(text: str) -> list[str]:
    text = _clean_text(text)

    if not text:
        return []

    matches = list(NUMBERED_SECTION_PATTERN.finditer(text))

    if not matches:
        return [text]

    sections = []

    if matches[0].start() > 0:
        prefix = text[:matches[0].start()].strip()

        if prefix:
            sections.append(prefix)

    for index, match in enumerate(matches):
        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        section = text[start:end].strip()

        if section:
            sections.append(section)

    return sections


def _looks_like_table_start(text: str) -> bool:
    text = _clean_text(text)

    if not text:
        return False

    lower = text.lower()

    if any(phrase in lower for phrase in TABLE_START_PHRASES):
        return True

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) < 2:
        return False

    numeric_lines = 0

    for line in lines:
        if re.search(
            r"(?:\d[\d,]*(?:\.\d+)?|\(\d[\d,]*(?:\.\d+)?\))",
            line,
        ):
            numeric_lines += 1

    return (
        numeric_lines >= 2
        and numeric_lines / len(lines) >= 0.35
    )


def _looks_like_table_continuation(text: str) -> bool:
    text = _clean_text(text)

    if not text:
        return False

    if any(
        terminator in text.lower()
        for terminator in TABLE_TERMINATORS
    ):
        return False

    if _is_numbered_section(text):
        return False

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return False

    if len(lines) <= 4:
        return True

    numeric_lines = sum(
        bool(
            re.search(
                r"(?:\d[\d,]*(?:\.\d+)?|\(\d[\d,]*(?:\.\d+)?\))",
                line,
            )
        )
        for line in lines
    )

    return numeric_lines >= 2


def _split_table_lines(
    text: str,
    max_tokens: int,
    encoder,
) -> list[str]:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return []

    chunks = []
    current = []

    for line in lines:
        candidate = "\n".join(
            current + [line]
        )

        if (
            current
            and _token_count(candidate, encoder) > max_tokens
        ):
            chunks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        chunks.append("\n".join(current))

    return chunks


def _split_narrative(
    text: str,
    max_tokens: int,
    encoder,
) -> list[str]:
    text = _clean_text(text)

    if not text:
        return []

    if _token_count(text, encoder) <= max_tokens:
        return [text]

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    chunks = []
    current = []

    for sentence in sentences:
        candidate = " ".join(
            current + [sentence]
        )

        if (
            current
            and _token_count(candidate, encoder) > max_tokens
        ):
            chunks.append(" ".join(current))
            current = [sentence]
        else:
            current.append(sentence)

    if current:
        chunks.append(" ".join(current))

    return chunks


def _group_blocks(blocks: list[dict]) -> list[dict]:
    usable = []

    for block in blocks:
        text = _clean_text(
            block.get("text", "")
        )

        if not text or _is_noise(text):
            continue

        usable.append(
            {
                "text": text,
                "x0": float(block.get("x0", 0)),
                "y0": float(block.get("y0", 0)),
                "x1": float(block.get("x1", 0)),
                "y1": float(block.get("y1", 0)),
            }
        )

    usable.sort(
        key=lambda block: (
            block["y0"],
            block["x0"],
        )
    )

    rows: list[list[dict]] = []

    for block in usable:
        placed = False

        for row in reversed(rows[-3:]):
            row_y = min(
                item["y0"]
                for item in row
            )

            if abs(block["y0"] - row_y) <= 7:
                row.append(block)
                placed = True
                break

        if not placed:
            rows.append([block])

    ordered = []

    for row in rows:
        row.sort(
            key=lambda block: block["x0"]
        )

        combined_text = "\n".join(
            block["text"]
            for block in row
        ).strip()

        if not combined_text:
            continue

        ordered.append(
            {
                "text": combined_text,
                "x0": min(
                    block["x0"]
                    for block in row
                ),
                "y0": min(
                    block["y0"]
                    for block in row
                ),
                "x1": max(
                    block["x1"]
                    for block in row
                ),
                "y1": max(
                    block["y1"]
                    for block in row
                ),
            }
        )

    return ordered


def _make_table_id(
    document_name: str,
    table_number: int,
) -> str:
    document_key = Path(
        document_name
    ).stem

    document_key = re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        document_key,
    ).strip("_")

    return (
        f"{document_key}"
        f"_financial_table_{table_number}"
    )


def chunk_financial_pages(
    pages: list[dict],
    document_name: str,
    max_tokens: int = 450,
) -> list[FinancialChunkData]:

    encoder = tiktoken.get_encoding(
        "cl100k_base"
    )

    chunks: list[FinancialChunkData] = []

    chunk_index = 0
    table_number = 0

    active_table_lines: list[str] = []
    active_table_id = ""
    active_table_page = 0
    active_table_note = ""
    active_table_section = ""
    active_table_unit = ""

    current_note = ""
    current_section = ""
    current_unit = ""

    def flush_table():
        nonlocal chunk_index
        nonlocal active_table_lines
        nonlocal active_table_id
        nonlocal active_table_page
        nonlocal active_table_note
        nonlocal active_table_section
        nonlocal active_table_unit

        if not active_table_lines:
            return

        table_text = "\n".join(
            active_table_lines
        ).strip()

        pieces = _split_table_lines(
            table_text,
            max_tokens=max_tokens,
            encoder=encoder,
        )

        for piece in pieces:
            chunk_index += 1

            chunks.append(
                {
                    "chunk_id": (
                        f"{Path(document_name).stem}"
                        f"_financial_{chunk_index}"
                    ),
                    "document": document_name,
                    "page": active_table_page,
                    "chunk_index": chunk_index,
                    "text": piece,
                    "token_count": _token_count(
                        piece,
                        encoder,
                    ),
                    "note": active_table_note,
                    "section": active_table_section,
                    "content_type": "table",
                    "table_id": active_table_id,
                    "unit": active_table_unit,
                }
            )

        active_table_lines = []
        active_table_id = ""
        active_table_page = 0
        active_table_note = ""
        active_table_section = ""
        active_table_unit = ""

    def add_narrative(
        text: str,
        page_number: int,
        note: str,
        section: str,
        unit: str,
    ):
        nonlocal chunk_index

        pieces = _split_narrative(
            text,
            max_tokens=max_tokens,
            encoder=encoder,
        )

        for piece in pieces:
            if not piece.strip():
                continue

            chunk_index += 1

            chunks.append(
                {
                    "chunk_id": (
                        f"{Path(document_name).stem}"
                        f"_financial_{chunk_index}"
                    ),
                    "document": document_name,
                    "page": page_number,
                    "chunk_index": chunk_index,
                    "text": piece,
                    "token_count": _token_count(
                        piece,
                        encoder,
                    ),
                    "note": note,
                    "section": section,
                    "content_type": "narrative",
                    "table_id": "",
                    "unit": unit,
                }
            )

    for page in pages:
        page_number = page["page"]

        blocks = _group_blocks(
            page.get("blocks", [])
        )

        for block in blocks:
            raw_text = block["text"]

            units = _split_numbered_sections(
                raw_text
            )

            for unit in units:
                text = _clean_text(unit)

                if not text:
                    continue

                unit_note = _extract_note(text)
                unit_section = _extract_section(text)
                unit_unit = _extract_unit(text)

                if unit_note:
                    current_note = unit_note

                if unit_section:
                    current_section = unit_section

                if unit_unit:
                    current_unit = unit_unit

                is_section = _is_numbered_section(
                    text
                )

                if is_section:
                    if active_table_lines:
                        flush_table()

                    if _looks_like_table_start(text):
                        table_number += 1

                        active_table_id = _make_table_id(
                            document_name,
                            table_number,
                        )

                        active_table_page = page_number
                        active_table_note = (
                            current_note
                        )
                        active_table_section = (
                            unit_section
                            or current_section
                        )
                        active_table_unit = (
                            unit_unit
                            or current_unit
                        )

                        active_table_lines.extend(
                            text.splitlines()
                        )
                    else:
                        add_narrative(
                            text,
                            page_number,
                            current_note,
                            (
                                unit_section
                                or current_section
                            ),
                            (
                                unit_unit
                                or current_unit
                            ),
                        )

                    continue

                if active_table_lines:
                    first_line = (
                        text.strip()
                        .splitlines()[0]
                        if text.strip()
                        else ""
                    )

                    numbered_table_row = bool(
                        re.match(
                            r"^\s*\d+\s+[A-Za-z(]",
                            first_line,
                        )
                    )

                    if (
                        _looks_like_table_continuation(
                            text
                        )
                        or numbered_table_row
                        or len(text.splitlines()) <= 4
                    ):
                        active_table_lines.extend(
                            text.splitlines()
                        )
                        continue

                    flush_table()

                if _looks_like_table_start(text):
                    table_number += 1

                    active_table_id = _make_table_id(
                        document_name,
                        table_number,
                    )

                    active_table_page = page_number
                    active_table_note = (
                        unit_note
                        or current_note
                    )
                    active_table_section = (
                        unit_section
                        or current_section
                    )
                    active_table_unit = (
                        unit_unit
                        or current_unit
                    )

                    active_table_lines.extend(
                        text.splitlines()
                    )

                    continue

                add_narrative(
                    text,
                    page_number,
                    (
                        unit_note
                        or current_note
                    ),
                    (
                        unit_section
                        or current_section
                    ),
                    (
                        unit_unit
                        or current_unit
                    ),
                )

        flush_table()

        current_note = ""
        current_section = ""
        current_unit = ""

    flush_table()

    return chunks