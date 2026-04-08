"""PDFDocument model for representing indexed PDF files.

Tracks document metadata and indexing status.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class ExtractionStatus(str, Enum):
    """Status of PDF text extraction."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"  # Some pages extracted, some failed


@dataclass
class PDFDocument:
    """Metadata and tracking for an indexed PDF document.

    Attributes:
        file_path: Path to the PDF file on disk
        filename: Just the filename (not full path)
        file_size_bytes: Size of PDF file in bytes
        id: Unique identifier (usually based on hash of file_path)
        indexed_at: Timestamp when document was indexed
        extraction_status: Current extraction status
        extraction_error: Error message if extraction failed
        total_chunks: Number of text chunks extracted and indexed
    """

    file_path: Path
    filename: str
    file_size_bytes: int
    id: Optional[str] = None
    indexed_at: Optional[datetime] = None
    extraction_status: ExtractionStatus = ExtractionStatus.PENDING
    extraction_error: Optional[str] = None
    total_chunks: int = 0

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        self.file_path = Path(self.file_path)

        # Validate file exists and is readable
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.file_path}")

        if not self.file_path.is_file():
            raise ValueError(f"Path is not a file: {self.file_path}")

        try:
            # Check read permissions
            with open(self.file_path, "rb") as f:
                f.read(1)
        except (OSError, PermissionError) as e:
            raise PermissionError(
                f"Cannot read PDF file {self.file_path}: {e}"
            ) from e

        # Validate file_size_bytes
        if self.file_size_bytes <= 0:
            actual_size = self.file_path.stat().st_size
            if actual_size > 0:
                self.file_size_bytes = actual_size
            else:
                raise ValueError(f"PDF file is empty: {self.file_path}")

    def mark_indexed(self, chunks: int) -> None:
        """Mark document as successfully indexed.

        Args:
            chunks: Number of chunks extracted
        """
        self.extraction_status = ExtractionStatus.SUCCESS
        self.total_chunks = chunks
        self.indexed_at = datetime.now()
        self.extraction_error = None

    def mark_failed(self, error: str) -> None:
        """Mark document as failed indexing.

        Args:
            error: Error message describing the failure
        """
        self.extraction_status = ExtractionStatus.FAILED
        self.extraction_error = error
        self.indexed_at = datetime.now()

    def mark_partial(self, chunks: int, error: str) -> None:
        """Mark document as partially indexed.

        Args:
            chunks: Number of chunks successfully extracted
            error: Error message describing partial failure
        """
        self.extraction_status = ExtractionStatus.PARTIAL
        self.total_chunks = chunks
        self.extraction_error = error
        self.indexed_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for storage/serialization.

        Returns:
            Dictionary representation of document metadata
        """
        return {
            "id": self.id,
            "file_path": str(self.file_path),
            "filename": self.filename,
            "file_size_bytes": self.file_size_bytes,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "extraction_status": self.extraction_status.value,
            "extraction_error": self.extraction_error,
            "total_chunks": self.total_chunks,
        }
