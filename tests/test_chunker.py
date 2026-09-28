from app.ingestion.chunker import chunk_pages


def make_block(text: str, block_number: int = 1):
    return {
        "text": text,
        "x0": 50.0,
        "y0": 50.0,
        "x1": 500.0,
        "y1": 100.0,
        "block_number": block_number,
    }


def test_chunking_creates_chunks():
    pages = [
        {
            "page": 10,
            "text": "telecom " * 1000,
            "blocks": [
                make_block("telecom " * 1000)
            ],
        }
    ]

    chunks = chunk_pages(
        pages,
        document_name="test.pdf",
        chunk_size=100,
        chunk_overlap=20,
    )

    assert len(chunks) > 1


def test_chunk_preserves_page_number():
    pages = [
        {
            "page": 25,
            "text": "network " * 300,
            "blocks": [
                make_block("network " * 300)
            ],
        }
    ]

    chunks = chunk_pages(
        pages,
        document_name="test.pdf",
        chunk_size=100,
        chunk_overlap=20,
    )

    assert len(chunks) > 0
    assert all(chunk["page"] == 25 for chunk in chunks)


def test_chunk_ids_are_unique():
    pages = [
        {
            "page": 25,
            "text": "network " * 300,
            "blocks": [
                make_block("network " * 300)
            ],
        }
    ]

    chunks = chunk_pages(
        pages,
        document_name="test.pdf",
        chunk_size=100,
        chunk_overlap=20,
    )

    chunk_ids = [chunk["chunk_id"] for chunk in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_empty_pages_are_skipped():
    pages = [
        {
            "page": 1,
            "text": "",
            "blocks": [],
        }
    ]

    chunks = chunk_pages(
        pages,
        document_name="test.pdf",
    )

    assert chunks == []


def test_invalid_chunk_size():
    pages = [
        {
            "page": 1,
            "text": "network",
            "blocks": [
                make_block("network")
            ],
        }
    ]

    try:
        chunk_pages(
            pages,
            document_name="test.pdf",
            chunk_size=0,
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_overlap_must_be_smaller_than_chunk_size():
    pages = [
        {
            "page": 1,
            "text": "network",
            "blocks": [
                make_block("network")
            ],
        }
    ]

    try:
        chunk_pages(
            pages,
            document_name="test.pdf",
            chunk_size=100,
            chunk_overlap=100,
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass