# Telarc — Telecom Knowledge Assistant

Telarc is an evidence-grounded Retrieval-Augmented Generation (RAG) system designed for querying telecom technical documentation, industry reports, standards, and financial statements using natural language.

The system retrieves relevant evidence from an indexed telecom knowledge base and uses an LLM to generate answers grounded only in the retrieved documents. Responses include source document and page-level citations, while unsupported questions are rejected rather than answered using unsupported assumptions.

---

## Problem

Telecom organizations work with large volumes of technical standards, security documents, annual reports, financial statements, and industry documentation.

Finding specific information across these documents can be time-consuming, especially when users need:

- Precise answers from lengthy documents
- Financial information for a specific company and fiscal year
- Technical information from standards and reports
- Traceability back to the original document and page
- Protection against unsupported or hallucinated answers

Telarc addresses this problem by combining document processing, semantic retrieval, specialized financial retrieval, grounded generation, and citation tracking into a single knowledge assistant.

---

## Solution

Telarc converts telecom documents into searchable, page-aware chunks and builds a vector index using dense embeddings.

When a user asks a question:

1. The question is analyzed.
2. Relevant document chunks are retrieved.
3. Semantic retrieval is performed using vector similarity search.
4. Financial questions can use specialized lexical retrieval.
5. Retrieved evidence is provided to the language model.
6. The model generates a structured grounded response.
7. Telarc maps the response back to the retrieved document sources.
8. The system abstains when the available evidence is insufficient.

This creates a retrieval-first architecture where the language model is used for answer generation rather than acting as the source of truth.

---

## Architecture

```text
                    TELARC
                       |
             +---------+---------+
             |                   |
        Telecom Documents     User Query
             |                   |
          PyMuPDF                |
             |                   |
       Document Cleaning         |
             |                   |
        Smart Chunking           |
             |                   |
       Page-aware Metadata       |
             |                   |
       BGE Embeddings            |
             |                   |
            FAISS <--------------+
             |
      Retrieval Layer
             |
    +--------+---------+
    |                  |
Semantic Retrieval   Financial
                     Retrieval
    |                  |
    +--------+---------+
             |
       Retrieved Evidence
             |
        Gemini LLM
             |
     Grounded Response
             |
     Citation Mapping
             |
          FastAPI
             |
        Streamlit UI
