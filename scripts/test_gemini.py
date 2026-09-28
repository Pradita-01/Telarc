from app.rag.generator import LocalGenerator


def main():
    generator = LocalGenerator()

    question = "What is 5G network slicing?"

    context = """
SOURCE [1]
Document: Ericsson_5G_Security.pdf
Page: 10
Chunk ID: test_chunk_001

Evidence:
5G network slicing allows a physical network infrastructure
to be logically divided into multiple virtual network slices.
Each slice can be configured for different service requirements.
"""

    answer = generator.generate(
        question=question,
        context=context,
    )

    print("\n" + "=" * 80)
    print("GEMINI TEST")
    print("=" * 80)

    print("\nQUESTION:")
    print(question)

    print("\nANSWER:")
    print(answer)


if __name__ == "__main__":
    main()