"""Integration tests for the full index workflow.

Tests the complete end-to-end process of indexing PDF files:
directory scanning → text extraction → sentence chunking → vector storage.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.services.pdf_processor import PDFProcessor
from src.services.vector_db import VectorDB
from src.models.pdf_document import PDFDocument


class TestIndexWorkflowIntegration:
    """Integration tests for the complete PDF indexing workflow."""

    @pytest.fixture
    def vector_db(self, temp_index_dir):
        """Create VectorDB instance with deterministic cleanup."""
        db = VectorDB(index_path=temp_index_dir)
        try:
            yield db
        finally:
            db.close()

    def test_full_index_workflow_single_pdf(self, temp_index_dir, sample_pdf_path, vector_db):
        """Test complete indexing workflow with a single PDF file."""
        # Given: one PDF and initialized processor/vector database services
        # Setup
        processor = PDFProcessor()

        # Create a dedicated directory with just one PDF
        test_dir = temp_index_dir / "single_pdf_test"
        test_dir.mkdir()
        test_pdf = test_dir / "test.pdf"
        test_pdf.touch()  # Create empty file, content will be mocked

        # Mock PDF content for consistent testing
        mock_text = "This is a test document. It contains multiple sentences. Each sentence should be chunked separately."

        # When: the full workflow runs (scan -> extract -> chunk -> store)
        with patch('src.services.pdf_processor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = mock_text
            mock_reader.return_value.pages = [mock_page]

            # Execute workflow
            pdf_files = processor.scan_directory(test_dir)
            assert len(pdf_files) == 1
            assert pdf_files[0] == test_pdf

            # Extract text
            extracted_text = processor.extract_text(test_pdf)
            assert extracted_text == mock_text

            # Create document ID
            document_id = f"pdf_{test_pdf.stem}"

            # Chunk text
            chunks = processor.chunk_text(extracted_text, test_pdf, document_id)
            assert len(chunks) == 3  # Should create 3 chunks from the 3 sentences

            # Verify chunk properties
            for i, chunk in enumerate(chunks):
                assert chunk.document_id == document_id
                assert chunk.file_path == test_pdf
                assert chunk.sentence_index == i
                assert chunk.total_sentences == 3
                assert chunk.id == f"{document_id}_sent_{i}"

            # Store in vector database
            vector_db.add_text_chunks(chunks)

            # Then: all generated chunks are persisted and reflected in stats
            # Verify storage
            stats = vector_db.get_collection_stats()
            assert stats['document_count'] == 3  # 3 chunks stored
            assert 'metadata' in stats

    def test_full_index_workflow_multiple_pdfs(self, temp_index_dir, vector_db):
        """Test complete indexing workflow with multiple PDF files."""
        # Given: two PDFs with distinct mocked contents
        # Create multiple test PDFs
        pdf_dir = temp_index_dir / "pdfs"
        pdf_dir.mkdir()

        pdf1_path = pdf_dir / "doc1.pdf"
        pdf2_path = pdf_dir / "doc2.pdf"

        # Create empty PDF files (content will be mocked)
        pdf1_path.touch()
        pdf2_path.touch()

        processor = PDFProcessor()
        # Mock different content for each PDF
        mock_texts = {
            str(pdf1_path): "First document content. With two sentences.",
            str(pdf2_path): "Second document has different text. Also two sentences."
        }

        def mock_extract_text(pdf_path: Path) -> str:
            return mock_texts[str(pdf_path)]

        # When: each PDF is scanned, extracted, chunked, and stored
        with patch('src.services.pdf_processor.PdfReader') as mock_reader:
            def mock_reader_init(pdf_path):
                mock_page = MagicMock()
                mock_page.extract_text.return_value = mock_texts[str(pdf_path)]
                mock_instance = MagicMock()
                mock_instance.pages = [mock_page]
                return mock_instance

            mock_reader.side_effect = mock_reader_init

            # Scan directory
            pdf_files = processor.scan_directory(pdf_dir)
            assert len(pdf_files) == 2
            assert pdf1_path in pdf_files
            assert pdf2_path in pdf_files

            # Process each PDF
            all_chunks = []
            for pdf_path in pdf_files:
                text = processor.extract_text(pdf_path)
                document_id = f"pdf_{pdf_path.stem}"
                chunks = processor.chunk_text(text, pdf_path, document_id)
                all_chunks.extend(chunks)

            # Should have 4 chunks total (2 sentences each from 2 docs)
            assert len(all_chunks) == 4

            # Store all chunks
            vector_db.add_text_chunks(all_chunks)

            # Then: combined chunk count and collection stats match expectations
            # Verify storage
            stats = vector_db.get_collection_stats()
            assert stats['document_count'] == 4  # 4 chunks stored
            assert 'metadata' in stats

    def test_index_workflow_handles_empty_directory(self, temp_index_dir, vector_db):
        """Test that indexing an empty directory works without errors."""
        # Given: an empty directory with no PDF files
        empty_dir = temp_index_dir / "empty"
        empty_dir.mkdir()

        processor = PDFProcessor()
        # When: scan and add operations are executed with no input files/chunks
        # Scan empty directory
        pdf_files = processor.scan_directory(empty_dir)
        assert pdf_files == []

        # No chunks to process
        vector_db.add_text_chunks([])

        # Then: collection remains empty and stats are still queryable
        # Verify empty collection
        stats = vector_db.get_collection_stats()
        assert stats['document_count'] == 0
        assert 'metadata' in stats

    def test_index_workflow_error_handling(self, temp_index_dir, sample_pdf_path, vector_db):
        """Test error handling during the indexing workflow."""
        # Given: initialized services and one sample PDF path
        processor = PDFProcessor()

        # When/Then: extraction errors are surfaced as ValueError
        # Test PDF extraction failure
        with patch('src.services.pdf_processor.PdfReader') as mock_reader:
            mock_reader.side_effect = Exception("PDF read error")

            with pytest.raises(ValueError, match="Failed to extract text"):
                processor.extract_text(sample_pdf_path)

        # Test vector DB storage failure
        from src.models.text_chunk import TextChunk
        chunks = [
            TextChunk(
                id="test_0",
                content="test",
                document_id="test",
                file_path=sample_pdf_path,
                page_number=None,
                sentence_index=0,
                total_sentences=1
            )
        ]

        # When/Then: vector storage failures are propagated to caller
        with patch.object(vector_db.collection, 'add', side_effect=Exception("Storage error")):
            with pytest.raises(Exception, match="Storage error"):
                vector_db.add_text_chunks(chunks)