"""SearchResult model for ranking and presenting search results.

Represents a single matching text chunk from search results.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchResult:
    """A single search result matching a query.

    Attributes:
        chunk_id: Unique identifier of the matching text chunk
        document_id: ID of the PDF document containing this chunk
        file_path: Path to the source PDF file
        matching_text: The actual text snippet that matched
        relevance_score: Semantic similarity score (0.0-1.0, higher is better)
        rank: Result position in ranked list (1-based)
        page_number: Page number in source PDF (optional)
    """

    chunk_id: str
    document_id: str
    file_path: str
    matching_text: str
    relevance_score: float
    rank: int
    page_number: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not self.chunk_id or not isinstance(self.chunk_id, str):
            raise ValueError("chunk_id must be a non-empty string")

        if not self.document_id or not isinstance(self.document_id, str):
            raise ValueError("document_id must be a non-empty string")

        if not self.file_path or not isinstance(self.file_path, str):
            raise ValueError("file_path must be a non-empty string")

        if not self.matching_text or not isinstance(self.matching_text, str):
            raise ValueError("matching_text must be a non-empty string")

        # Validate relevance_score
        if not isinstance(self.relevance_score, (int, float)):
            raise ValueError("relevance_score must be numeric")

        if not (0.0 <= self.relevance_score <= 1.0):
            raise ValueError(f"relevance_score must be between 0 and 1, got {self.relevance_score}")

        # Validate rank
        if not isinstance(self.rank, int) or self.rank < 1:
            raise ValueError("rank must be a positive integer")

        # Validate page_number if provided
        if self.page_number is not None:
            if not isinstance(self.page_number, int) or self.page_number < 1:
                raise ValueError("page_number must be a positive integer or None")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of the search result
        """
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "file_path": self.file_path,
            "matching_text": self.matching_text,
            "relevance_score": self.relevance_score,
            "rank": self.rank,
            "page_number": self.page_number,
        }

    def formatted_snippet(self, max_length: int = 100) -> str:
        """Return formatted text snippet for display.

        Args:
            max_length: Maximum length of snippet (will truncate with ellipsis if needed)

        Returns:
            Formatted text snippet
        """
        if len(self.matching_text) <= max_length:
            return self.matching_text

        return self.matching_text[:max_length].rstrip() + "..."
