"""Feedback and logging module for LESS CLI.

Provides user-facing messages, progress reporting, and error formatting
with proper exit codes per specification.
"""
import sys
from enum import IntEnum
from typing import Optional


class ExitCode(IntEnum):
    """Standard exit codes for CLI operations."""

    SUCCESS = 0
    ERROR = 1
    INVALID_INPUT = 1


class Feedback:
    """User-facing feedback handler with structured output."""

    @staticmethod
    def info(message: str) -> None:
        """Print informational message to stdout.

        Args:
            message: Message to display
        """
        print(message, file=sys.stdout)

    @staticmethod
    def error(message: str) -> None:
        """Print error message to stderr.

        Args:
            message: Error message to display
        """
        print(f"Error: {message}", file=sys.stderr)

    @staticmethod
    def progress(message: str) -> None:
        """Print progress message to stdout.

        Args:
            message: Progress message to display
        """
        print(message, file=sys.stdout)

    @staticmethod
    def success(message: str) -> None:
        """Print success message to stdout.

        Args:
            message: Success message to display
        """
        print(message, file=sys.stdout)

    @staticmethod
    def section(title: str) -> None:
        """Print section header.

        Args:
            title: Section title
        """
        print(f"\n{title}", file=sys.stdout)


class IndexFeedback(Feedback):
    """Feedback specific to indexing operations."""

    @staticmethod
    def scanning(directory: str) -> None:
        """Report directory scanning."""
        Feedback.progress(f"Scanning directory: {directory}")

    @staticmethod
    def files_found(count: int) -> None:
        """Report number of PDF files found."""
        plural = "file" if count == 1 else "files"
        Feedback.info(f"Found {count} PDF {plural}.")

    @staticmethod
    def processing(filename: str) -> None:
        """Report file processing started."""
        Feedback.progress(f"Processing: {filename}")

    @staticmethod
    def indexed_success(filename: str, chunks: int) -> None:
        """Report successful indexing of a file."""
        Feedback.info(f"✓ Indexed {filename} ({chunks} chunks)")

    @staticmethod
    def indexed_failed(filename: str, reason: str) -> None:
        """Report failed indexing of a file."""
        Feedback.info(f"✗ Failed to index {filename}: {reason}")

    @staticmethod
    def completion(total_files: int, total_chunks: int, failed: int = 0) -> None:
        """Report indexing completion."""
        failed_msg = f", {failed} file{'s' if failed != 1 else ''} failed" if failed > 0 else ""
        Feedback.success(
            f"Indexing complete. {total_files} files indexed, {total_chunks} chunks created{failed_msg}."
        )

    @staticmethod
    def no_files_found(directory: str) -> None:
        """Report that no PDF files were found."""
        Feedback.info(f"No PDF files found in '{directory}'. Index unchanged.")


class SearchFeedback(Feedback):
    """Feedback specific to search operations."""

    @staticmethod
    def searching() -> None:
        """Report search operation started."""
        Feedback.progress("Searching index...")

    @staticmethod
    def results_found(count: int) -> None:
        """Report number of results found."""
        plural = "result" if count == 1 else "results"
        Feedback.info(f"{count} {plural} found.\n")

    @staticmethod
    def result_item(
        rank: int, file_path: str, text: str, score: float, page: Optional[int] = None
    ) -> None:
        """Print a single search result.

        Args:
            rank: Result position (1-based)
            file_path: Path to source PDF
            text: Matching text snippet
            score: Relevance score
            page: Page number (optional)
        """
        Feedback.info(f"{rank}. File: {file_path}")
        Feedback.info(f"   Text: {text}")
        page_str = f" (Page {page})" if page else ""
        Feedback.info(f"   Score: {score:.2f}{page_str}\n")

    @staticmethod
    def display_results(results: list, query: str) -> None:
        """Display search results in formatted output.

        Args:
            results: List of SearchResult objects
            query: Original search query
        """
        if not results:
            SearchFeedback.no_results_found(query)
            return

        SearchFeedback.results_found(len(results))

        for result in results:
            SearchFeedback.result_item(
                rank=result.rank,
                file_path=result.file_path,
                text=result.formatted_snippet(),
                score=result.relevance_score,
                page=result.page_number,
            )

    @staticmethod
    def no_results_found(query: str) -> None:
        """Report that no results were found."""
        Feedback.info(
            f"Query: '{query}'\nNo results found. Try a broader query or index more documents."
        )

    @staticmethod
    def no_index() -> None:
        """Report that no index exists."""
        Feedback.error("No index found. Run 'less index <directory>' to get started.")

    @staticmethod
    def empty_index(query: str) -> None:
        """Report that index is empty."""
        Feedback.info(
            f"Query: '{query}'\nNo documents indexed. Run 'less index <directory>' to add documents."
        )


class ErrorMessages:
    """Standardized error messages per specification."""

    DIRECTORY_NOT_FOUND = "Directory '{path}' not found or not readable."
    DIRECTORY_NOT_READABLE = "Directory '{path}' is not readable. Check permissions."
    DISK_FULL = "Not enough disk space to store index."
    QUERY_EMPTY = "Query cannot be empty."
    INDEX_NOT_FOUND = "No index found at '{path}'. Run 'less index <directory>' first."
    INVALID_TOP_K = "--top-k must be a positive integer."
    QUERY_PROCESSING_ERROR = "Query processing failed. {reason}"
    PDF_EXTRACTION_ERROR = "Failed to extract text from PDF. {reason}"
    CHROMADB_ERROR = "Vector database error. {reason}"


def exit_with_error(message: str, exit_code: int = ExitCode.ERROR) -> None:
    """Print error and exit with code.

    Args:
        message: Error message
        exit_code: Exit code to use
    """
    Feedback.error(message)
    sys.exit(exit_code)


def exit_success(message: Optional[str] = None) -> None:
    """Print optional message and exit successfully.

    Args:
        message: Optional success message
    """
    if message:
        Feedback.success(message)
    sys.exit(ExitCode.SUCCESS)
