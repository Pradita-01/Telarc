from typing import TypedDict


class Citation(TypedDict):
    source_id: int
    document: str
    page: int
    chunk_id: str
    score: float


def build_citations(results: list[dict]) -> list[Citation]:
    """
    Build citation metadata from retrieved chunks.

    Telarc owns citation generation.
    The LLM never generates or invents document/page metadata.
    """

    citations: list[Citation] = []

    for source_id, result in enumerate(results, start=1):
        citations.append(
            {
                "source_id": source_id,
                "document": result["document"],
                "page": result["page"],
                "chunk_id": result["chunk_id"],
                "score": float(result["score"]),
            }
        )

    return citations


def format_citations(citations: list[Citation]) -> str:
    """
    Format citation metadata for display.
    """

    if not citations:
        return "No sources available."

    lines = ["Sources:"]

    for citation in citations:
        lines.append(
            f"[{citation['source_id']}] "
            f"{citation['document']} — "
            f"Page {citation['page']}"
        )

    return "\n".join(lines)