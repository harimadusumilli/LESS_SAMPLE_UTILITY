"""Search command handler for LESS CLI.

Provides the `less search` command for querying the indexed PDF documents.
"""

import logging
from pathlib import Path
from typing import Optional

from src.services.search_engine import SearchEngine
from src.utils.config import Config
from src.utils.feedback import Feedback, IndexFeedback, SearchFeedback


def handle_search(
    query: str,
    index_path: Optional[str] = None,
    top_k: int = 5,
    threshold: Optional[float] = None,
    verbose: bool = False,
) -> int:
    """Handle the search command.

    Args:
        query: Search query string
        index_path: Custom path to index directory
        top_k: Number of results to return
        threshold: Minimum relevance score threshold
        verbose: Whether to show detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)

    try:
        # Determine index path
        if index_path:
            index_dir = Path(index_path)
        else:
            index_dir = Config.get_index_path()

        # Check if index exists
        if not index_dir.exists():
            Feedback.error(f"Index directory does not exist: {index_dir}")
            Feedback.info("Run 'less index <directory>' to create an index first.")
            return 1

        # Initialize search engine
        search_engine = SearchEngine(index_path=str(index_dir))

        # Perform search
        if verbose:
            SearchFeedback.searching()
        Feedback.info(f"Searching for: '{query}'")
        if threshold:
            Feedback.info(f"Using relevance threshold: {threshold}")

        results = search_engine.query(query, top_k=top_k, min_score=threshold)

        if not results:
            SearchFeedback.no_results_found(query)
            return 0

        # Display results
        SearchFeedback.display_results(results, query)

        return 0

    except Exception as e:
        logger.exception(f"Search failed: {e}")
        Feedback.error(f"Search failed: {e}")
        return 1