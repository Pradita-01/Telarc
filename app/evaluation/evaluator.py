import json
from pathlib import Path

from app.rag.pipeline import RAGPipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "questions.json"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "evaluation_report.json"
)


def load_dataset() -> list[dict]:
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def evaluate_question(
    pipeline: RAGPipeline,
    item: dict,
) -> dict:

    result = pipeline.answer(
        item["question"]
    )

    retrieved_documents = [
        chunk["document"]
        for chunk in result.get(
            "retrieved_chunks",
            [],
        )
    ]

    retrieved_pages = [
        chunk["page"]
        for chunk in result.get(
            "retrieved_chunks",
            [],
        )
    ]

    expected_answerable = (
        item["expected_answerable"]
    )

    actual_answerable = (
        result["answerable"]
    )

    answerability_correct = (
        expected_answerable
        == actual_answerable
    )

    evidence_correct = True

    if expected_answerable:

        expected_document = (
            item["expected_document"]
        )

        expected_page = (
            item["expected_page"]
        )

        evidence_correct = (
            expected_document
            in retrieved_documents
            and expected_page
            in retrieved_pages
        )

    return {
        "id": item["id"],
        "question": item["question"],
        "category": item["category"],
        "expected_answerable": (
            expected_answerable
        ),
        "actual_answerable": (
            actual_answerable
        ),
        "answerability_correct": (
            answerability_correct
        ),
        "evidence_correct": (
            evidence_correct
        ),
        "answer": result["answer"],
        "citations": result.get(
            "citations",
            [],
        ),
    }


def run_evaluation():

    print(
        "Loading Telarc evaluation dataset..."
    )

    dataset = load_dataset()

    print(
        f"Evaluation questions: "
        f"{len(dataset)}"
    )

    pipeline = RAGPipeline()

    results = []

    for index, item in enumerate(
        dataset,
        start=1,
    ):

        print(
            f"\n[{index}/{len(dataset)}] "
            f"{item['question']}"
        )

        result = evaluate_question(
            pipeline,
            item,
        )

        results.append(result)

        print(
            f"Answerable: "
            f"{result['actual_answerable']}"
        )

        print(
            f"Answerability correct: "
            f"{result['answerability_correct']}"
        )

        print(
            f"Evidence retrieved: "
            f"{result['evidence_correct']}"
        )

    total = len(results)

    answerability_accuracy = (
        sum(
            result["answerability_correct"]
            for result in results
        )
        / total
        if total
        else 0
    )

    evidence_accuracy = (
        sum(
            result["evidence_correct"]
            for result in results
        )
        / total
        if total
        else 0
    )

    report = {
        "total_questions": total,
        "answerability_accuracy": round(
            answerability_accuracy,
            4,
        ),
        "evidence_retrieval_accuracy": round(
            evidence_accuracy,
            4,
        ),
        "results": results,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("\n" + "=" * 60)
    print(
        "TELARC EVALUATION COMPLETE"
    )
    print("=" * 60)

    print(
        f"Total questions: {total}"
    )

    print(
        f"Answerability accuracy: "
        f"{answerability_accuracy:.2%}"
    )

    print(
        f"Evidence retrieval accuracy: "
        f"{evidence_accuracy:.2%}"
    )

    print(
        f"Report saved to: "
        f"{REPORT_PATH}"
    )

    return report


if __name__ == "__main__":
    run_evaluation()