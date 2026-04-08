"""TextChunk model for representing indexed text chunks.

Represents individual text chunks extracted from PDFs for vector indexing.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TextChunk:
    """A text chunk extracted from a PDF for indexing.

    Attributes:
        id: Unique identifier for this chunk
        document_id: ID of the parent PDF document
        content: The actual text content of this chunk
        file_path: Path to the source PDF file
        page_number: Page number in the PDF (optional)
        sentence_index: Index of this sentence within the document
        total_sentences: Total number of sentences in the document
    """

    id: str
    document_id: str
    content: str
    file_path: Path
    page_number: Optional[int]
    sentence_index: int
    total_sentences: int

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("id must be a non-empty string")

        if not self.document_id or not isinstance(self.document_id, str):
            raise ValueError("document_id must be a non-empty string")

        if not self.content or not isinstance(self.content, str):
            raise ValueError("content must be a non-empty string")

        self.file_path = Path(self.file_path)

        if self.page_number is not None and self.page_number < 1:
            raise ValueError("page_number must be positive if provided")

        if self.sentence_index < 0:
            raise ValueError("sentence_index must be non-negative")

        if self.total_sentences < 1:
            raise ValueError("total_sentences must be positive")

    def to_chroma_format(self) -> tuple[str, dict, str]:
        """Convert to format expected by VectorDB.add_documents().

        Returns:
            Tuple of (id, metadata_dict, content)
        """
        metadata = {
            "document_id": self.document_id,
            "file_path": str(self.file_path),
            "sentence_index": self.sentence_index,
            "total_sentences": self.total_sentences,
        }
        # Only include page_number if it's not None (ChromaDB doesn't accept None in metadata)
        if self.page_number is not None:
            metadata["page_number"] = self.page_number
        return (self.id, metadata, self.content)