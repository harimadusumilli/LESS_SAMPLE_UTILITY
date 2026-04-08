"""Pytest fixtures for LESS testing.

Provides shared test setup, temporary directories, mock objects, and sample data.
"""
import tempfile
import shutil
import time
import gc
from pathlib import Path
from typing import Generator
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def temp_index_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for ChromaDB index.

    Yields:
        Temporary directory path
    """
    tmpdir = Path(tempfile.mkdtemp())
    try:
        yield tmpdir
    finally:
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                shutil.rmtree(tmpdir)
                break
            except PermissionError:
                if attempt == max_attempts - 1:
                    break
                gc.collect()
                time.sleep(0.1)


@pytest.fixture
def sample_pdf_path() -> Generator[Path, None, None]:
    """Provide a path to a sample PDF file for testing.

    Creates a minimal valid PDF file.

    Yields:
        Path to temporary PDF file
    """
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        # Minimal valid PDF structure
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Sample PDF) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000214 00000 n
0000000301 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
394
%%EOF
"""
        f.write(pdf_content)
        pdf_path = Path(f.name)

    yield pdf_path

    # Cleanup
    pdf_path.unlink(missing_ok=True)


@pytest.fixture
def mock_vector_db() -> MagicMock:
    """Provide a mock VectorDB instance.

    Returns:
        MagicMock configured for VectorDB interface
    """
    mock = MagicMock()
    mock.add_documents = MagicMock()
    mock.search = MagicMock(
        return_value={
            "ids": [["chunk_1", "chunk_2"]],
            "documents": [["Sample text 1", "Sample text 2"]],
            "metadatas": [
                [
                    {
                        "document_id": "doc_1",
                        "file_path": "/path/to/doc1.pdf",
                        "page_number": 1,
                    },
                    {
                        "document_id": "doc_2",
                        "file_path": "/path/to/doc2.pdf",
                        "page_number": 2,
                    },
                ]
            ],
            "distances": [[0.1, 0.2]],
        }
    )
    mock.get_collection_stats = MagicMock(return_value={"count": 100})
    return mock


@pytest.fixture
def sample_query() -> str:
    """Provide a sample search query.

    Returns:
        Sample query string
    """
    return "machine learning algorithms"


@pytest.fixture
def sample_search_results() -> dict:
    """Provide sample search results matching the SearchResult model.

    Returns:
        Dictionary with search result data
    """
    return {
        "ids": [["chunk_1", "chunk_2", "chunk_3"]],
        "documents": [
            [
                "Machine learning is a subset of artificial intelligence.",
                "Algorithms are fundamental to machine learning.",
                "Deep learning uses neural networks for pattern recognition.",
            ]
        ],
        "metadatas": [
            [
                {
                    "document_id": "doc_001",
                    "file_path": "samples/ml_intro.pdf",
                    "page_number": 1,
                },
                {
                    "document_id": "doc_001",
                    "file_path": "samples/ml_intro.pdf",
                    "page_number": 3,
                },
                {
                    "document_id": "doc_002",
                    "file_path": "samples/deep_learning.pdf",
                    "page_number": 2,
                },
            ]
        ],
        "distances": [[0.15, 0.25, 0.35]],  # Lower distance = higher relevance
    }


@pytest.fixture
def sample_pdf_documents() -> list:
    """Provide sample PDFDocument data.

    Returns:
        List of PDF document metadata dictionaries
    """
    return [
        {
            "id": "doc_001",
            "file_path": "samples/doc1.pdf",
            "filename": "doc1.pdf",
            "file_size_bytes": 50000,
            "extraction_status": "success",
            "extraction_error": None,
            "total_chunks": 25,
        },
        {
            "id": "doc_002",
            "file_path": "samples/doc2.pdf",
            "filename": "doc2.pdf",
            "file_size_bytes": 75000,
            "extraction_status": "success",
            "extraction_error": None,
            "total_chunks": 35,
        },
    ]


@pytest.fixture
def mock_chroma_client() -> MagicMock:
    """Provide a mock ChromaDB client.

    Returns:
        MagicMock configured for ChromaDB Client interface
    """
    mock_collection = MagicMock()
    mock_collection.count = MagicMock(return_value=100)
    mock_collection.add = MagicMock()
    mock_collection.query = MagicMock(
        return_value={
            "ids": [["chunk_1", "chunk_2"]],
            "documents": [["text 1", "text 2"]],
            "metadatas": [[{}, {}]],
            "distances": [[0.1, 0.2]],
        }
    )

    mock_client = MagicMock()
    mock_client.get_or_create_collection = MagicMock(return_value=mock_collection)
    return mock_client


@pytest.fixture
def config_with_temp_index(temp_index_dir) -> dict:
    """Provide configuration dict with temporary index path.

    Args:
        temp_index_dir: Temporary directory fixture

    Returns:
        Configuration dictionary
    """
    return {
        "index_path": str(temp_index_dir),
        "verbose": True,
        "force": False,
    }
