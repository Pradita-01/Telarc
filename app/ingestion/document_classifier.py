from pathlib import Path


FINANCIAL_KEYWORDS = (
    "standalone financial statements",
    "financial statements",
    "balance sheet",
    "statement of profit and loss",
    "cash flow statement",
    "notes to the standalone financial statements",
)


def classify_document(
    pdf_path: str | Path,
    pages: list[dict],
) -> str:
    filename = Path(pdf_path).name.lower()

    filename_score = 0

    if "financial statement" in filename:
        filename_score += 3

    if "annual report" in filename:
        filename_score += 1

    sample_text = "\n".join(
        page.get("text", "")
        for page in pages[:10]
    ).lower()

    keyword_score = sum(
        1
        for keyword in FINANCIAL_KEYWORDS
        if keyword in sample_text
    )

    if filename_score >= 3 or keyword_score >= 3:
        return "financial"

    return "general"