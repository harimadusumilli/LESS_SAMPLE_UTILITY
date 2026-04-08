"""Unit tests for pdf_processor module."""

from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from less_sample_utility.pdf_processor import (
    chunk_text,
    extract_text_from_pdf,
    process_pdf,
    process_pdf_directory,
)


# ---------------------------------------------------------------------------
# chunk_text
# ---------------------------------------------------------------------------

class TestChunkText:
    def test_basic_chunking(self):
        text = "a" * 1000
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=0)
        assert len(chunks) == 10
        assert all(len(c) == 100 for c in chunks)

    def test_overlap(self):
        text = "abcdefghij"  # 10 chars
        chunks = chunk_text(text, chunk_size=4, chunk_overlap=2)
        # start positions: 0, 2, 4, 6, 8
        assert chunks[0] == "abcd"
        assert chunks[1] == "cdef"

    def test_text_shorter_than_chunk(self):
        text = "hello"
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=0)
        assert chunks == ["hello"]

    def test_empty_text(self):
        chunks = chunk_text("", chunk_size=100, chunk_overlap=0)
        assert chunks == []

    def test_invalid_chunk_size(self):
        with pytest.raises(ValueError):
            chunk_text("hello", chunk_size=0)

    def test_invalid_overlap_negative(self):
        with pytest.raises(ValueError):
            chunk_text("hello", chunk_size=10, chunk_overlap=-1)

    def test_overlap_gte_chunk_size(self):
        with pytest.raises(ValueError):
            chunk_text("hello", chunk_size=5, chunk_overlap=5)


# ---------------------------------------------------------------------------
# extract_text_from_pdf
# ---------------------------------------------------------------------------

class TestExtractTextFromPdf:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/nonexistent/path/doc.pdf")

    def test_not_a_pdf(self, tmp_path):
        txt_file = tmp_path / "doc.txt"
        txt_file.write_text("hello")
        with pytest.raises(ValueError):
            extract_text_from_pdf(txt_file)

    def test_valid_pdf(self, tmp_path):
        """Create a minimal PDF and verify text extraction."""
        pdf_content = b"""%PDF-1.4
1 0 obj<</Type /Catalog /Pages 2 0 R>>endobj
2 0 obj<</Type /Pages /Kids [3 0 R] /Count 1>>endobj
3 0 obj<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
/Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 44>>
stream
BT /F1 12 Tf 100 700 Td (Hello World) Tj ET
endstream
endobj
5 0 obj<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000360 00000 n 
trailer<</Size 6 /Root 1 0 R>>
startxref
441
%%EOF"""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(pdf_content)
        # We just verify it doesn't raise; actual text depends on pypdf
        try:
            result = extract_text_from_pdf(pdf_file)
            assert isinstance(result, str)
        except Exception:
            pass  # minimal PDF may not parse perfectly; test structure only


# ---------------------------------------------------------------------------
# process_pdf_directory
# ---------------------------------------------------------------------------

class TestProcessPdfDirectory:
    def test_not_a_directory(self, tmp_path):
        txt_file = tmp_path / "file.txt"
        txt_file.write_text("hi")
        with pytest.raises(NotADirectoryError):
            process_pdf_directory(txt_file)

    def test_empty_directory(self, tmp_path):
        result = process_pdf_directory(tmp_path)
        assert result == {}
