"""PDF processor: extract text from PDF files and split it into chunks."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pypdf import PdfReader


DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Return the full text content of a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Concatenated text of all pages.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the file is not a valid PDF.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)
    return "\n".join(pages_text)


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """Split *text* into overlapping chunks of *chunk_size* characters.

    Args:
        text: The input text to chunk.
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be a non-negative integer.")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += chunk_size - chunk_overlap
    return chunks


def process_pdf(
    pdf_path: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """Extract text from a PDF and return it as a list of chunks.

    Args:
        pdf_path: Path to the PDF file.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of text chunks extracted from the PDF.
    """
    text = extract_text_from_pdf(pdf_path)
    return chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def process_pdf_directory(
    directory: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> dict[str, List[str]]:
    """Process all PDF files in *directory* and return a mapping of filename → chunks.

    Args:
        directory: Path to the directory containing PDF files.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        Dictionary mapping each PDF filename to its list of text chunks.

    Raises:
        NotADirectoryError: If *directory* is not a valid directory.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    results: dict[str, List[str]] = {}
    for pdf_file in sorted(directory.glob("*.pdf")):
        results[pdf_file.name] = process_pdf(
            pdf_file, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
    return results
