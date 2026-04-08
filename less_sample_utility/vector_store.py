"""ChromaDB vector store: persist and retrieve PDF chunk embeddings."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.utils import embedding_functions

DEFAULT_COLLECTION_NAME = "pdf_documents"
DEFAULT_PERSIST_DIR = "chroma_db"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class VectorStore:
    """Wrapper around a persistent ChromaDB collection.

    Args:
        persist_dir: Directory where ChromaDB stores its data.
        collection_name: Name of the ChromaDB collection.
        embedding_model: Sentence-Transformers model name used for embeddings.
    """

    def __init__(
        self,
        persist_dir: str | Path = DEFAULT_PERSIST_DIR,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:
        self._persist_dir = str(persist_dir)
        self._collection_name = collection_name

        self._ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )

        self._client = chromadb.PersistentClient(path=self._persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            embedding_function=self._ef,
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add_chunks(
        self,
        chunks: List[str],
        source: str,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add text *chunks* originating from *source* to the collection.

        Args:
            chunks: List of text chunks to embed and store.
            source: Identifier for the source document (e.g. filename).
            ids: Optional explicit IDs; auto-generated if not provided.
        """
        if not chunks:
            return

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in chunks]

        metadatas = [{"source": source, "chunk_index": i} for i, _ in enumerate(chunks)]

        self._collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids,
        )

    def add_pdf_chunks(self, pdf_chunks: dict[str, List[str]]) -> None:
        """Add chunks for multiple PDFs at once.

        Args:
            pdf_chunks: Mapping of filename → list of text chunks, as returned by
                :func:`~less_sample_utility.pdf_processor.process_pdf_directory`.
        """
        for source, chunks in pdf_chunks.items():
            self.add_chunks(chunks, source=source)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return the total number of documents in the collection."""
        return self._collection.count()

    def delete_collection(self) -> None:
        """Delete the entire collection (useful for a fresh start)."""
        self._client.delete_collection(self._collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            embedding_function=self._ef,
        )
