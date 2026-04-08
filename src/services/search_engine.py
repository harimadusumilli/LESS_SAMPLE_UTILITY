"""Search engine service for semantic search over indexed PDF documents.

Provides high-level search functionality that combines query embedding,
vector similarity search, and result ranking.
"""

import logging
from pathlib import Path
from typing import List, Optional

from src.models.search_result import SearchResult
from src.services.vector_db import VectorDB


class SearchEngine:
    """Search engine for semantic search over indexed documents."""

    def __init__(self, index_path: str):
        """Initialize search engine with index path.

        Args:
            index_path: Path to the ChromaDB index directory
        """
        self.logger = logging.getLogger(__name__)
        self.vector_db = VectorDB(index_path=index_path)

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        min_score: Optional[float] = None,
    ) -> List[SearchResult]:
        """Execute semantic search query.

        Args:
            query_text: Search query string
            top_k: Maximum number of results to return
            min_score: Minimum relevance score threshold (0.0-1.0)

        Returns:
            List of SearchResult objects, ranked by relevance
        """
        self.logger.info(f"Executing search query: '{query_text}' (top_k={top_k}, min_score={min_score})")

        # Perform vector search
        results = self.vector_db.search(query_text, n_results=top_k, min_score=min_score)

        self.logger.info(f"Found {len(results)} results")
        return results

    def rank_results(
        self,
        results: List[SearchResult],
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> List[SearchResult]:
        """Rank and filter search results.

        Args:
            results: Raw search results from vector database
            top_k: Maximum number of results to return
            min_score: Minimum relevance score threshold

        Returns:
            Filtered and ranked results
        """
        # Results are already ranked by VectorDB.search()
        # Apply additional filtering if needed

        filtered_results = results

        # Apply minimum score filter (if not already done by vector_db)
        if min_score is not None:
            filtered_results = [
                result for result in filtered_results
                if result.relevance_score >= min_score
            ]

        # Apply top-k limit
        if top_k is not None:
            filtered_results = filtered_results[:top_k]

        return filtered_results