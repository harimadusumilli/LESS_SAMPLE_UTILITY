"""PDF processing service for text extraction and chunking.

Handles PDF file discovery, text extraction using PyPDF, and sentence-level
text chunking using spaCy for semantic indexing.
"""
import hashlib
import logging
from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader
import spacy

from src.models.pdf_document import PDFDocument
from src.models.text_chunk import TextChunk
from src.utils.feedback import IndexFeedback


class PDFProcessor:
    """Service for processing PDF files for indexing."""

    def __init__(self, nlp_model: Optional[spacy.Language] = None):
        """Initialize PDF processor with NLP model.

        Args:
            nlp_model: Pre-loaded spaCy model for sentence tokenization.
                      If None, will load en_core_web_sm.
        """
        self.nlp = nlp_model or spacy.load("en_core_web_sm")
        self.logger = logging.getLogger(__name__)

    def scan_directory(self, directory_path: Path) -> List[Path]:
        """Recursively scan directory for PDF files.

        Args:
            directory_path: Root directory to scan

        Returns:
            List of PDF file paths found

        Raises:
            ValueError: If directory doesn't exist or isn't readable
        """
        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")

        if not directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")

        pdf_files = []
        try:
            for file_path in directory_path.rglob("*.pdf"):
                if file_path.is_file():
                    pdf_files.append(file_path)
        except PermissionError as e:
            raise ValueError(f"Permission denied accessing directory: {e}")

        return pdf_files

    def extract_text(self, pdf_path: Path) -> str:
        """Extract text content from a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            ValueError: If PDF cannot be read or processed
        """
        try:
            reader = PdfReader(str(pdf_path))
            text_content = []

            for page in reader.pages:
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    text_content.append(text)

            full_text = "\n".join(text_content)

            if not full_text.strip():
                raise ValueError(f"No readable text found in PDF: {pdf_path}")

            return full_text

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF {pdf_path}: {e}")

    def chunk_text(
        self,
        text: str,
        source_path: Path | str,
        document_id: str | Path,
    ) -> List[TextChunk]:
        """Chunk text into sentence-level documents for indexing.

        Args:
            text: Full text content to chunk
            source_path: Original PDF file path for metadata
            document_id: Unique ID of the parent PDF document

        Returns:
            List of TextChunk objects with sentence chunks
        """
        normalized_source_path, normalized_document_id = self._normalize_chunk_args(
            source_path, document_id
        )

        # Use spaCy for sentence tokenization
        doc = self.nlp(text)

        chunks = []
        sentence_count = 0

        for sent in doc.sents:
            sentence_text = sent.text.strip()

            # Skip empty or whitespace-only sentences
            if not sentence_text:
                continue

            # Create text chunk (total_sentences will be updated after counting)
            chunk = TextChunk(
                id=f"{normalized_document_id}_sent_{sentence_count}",
                document_id=normalized_document_id,
                content=sentence_text,
                file_path=normalized_source_path,
                page_number=None,  # Could be enhanced to track page numbers
                sentence_index=sentence_count,
                total_sentences=1  # Temporary value, will be updated
            )

            chunks.append(chunk)
            sentence_count += 1

        # Update total_sentences for all chunks
        for chunk in chunks:
            chunk.total_sentences = sentence_count

        return chunks

    def _normalize_chunk_args(
        self,
        source_path: Path | str,
        document_id: str | Path,
    ) -> tuple[Path, str]:
        """Normalize chunk_text arguments while preserving compatibility.

        Supports both call orders:
        - chunk_text(text, source_path, document_id)
        - chunk_text(text, document_id, source_path)
        """
        if isinstance(source_path, (str, Path)) and isinstance(document_id, (str, Path)):
            source_is_path = isinstance(source_path, Path)
            doc_is_path = isinstance(document_id, Path)

            if source_is_path and not doc_is_path:
                return source_path, str(document_id)

            if not source_is_path and doc_is_path:
                return document_id, str(source_path)

        return Path(source_path), str(document_id)