from app.rag.generator import LocalGenerator


def main():
    generator = LocalGenerator()

    question = "What is 5G network slicing?"

    context = """
5G network slicing allows a single physical 5G network
to be divided into multiple virtual networks (slices),
each tailored to specific services and users with different
requirements, such as latency, bandwidth, or security needs.
"""

    answer = generator.generate(
        question=question,
        context=context,
        max_new_tokens=150,
    )

    print("\n" + "=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(question)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    main()