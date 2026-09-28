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
    / "retrieval_evaluation_report.json"
)


def load_dataset() -> list[dict]:
    """Load the Telarc evaluation dataset."""

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def evaluate_retrieval(
    pipeline: RAGPipeline,
    item: dict,
) -> dict:
    """
    Evaluate retrieval without calling the LLM.

    This deliberately calls the retrieval layer directly so
    temporary Gemini availability does not affect retrieval
    evaluation.
    """

    retrieved_chunks = pipeline._retrieve(
        item["question"],
        top_k=8,
    )

    retrieved_documents = [
        chunk["document"]
        for chunk in retrieved_chunks
    ]

    retrieved_pages = [
        chunk["page"]
        for chunk in retrieved_chunks
    ]

    expected_answerable = item["expected_answerable"]

    preferred_source_retrieved = None

    if expected_answerable:

        expected_document = item["expected_document"]
        expected_page = item["expected_page"]

        preferred_source_retrieved = (
            expected_document in retrieved_documents
            and expected_page in retrieved_pages
        )

    return {
        "id": item["id"],
        "question": item["question"],
        "category": item["category"],
        "expected_answerable": expected_answerable,
        "preferred_source_retrieved": (
            preferred_source_retrieved
        ),
        "retrieved_documents": retrieved_documents,
        "retrieved_pages": retrieved_pages,
        "retrieved_chunks": [
            {
                "document": chunk["document"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"],
                "score": chunk.get("score"),
            }
            for chunk in retrieved_chunks
        ],
    }


def run_evaluation():
    """Run retrieval evaluation and save the report."""

    print(
        "Loading Telarc retrieval evaluation..."
    )

    dataset = load_dataset()

    print(
        f"Evaluation questions: {len(dataset)}"
    )

    print(
        "Initializing Telarc retrieval pipeline..."
    )

    pipeline = RAGPipeline()

    print(
        "Telarc retrieval pipeline ready."
    )

    results = []

    for index, item in enumerate(
        dataset,
        start=1,
    ):

        print(
            f"\n[{index}/{len(dataset)}] "
            f"{item['question']}"
        )

        result = evaluate_retrieval(
            pipeline,
            item,
        )

        results.append(result)

        if result[
            "preferred_source_retrieved"
        ] is None:

            print(
                "Preferred source: "
                "N/A (abstention question)"
            )

        else:

            print(
                "Preferred source retrieved: "
                f"{result['preferred_source_retrieved']}"
            )

            if not result[
                "preferred_source_retrieved"
            ]:

                print(
                    "Expected: "
                    f"{item['expected_document']} "
                    f"page {item['expected_page']}"
                )

    answerable_results = [
        result
        for result in results
        if result["expected_answerable"]
    ]

    preferred_source_accuracy = (
        sum(
            result[
                "preferred_source_retrieved"
            ]
            for result in answerable_results
        )
        / len(answerable_results)
        if answerable_results
        else 0.0
    )

    report = {
        "total_questions": len(results),
        "answerable_questions": len(
            answerable_results
        ),
        "preferred_source_retrieval_accuracy": round(
            preferred_source_accuracy,
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
        "TELARC RETRIEVAL EVALUATION COMPLETE"
    )
    print("=" * 60)

    print(
        f"Total questions: {len(results)}"
    )

    print(
        f"Answerable questions: "
        f"{len(answerable_results)}"
    )

    print(
        "Preferred-source retrieval accuracy: "
        f"{preferred_source_accuracy:.2%}"
    )

    print(
        f"Report saved to: {REPORT_PATH}"
    )


if __name__ == "__main__":
    run_evaluation()