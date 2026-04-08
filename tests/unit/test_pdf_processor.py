"""Unit tests for PDF processing service.

Tests PDF text extraction, sentence chunking, and directory scanning functionality.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.services.pdf_processor import PDFProcessor
from src.models.text_chunk import TextChunk


class TestPDFProcessor:
    """Unit tests for PDFProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create PDF processor instance."""
        return PDFProcessor()

    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """Create a sample PDF file path."""
        return tmp_path / "sample.pdf"

    def test_scan_directory_finds_pdf_files(self, processor, tmp_path):
        """Test that scan_directory finds PDF files recursively."""
        # Given: a directory tree containing PDF and non-PDF files
        # Create test directory structure
        root_dir = tmp_path / "docs"
        root_dir.mkdir()

        # Create subdirectories
        sub_dir = root_dir / "subdir"
        sub_dir.mkdir()

        # Create PDF files
        pdf1 = root_dir / "doc1.pdf"
        pdf1.write_text("dummy pdf content")

        pdf2 = sub_dir / "doc2.pdf"
        pdf2.write_text("dummy pdf content")

        # Create non-PDF file (should be ignored)
        txt_file = root_dir / "notes.txt"
        txt_file.write_text("text content")

        # When: scanning for PDF files recursively
        # Scan directory
        pdf_files = processor.scan_directory(root_dir)

        # Then: only PDF files are returned
        # Should find both PDF files
        assert len(pdf_files) == 2
        assert pdf1 in pdf_files
        assert pdf2 in pdf_files
        assert txt_file not in pdf_files

    def test_scan_directory_case_insensitive_extension(self, processor, tmp_path):
        """Test that scan_directory finds PDFs regardless of case."""
        # Given: files with mixed-case PDF extensions
        root_dir = tmp_path / "docs"
        root_dir.mkdir()

        # Create PDFs with different case extensions
        pdf1 = root_dir / "doc1.PDF"
        pdf1.write_text("dummy")

        pdf2 = root_dir / "doc2.Pdf"
        pdf2.write_text("dummy")

        # When: scanning the directory
        pdf_files = processor.scan_directory(root_dir)

        # Then: all valid PDFs are discovered
        assert len(pdf_files) == 2
        assert pdf1 in pdf_files
        assert pdf2 in pdf_files

    def test_scan_directory_nonexistent_directory(self, processor):
        """Test that scan_directory raises ValueError for nonexistent directory."""
        # Given: a path that does not exist
        nonexistent = Path("/nonexistent/directory")

        # When/Then: scan_directory reports a directory-not-found validation error
        with pytest.raises(ValueError, match="Directory does not exist"):
            processor.scan_directory(nonexistent)

    def test_scan_directory_not_a_directory(self, processor, tmp_path):
        """Test that scan_directory raises ValueError for file path."""
        # Given: a regular file path instead of a directory path
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        # When/Then: scan_directory rejects non-directory inputs
        with pytest.raises(ValueError, match="Path is not a directory"):
            processor.scan_directory(file_path)

    def test_scan_directory_permission_error(self, processor, tmp_path):
        """Test that scan_directory raises ValueError on permission error."""
        # Given: a directory whose recursive scan raises PermissionError
        root_dir = tmp_path / "docs"
        root_dir.mkdir()

        # When/Then: permission issues are converted to a user-facing ValueError
        with patch("pathlib.Path.rglob", side_effect=PermissionError("Access denied")):
            with pytest.raises(ValueError, match="Permission denied"):
                processor.scan_directory(root_dir)

    @patch("src.services.pdf_processor.PdfReader")
    def test_extract_text_successful(self, mock_pdf_reader, processor, sample_pdf_path):
        """Test successful text extraction from PDF."""
        # Given: a readable one-page PDF returned by the mocked reader
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Page content here."

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        # When: extract_text is called
        # Extract text
        result = processor.extract_text(sample_pdf_path)

        # Then: the extracted page text is returned and reader is called once
        assert result == "Page content here."
        mock_pdf_reader.assert_called_once_with(str(sample_pdf_path))

    @patch("src.services.pdf_processor.PdfReader")
    def test_extract_text_multiple_pages(self, mock_pdf_reader, processor, sample_pdf_path):
        """Test text extraction from multi-page PDF."""
        # Given: a PDF reader with two pages of text
        # Mock multiple pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content."

        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content."

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance

        # When: extract_text aggregates page text
        result = processor.extract_text(sample_pdf_path)

        # Then: page texts are joined in page order with newlines
        assert result == "Page 1 content.\nPage 2 content."

    @patch("src.services.pdf_processor.PdfReader")
    def test_extract_text_empty_pages_filtered(self, mock_pdf_reader, processor, sample_pdf_path):
        """Test that empty pages are filtered out."""
        # Given: a PDF with valid, empty, and whitespace-only pages
        # Mock pages with mixed content
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Content here."

        mock_page2 = Mock()
        mock_page2.extract_text.return_value = ""  # Empty page

        mock_page3 = Mock()
        mock_page3.extract_text.return_value = "   \n\t  "  # Whitespace only

        mock_page4 = Mock()
        mock_page4.extract_text.return_value = "More content."

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page1, mock_page2, mock_page3, mock_page4]
        mock_pdf_reader.return_value = mock_reader_instance

        # When: extract_text processes all pages
        result = processor.extract_text(sample_pdf_path)

        # Then: only non-empty page content is preserved
        assert result == "Content here.\nMore content."

    @patch("src.services.pdf_processor.PdfReader")
    def test_extract_text_no_readable_text(self, mock_pdf_reader, processor, sample_pdf_path):
        """Test error when PDF has no readable text."""
        # Given: a PDF where all extracted text is empty
        mock_page = Mock()
        mock_page.extract_text.return_value = ""

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        # When/Then: extraction fails with a clear no-text error
        with pytest.raises(ValueError, match="No readable text found"):
            processor.extract_text(sample_pdf_path)

    @patch("src.services.pdf_processor.PdfReader")
    def test_extract_text_pdf_read_error(self, mock_pdf_reader, processor, sample_pdf_path):
        """Test error handling when PDF cannot be read."""
        # Given: the underlying PDF reader throws an exception
        mock_pdf_reader.side_effect = Exception("PDF read error")

        # When/Then: read failures are wrapped as user-facing extraction errors
        with pytest.raises(ValueError, match="Failed to extract text"):
            processor.extract_text(sample_pdf_path)

    def test_chunk_text_basic_sentence_splitting(self, processor, sample_pdf_path):
        """Test basic sentence splitting functionality."""
        # Given: multi-sentence text and a document identifier
        text = "This is the first sentence. This is the second sentence! What about this question?"
        document_id = "test_doc_123"

        # When: chunk_text splits content into sentence-level chunks
        chunks = processor.chunk_text(text, sample_pdf_path, document_id)

        # Then: each chunk has expected text and metadata
        assert len(chunks) == 3

        # Check first chunk
        assert chunks[0].content == "This is the first sentence."
        assert chunks[0].file_path == sample_pdf_path
        assert chunks[0].document_id == document_id
        assert chunks[0].id == f"{document_id}_sent_0"
        assert chunks[0].sentence_index == 0
        assert chunks[0].total_sentences == 3

        # Check second chunk
        assert chunks[1].content == "This is the second sentence!"
        assert chunks[1].sentence_index == 1

        # Check third chunk
        assert chunks[2].content == "What about this question?"
        assert chunks[2].sentence_index == 2

    def test_chunk_text_filters_empty_sentences(self, processor, sample_pdf_path):
        """Test that empty and whitespace-only sentences are filtered."""
        # Given: text containing blank lines between valid sentences
        text = "Valid sentence.\n\n\nAnother valid sentence."
        document_id = "test_doc_456"

        # When: sentence chunking is performed
        chunks = processor.chunk_text(text, sample_pdf_path, document_id)

        # Then: only non-empty sentences become chunks
        assert len(chunks) == 2
        assert chunks[0].content == "Valid sentence."
        assert chunks[1].content == "Another valid sentence."

    def test_chunk_text_complex_punctuation(self, processor, sample_pdf_path):
        """Test sentence splitting with complex punctuation."""
        # Given: text containing abbreviations and varied punctuation
        text = "Dr. Smith said hello! How are you? I'm fine... Really?"
        document_id = "test_doc_789"

        # When: chunking is delegated to spaCy sentence boundaries
        chunks = processor.chunk_text(text, sample_pdf_path, document_id)

        # Then: expected sentences are represented in output chunks
        # Should split on !, ?, and potentially on ... depending on spaCy
        assert len(chunks) >= 3  # At minimum these sentences

        contents = [chunk.content for chunk in chunks]
        assert "Dr. Smith said hello!" in contents
        assert "How are you?" in contents

    def test_chunk_text_empty_input(self, processor, sample_pdf_path):
        """Test chunking with empty input text."""
        # Given: an empty text input
        document_id = "test_doc_empty"

        # When: chunk_text is called
        chunks = processor.chunk_text("", sample_pdf_path, document_id)

        # Then: no chunks are produced
        assert len(chunks) == 0

    def test_chunk_text_whitespace_only(self, processor, sample_pdf_path):
        """Test chunking with whitespace-only input."""
        # Given: input containing only whitespace characters
        document_id = "test_doc_whitespace"

        # When: chunk_text normalizes and evaluates content
        chunks = processor.chunk_text("   \n\t  ", sample_pdf_path, document_id)

        # Then: no chunks are produced from whitespace-only content
        assert len(chunks) == 0

    def test_chunk_text_single_sentence(self, processor, sample_pdf_path):
        """Test chunking with single sentence."""
        # Given: text with exactly one sentence
        text = "This is a single sentence."
        document_id = "test_doc_single"

        # When: sentence chunking runs
        chunks = processor.chunk_text(text, sample_pdf_path, document_id)

        # Then: output contains one chunk with correct sentence metadata
        assert len(chunks) == 1
        assert chunks[0].content == "This is a single sentence."
        assert chunks[0].sentence_index == 0
        assert chunks[0].total_sentences == 1