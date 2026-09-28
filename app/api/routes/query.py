from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.pipeline import RAGPipeline


router = APIRouter()

pipeline = RAGPipeline()


class QueryRequest(BaseModel):
    question: str


class CitationResponse(BaseModel):
    source_id: int
    document: str
    page: int
    chunk_id: str
    score: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    answerable: bool
    citations: list[CitationResponse]
    debug_retrieval: list[dict]


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):

    result = pipeline.answer(
        request.question
    )

    debug_retrieval = []

    for chunk in result.get(
        "retrieved_chunks",
        []
    ):

        debug_retrieval.append(
            {
                "document": chunk["document"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"],
                "score": chunk["score"],
                "text": chunk["text"][:1000],
            }
        )

    return {
        "question": result["question"],
        "answer": result["answer"],
        "answerable": result["answerable"],
        "citations": result["citations"],
        "debug_retrieval": debug_retrieval,
    }