import json
from pathlib import Path


INDEX_FILE = Path("data/indexes/chunks.json")


def main():

    print("=" * 80)
    print("TELARC RELIANCE RETRIEVAL DIAGNOSTIC")
    print("=" * 80)

    if not INDEX_FILE.exists():

        print(f"\nERROR: {INDEX_FILE} was not found.")
        return

    with INDEX_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        chunks = json.load(file)


    print(f"\nTotal indexed chunks: {len(chunks)}")


    # ---------------------------------------------------------
    # Find Reliance / Jio chunks
    # ---------------------------------------------------------

    reliance_chunks = []

    for chunk in chunks:

        document = chunk.get(
            "document",
            "",
        ).lower()

        if (
            "reliance" in document
            or "jio" in document
        ):

            reliance_chunks.append(chunk)


    print(
        f"Reliance/Jio chunks: "
        f"{len(reliance_chunks)}"
    )


    # ---------------------------------------------------------
    # Show Reliance documents
    # ---------------------------------------------------------

    documents = sorted(
        {
            chunk["document"]
            for chunk in reliance_chunks
        }
    )


    print("\nReliance/Jio documents:")

    for document in documents:

        count = sum(
            1
            for chunk in reliance_chunks
            if chunk["document"] == document
        )

        print(
            f"  {count:5d} chunks  |  {document}"
        )


    # ---------------------------------------------------------
    # Search for financial terms
    # ---------------------------------------------------------

    search_terms = [
        "revenue",
        "revenue from operations",
        "profit",
        "profit for the year",
        "profit before tax",
        "profit after tax",
        "total income",
        "statement of profit and loss",
    ]


    print("\n")
    print("=" * 80)
    print("FINANCIAL EVIDENCE SEARCH")
    print("=" * 80)


    for term in search_terms:

        print(f"\n### {term.upper()}")

        matches = []

        for chunk in reliance_chunks:

            text = chunk.get(
                "text",
                "",
            ).lower()

            if term.lower() in text:

                matches.append(chunk)


        print(
            f"Matches: {len(matches)}"
        )


        for chunk in matches[:5]:

            print("\n----------------------------------------")

            print(
                f"Document : "
                f"{chunk.get('document')}"
            )

            print(
                f"Page     : "
                f"{chunk.get('page')}"
            )

            print(
                f"Chunk ID : "
                f"{chunk.get('chunk_id')}"
            )

            print(
                f"Tokens   : "
                f"{chunk.get('token_count')}"
            )

            text = chunk.get(
                "text",
                "",
            )

            print(
                "\n"
                + text[:1200]
            )


    # ---------------------------------------------------------
    # Search specifically for FY2024-25
    # ---------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("FY2024-25 DOCUMENT CHECK")
    print("=" * 80)


    target_documents = []

    for document in documents:

        document_lower = document.lower()

        if (
            "2024-25" in document_lower
            or "2024_25" in document_lower
        ):

            target_documents.append(
                document
            )


    if not target_documents:

        print(
            "\nWARNING: Could not identify "
            "a 2024-25 Reliance document by filename."
        )

    else:

        for document in target_documents:

            print(
                f"\nFOUND: {document}"
            )


            document_chunks = [
                chunk
                for chunk in reliance_chunks
                if chunk["document"] == document
            ]


            print(
                f"Chunks: {len(document_chunks)}"
            )


            for term in [
                "revenue",
                "profit",
                "total income",
            ]:

                matches = [
                    chunk
                    for chunk in document_chunks
                    if term.lower()
                    in chunk.get(
                        "text",
                        "",
                    ).lower()
                ]


                print(
                    f"  {term}: "
                    f"{len(matches)} matches"
                )


    print("\n")
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()