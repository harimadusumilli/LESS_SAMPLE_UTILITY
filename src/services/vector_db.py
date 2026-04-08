"""ChromaDB wrapper service for vector storage and semantic search.

Provides a persistence layer for document embeddings and search functionality
using ChromaDB for local storage.
"""
from pathlib import Path
from typing import Any, Optional
import gc
import chromadb

from src.models.search_result import SearchResult
from src.models.text_chunk import TextChunk


class VectorDB:
    """Wrapper around ChromaDB for consistent interface.

    Manages connection to ChromaDB, handles document storage and retrieval,
    and provides semantic search functionality.
    """

    def __init__(self, index_path: Path) -> None:
        """Initialize ChromaDB connection.

        Args:
            index_path: Path to ChromaDB persistence directory

        Raises:
            OSError: If index path is not accessible
        """
        self.index_path = Path(index_path)

        # Ensure index directory exists
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB with persistent storage using new API
        self.client = chromadb.PersistentClient(path=str(self.index_path))

        # Get or create the collection for PDF documents
        self.collection = self.client.get_or_create_collection(
            name="pdf_documents",
            metadata={"description": "Indexed PDF documents and their embeddings"},
        )

    def add_text_chunks(self, chunks: list[TextChunk]) -> None:
        """Add text chunks to the vector database.

        Args:
            chunks: List of TextChunk objects to index

        Raises:
            ValueError: If chunks list is empty or invalid
            Exception: If ChromaDB operation fails
        """
        if not chunks:
            return  # Nothing to add

        # Convert TextChunk objects to ChromaDB format
        ids = []
        metadatas = []
        documents = []

        for chunk in chunks:
            chunk_id, metadata, content = chunk.to_chroma_format()
            ids.append(chunk_id)
            metadatas.append(metadata)
            documents.append(content)

        # Use existing add_documents method
        self.add_documents(ids, metadatas, documents)

    def update_metadata(self, metadata: dict[str, Any]) -> None:
        """Update collection metadata.

        Args:
            metadata: Dict of metadata to update

        Raises:
            Exception: If ChromaDB operation fails
        """
        self.collection.modify(metadata=metadata)

    def add_documents(
        self, ids: list[str], metadatas: list[dict[str, Any]], documents: list[str]
    ) -> None:
        """Add documents (chunks) to the vector database.

        Args:
            ids: List of unique chunk identifiers
            metadatas: List of metadata dicts (contains file_path, page_number, etc.)
            documents: List of text chunks to embed and store

        Raises:
            ValueError: If ids, metadatas, and documents have different lengths
            Exception: If ChromaDB operation fails
        """
        if not (len(ids) == len(metadatas) == len(documents)):
            raise ValueError("ids, metadatas, and documents must have same length")

        if len(ids) == 0:
            return  # Nothing to add

        # ChromaDB auto-generates embeddings using default embedding function
        self.collection.add(ids=ids, metadatas=metadatas, documents=documents)

    def search(
        self, query_text: str, n_results: int = 5, min_score: Optional[float] = None
    ) -> list[SearchResult]:
        """Search for documents semantically similar to query.

        Args:
            query_text: Query string to embed and search
            n_results: Number of results to return (default 5)
            min_score: Minimum relevance score threshold (optional)

        Returns:
            List of SearchResult objects ranked by relevance

        Raises:
            ValueError: If query is empty or n_results is invalid
            Exception: If ChromaDB operation fails
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query cannot be empty")

        if n_results <= 0:
            raise ValueError("n_results must be positive")

        results = self.collection.query(
            query_texts=[query_text], n_results=n_results, include=["distances", "metadatas", "documents"]
        )

        # Convert ChromaDB results to SearchResult objects
        search_results = []

        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                # Convert distance to similarity score (higher is better)
                similarity_score = 1.0 - distance

                # Skip results below minimum score threshold
                if min_score is not None and similarity_score < min_score:
                    continue

                metadata = results["metadatas"][0][i]
                content = results["documents"][0][i]

                search_result = SearchResult(
                    chunk_id=chunk_id,
                    document_id=metadata["document_id"],
                    file_path=metadata["file_path"],
                    matching_text=content,
                    relevance_score=similarity_score,
                    rank=len(search_results) + 1,  # 1-based ranking
                    page_number=metadata.get("page_number"),
                )

                search_results.append(search_result)

        return search_results

    def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics about the indexed collection.

        Returns:
            Dict with 'document_count' and 'metadata'
        """
        stats = {
            "document_count": self.collection.count(),
            "metadata": self.collection.metadata,
        }
        return stats

    def delete_document(self, document_id: str) -> None:
        """Delete a document (all its chunks) from the index.

        Args:
            document_id: Document ID to delete

        Raises:
            Exception: If deletion fails
        """
        # Find all chunks with this document_id in metadata
        self.collection.delete(
            where={"document_id": {"$eq": document_id}},
        )

    def clear_index(self) -> None:
        """Clear entire index (all documents and chunks).

        WARNING: This is destructive and cannot be undone without reindexing.
        """
        if self.collection.count() > 0:
            self.client.delete_collection(name="pdf_documents")
            self.collection = self.client.get_or_create_collection(
                name="pdf_documents",
                metadata={"description": "Indexed PDF documents and their embeddings"},
            )

    def persist(self) -> None:
        """Explicitly persist index to disk.

        ChromaDB auto-persists with duckdb+parquet backend, but this ensures
        any pending writes are flushed.
        """
        if hasattr(self.client, "persist"):
            self.client.persist()

    def close(self) -> None:
        """Best-effort cleanup of ChromaDB resources.

        This is primarily used by tests on Windows where sqlite files can
        remain locked until references are released and garbage collected.
        """
        self.persist()
        self.collection = None
        self.client = None
        gc.collect()
