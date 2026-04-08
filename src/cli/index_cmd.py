"""Index command handler for LESS CLI.

Implements the `less index <directory>` command to scan directories,
extract PDF text, chunk into sentences, and store in ChromaDB.
"""
from pathlib import Path
from typing import Optional

from src.services.pdf_processor import PDFProcessor
from src.services.vector_db import VectorDB
from src.utils.config import Config
from src.utils.feedback import ExitCode, Feedback, IndexFeedback


def handle_index(
    directory: Path,
    index_path: Optional[str] = None,
    force: bool = False,
    verbose: bool = False,
) -> int:
    """Handle the index command.

    Args:
        directory: Directory containing PDF files to index
        index_path: Custom path for index storage
        force: Whether to reindex all files
        verbose: Whether to show detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    vector_db = None
    try:
        # Resolve index path
        resolved_index_path = Config.get_index_path(index_path)
        Config.ensure_index_directory(resolved_index_path)

        # Initialize services
        pdf_processor = PDFProcessor()
        vector_db = VectorDB(resolved_index_path)

        # Scan for PDF files
        if verbose:
            IndexFeedback.scanning(str(directory))

        pdf_files = pdf_processor.scan_directory(directory)

        if not pdf_files:
            IndexFeedback.no_files_found(str(directory))
            return ExitCode.SUCCESS

        if verbose:
            IndexFeedback.files_found(len(pdf_files))

        # Process each PDF file
        total_chunks = 0
        for pdf_path in pdf_files:
            if verbose:
                IndexFeedback.processing(pdf_path.name)

            try:
                # Extract text
                text = pdf_processor.extract_text(pdf_path)
                if not text.strip():
                    if verbose:
                        IndexFeedback.indexed_failed(pdf_path.name, "no text extracted")
                    continue

                # Create document ID from file path
                doc_id = pdf_path.name

                # Chunk text into sentences
                chunks = pdf_processor.chunk_text(text, pdf_path, doc_id)

                if not chunks:
                    if verbose:
                        IndexFeedback.indexed_failed(pdf_path.name, "no chunks created")
                    continue

                # Add chunks to vector database
                vector_db.add_text_chunks(chunks)
                total_chunks += len(chunks)

                if verbose:
                    IndexFeedback.indexed_success(pdf_path.name, len(chunks))

            except Exception as e:
                Feedback.error(f"Failed to process '{pdf_path}': {e}")
                return ExitCode.ERROR

        # Report success
        IndexFeedback.completion(len(pdf_files), total_chunks)
        return ExitCode.SUCCESS

    except Exception as e:
        Feedback.error(f"Unexpected error during indexing: {e}")
        return ExitCode.ERROR
    finally:
        if vector_db is not None:
            vector_db.close()