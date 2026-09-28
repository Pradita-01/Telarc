from pathlib import Path

import pytest

from app.ingestion.pdf_loader import load_pdf


# Real PDF used for the ingestion test
AIRTel_PDF = Path("data/raw/Bharti Airtel IAR 2024-25.pdf")


def test_pdf_loads_successfully():
    """The Airtel PDF should load and return pages."""

    pages = load_pdf(AIRTel_PDF)

    assert len(pages) > 0


def test_page_numbers_start_at_one():
    """Page numbering should be 1-based."""

    pages = load_pdf(AIRTel_PDF)

    assert pages[0]["page"] == 1


def test_pages_have_expected_structure():
    """Every extracted page should contain page number and text."""

    pages = load_pdf(AIRTel_PDF)

    for page in pages:
        assert "page" in page
        assert "text" in page
        assert isinstance(page["page"], int)
        assert isinstance(page["text"], str)


def test_page_numbers_are_sequential():
    """Pages should retain their original sequential order."""

    pages = load_pdf(AIRTel_PDF)

    page_numbers = [page["page"] for page in pages]

    assert page_numbers == list(range(1, len(pages) + 1))


def test_missing_pdf_raises_error():
    """A missing PDF should raise FileNotFoundError."""

    with pytest.raises(FileNotFoundError):
        load_pdf("data/raw/does_not_exist.pdf")


def test_non_pdf_file_raises_error(tmp_path):
    """A non-PDF file should be rejected."""

    text_file = tmp_path / "test.txt"
    text_file.write_text("This is not a PDF.")

    with pytest.raises(ValueError):
        load_pdf(text_file)