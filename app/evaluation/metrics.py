def answerability_accuracy(
    results: list[dict],
) -> float:

    if not results:
        return 0.0

    correct = sum(
        result["answerable_correct"]
        for result in results
    )

    return correct / len(results)


def evidence_retrieval_accuracy(
    results: list[dict],
) -> float:

    if not results:
        return 0.0

    correct = sum(
        result["evidence_correct"]
        for result in results
    )

    return correct / len(results)


def category_accuracy(
    results: list[dict],
    category: str,
) -> float:

    category_results = [
        result
        for result in results
        if result["category"] == category
    ]

    if not category_results:
        return 0.0

    correct = sum(
        result["answerable_correct"]
        for result in category_results
    )

    return correct / len(category_results)