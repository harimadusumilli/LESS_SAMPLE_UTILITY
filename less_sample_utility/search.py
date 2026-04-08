"""Semantic search: query the ChromaDB vector store by meaning/context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from less_sample_utility.vector_store import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_PERSIST_DIR,
    VectorStore,
)

DEFAULT_N_RESULTS = 5


@dataclass
class SearchResult:
    """A single semantic search result.

    Attributes:
        document: The matched text chunk.
        source: Source document filename.
        chunk_index: Position of the chunk within its source document.
        distance: Embedding distance (lower ≈ more similar).
    """

    document: str
    source: str
    chunk_index: int
    distance: float


class SemanticSearch:
    """Provides semantic search over a :class:`~less_sample_utility.vector_store.VectorStore`.

    Args:
        persist_dir: ChromaDB persistence directory.
        collection_name: Collection to search.
        embedding_model: Sentence-Transformers model used for query embedding.
    """

    def __init__(
        self,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:
        self._store = VectorStore(
            persist_dir=persist_dir,
            collection_name=collection_name,
            embedding_model=embedding_model,
        )

    @property
    def store(self) -> VectorStore:
        """Underlying :class:`~less_sample_utility.vector_store.VectorStore`."""
        return self._store

    def search(
        self,
        query: str,
        n_results: int = DEFAULT_N_RESULTS,
        source_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        """Search for chunks semantically similar to *query*.

        Args:
            query: The natural-language question or search phrase.
            n_results: Maximum number of results to return.
            source_filter: If provided, restrict results to this source filename.

        Returns:
            List of :class:`SearchResult` objects ordered by ascending distance.
        """
        where = {"source": source_filter} if source_filter else None

        kwargs: dict = {
            "query_texts": [query],
            "n_results": min(n_results, max(self._store.count(), 1)),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        raw = self._store._collection.query(**kwargs)

        results: List[SearchResult] = []
        for doc, meta, dist in zip(
            raw["documents"][0],
            raw["metadatas"][0],
            raw["distances"][0],
        ):
            results.append(
                SearchResult(
                    document=doc,
                    source=meta.get("source", ""),
                    chunk_index=int(meta.get("chunk_index", 0)),
                    distance=float(dist),
                )
            )
        return results
