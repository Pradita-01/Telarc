from app.ingestion.document_classifier import classify_document


def test_financial_document_by_content():
    pages = [
        {
            "page": 1,
            "text": """
            Reliance Jio Infocomm Limited
            Standalone Financial Statements
            Balance Sheet
            Statement of Profit and Loss
            Notes to the Standalone Financial Statements
            """,
        }
    ]

    result = classify_document(
        "some_document.pdf",
        pages,
    )

    assert result == "financial"


def test_general_document():
    pages = [
        {
            "page": 1,
            "text": """
            Telecom Network Architecture
            5G Core Network
            Network Functions
            """,
        }
    ]

    result = classify_document(
        "3GPP_Network_Architecture.pdf",
        pages,
    )

    assert result == "general"