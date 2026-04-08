"""LESS CLI main entry point and command routing.

Provides argument parsing, command dispatch, and top-level error handling.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from src.utils.feedback import Feedback, ExitCode


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.

    Returns:
        Configured ArgumentParser for LESS CLI
    """
    parser = argparse.ArgumentParser(
        prog="less",
        description="LESS: PDF Indexing and Semantic Search CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  less index ~/documents          # Index all PDFs in ~/documents
  less index . --force            # Reindex current directory
  less search "machine learning"  # Search the index
  less search "AI" --top-k 10     # Get 10 results instead of default 5
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
        help="Show version and exit",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Index command
    index_parser = subparsers.add_parser(
        "index",
        help="Index PDF files in a directory",
        description="Recursively index PDF files in the specified directory",
    )
    index_parser.add_argument(
        "directory",
        help="Directory containing PDF files to index (default: current directory)",
    )
    index_parser.add_argument(
        "--index-path",
        type=str,
        default=None,
        help="Custom path to store index (default: ~/.less/index)",
    )
    index_parser.add_argument(
        "--force",
        action="store_true",
        help="Reindex all files, overwriting existing index",
    )
    index_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress messages",
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search the indexed documents",
        description="Search the indexed documents using semantic search",
    )
    search_parser.add_argument(
        "query",
        help="Search query (will search for semantic matches)",
    )
    search_parser.add_argument(
        "--index-path",
        type=str,
        default=None,
        help="Custom path to index (default: ~/.less/index)",
    )
    search_parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of top results to return (default: 5)",
    )
    search_parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Minimum relevance score (0.0-1.0) to include in results",
    )
    search_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress messages",
    )

    return parser


def validate_index_command(args: argparse.Namespace) -> Optional[tuple[Path, dict]]:
    """Validate arguments for index command.

    Args:
        args: Parsed arguments

    Returns:
        Tuple of (directory_path, options_dict) or None if validation fails
    """
    directory = args.directory

    try:
        dir_path = Path(directory).resolve()
    except (ValueError, OSError) as e:
        Feedback.error(f"Invalid directory path '{directory}': {e}")
        return None

    if not dir_path.exists():
        Feedback.error(f"Directory does not exist: {dir_path}")
        return None

    if not dir_path.is_dir():
        Feedback.error(f"Path is not a directory: {dir_path}")
        return None

    try:
        # Check read permission by listing directory
        list(dir_path.iterdir())
    except (OSError, PermissionError) as e:
        Feedback.error(f"Cannot read directory '{dir_path}': {e}")
        return None

    options = {
        "index_path": args.index_path,
        "force": args.force,
        "verbose": args.verbose,
    }

    return dir_path, options


def validate_search_command(args: argparse.Namespace) -> Optional[dict]:
    """Validate arguments for search command.

    Args:
        args: Parsed arguments

    Returns:
        Options dict or None if validation fails
    """
    query = args.query.strip()

    if not query:
        Feedback.error("Query cannot be empty.")
        return None

    if args.top_k <= 0:
        Feedback.error(f"--top-k must be a positive integer, got {args.top_k}")
        return None

    if args.threshold is not None:
        if not (0.0 <= args.threshold <= 1.0):
            Feedback.error(
                f"--threshold must be between 0.0 and 1.0, got {args.threshold}"
            )
            return None

    options = {
        "query": query,
        "index_path": args.index_path,
        "top_k": args.top_k,
        "threshold": args.threshold,
        "verbose": args.verbose,
    }

    return options


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for LESS CLI.

    Args:
        argv: Command-line arguments (for testing; uses sys.argv if None)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # No command provided
    if not args.command:
        parser.print_help()
        return ExitCode.ERROR

    # Route to command handlers
    if args.command == "index":
        from src.cli.index_cmd import handle_index

        validated = validate_index_command(args)
        if validated is None:
            return ExitCode.ERROR

        directory, options = validated
        return handle_index(directory, **options)

    elif args.command == "search":
        from src.cli.search_cmd import handle_search

        validated = validate_search_command(args)
        if validated is None:
            return ExitCode.ERROR

        return handle_search(**validated)

    else:
        Feedback.error(f"Unknown command: {args.command}")
        return ExitCode.ERROR


if __name__ == "__main__":
    sys.exit(main())
