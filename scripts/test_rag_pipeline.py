from app.rag.pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()

    question = "What was Reliance Jio's subscriber base in FY 2024-25?"

    print("\n" + "=" * 80)
    print("TELARC QUESTION")
    print("=" * 80)
    print(question)

    response = pipeline.answer(
        question=question,
        top_k=5,
    )

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(response["answer"])

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)

    for citation in response["citations"]:
        print(
            f"[{citation['source_id']}] "
            f"{citation['document']} — "
            f"Page {citation['page']}"
        )


if __name__ == "__main__":
    main()