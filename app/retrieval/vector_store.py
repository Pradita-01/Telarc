from pathlib import Path
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    """
    Vector index for Telarc document chunks.

    Responsibilities:
    1. Load processed chunks
    2. Generate embeddings
    3. Store vectors in FAISS
    4. Save/load the FAISS index
    5. Keep chunk metadata alongside the index
    6. Search for relevant chunks
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
    ):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []

    def build(self, processed_dir: str | Path):
        """
        Build a FAISS index from processed JSON files.
        """

        processed_dir = Path(processed_dir)

        if not processed_dir.exists():
            raise FileNotFoundError(
                f"Processed directory not found: {processed_dir}"
            )

        json_files = sorted(processed_dir.glob("*.json"))

        if not json_files:
            raise ValueError(
                f"No JSON files found in {processed_dir}"
            )

        self.chunks = []

        for json_file in json_files:
            with json_file.open("r", encoding="utf-8") as file:
                document_chunks = json.load(file)

            self.chunks.extend(document_chunks)

        texts = [chunk["text"] for chunk in self.chunks]

        print(f"Loaded chunks: {len(texts)}")
        print("Creating embeddings...")

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        print(f"Vector dimension: {dimension}")
        print(f"Vectors indexed: {self.index.ntotal}")

    def save(self, index_dir: str | Path):
        """
        Save the FAISS index and chunk metadata to disk.
        """

        if self.index is None:
            raise RuntimeError(
                "Cannot save an empty vector index."
            )

        index_dir = Path(index_dir)
        index_dir.mkdir(parents=True, exist_ok=True)

        index_path = index_dir / "telarc.faiss"
        chunks_path = index_dir / "chunks.json"

        faiss.write_index(
            self.index,
            str(index_path),
        )

        with chunks_path.open("w", encoding="utf-8") as file:
            json.dump(
                self.chunks,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print(f"FAISS index saved to: {index_path}")
        print(f"Chunk metadata saved to: {chunks_path}")

    def load(self, index_dir: str | Path):
        """
        Load a previously saved FAISS index and chunk metadata.
        """

        index_dir = Path(index_dir)

        index_path = index_dir / "telarc.faiss"
        chunks_path = index_dir / "chunks.json"

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not chunks_path.exists():
            raise FileNotFoundError(
                f"Chunk metadata not found: {chunks_path}"
            )

        self.index = faiss.read_index(
            str(index_path)
        )

        with chunks_path.open("r", encoding="utf-8") as file:
            self.chunks = json.load(file)

        if self.index.ntotal != len(self.chunks):
            raise ValueError(
                "FAISS index size does not match "
                "the number of stored chunks."
            )

        print(f"Loaded vectors: {self.index.ntotal}")
        print(f"Loaded chunks: {len(self.chunks)}")

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search the vector index for the most relevant chunks.
        """

        if self.index is None:
            raise RuntimeError(
                "Vector index has not been built."
            )

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index == -1:
                continue

            chunk = self.chunks[index].copy()

            chunk["score"] = float(score)

            results.append(chunk)

        return results