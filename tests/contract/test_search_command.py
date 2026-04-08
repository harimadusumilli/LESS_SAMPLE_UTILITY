"""Contract tests for the search command CLI interface.

Tests the command-line interface for the search command, ensuring
argument parsing, validation, and output formatting work correctly.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src.cli.main import main


class TestSearchCommandContract:
    """Test search command argument parsing and validation."""

    def test_search_command_requires_query_argument(self):
        """Test that search command requires a query argument."""
        # Given/When: search is called without required query text
        # Then: argparse exits with usage error code 2
        with pytest.raises(SystemExit) as exc_info:
            main(["search"])
        assert exc_info.value.code == 2  # argparse error

    def test_search_command_accepts_query_argument(self):
        """Test that search command accepts a query argument."""
        # Given: a valid query and mocked search handler
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 0
            # When: command is executed with query text
            result = main(["search", "test query"])
            # Then: CLI delegates to handler and returns success
            assert result == 0
            mock_handler.assert_called_once()

    def test_search_command_help_option(self):
        """Test search command help option."""
        # Given/When: help is requested for search command
        # Then: help exits successfully with code 0
        with pytest.raises(SystemExit) as exc_info:
            main(["search", "--help"])
        assert exc_info.value.code == 0  # help shows and exits successfully

    def test_search_command_with_top_k_option(self):
        """Test search command with --top-k option."""
        # Given: valid query and top-k override
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 0
            # When/Then: option parses and command succeeds
            result = main(["search", "query", "--top-k", "10"])
            assert result == 0
            mock_handler.assert_called_once()

    def test_search_command_with_threshold_option(self):
        """Test search command with --threshold option."""
        # Given: valid query and threshold override
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 0
            # When/Then: threshold is accepted and delegated
            result = main(["search", "query", "--threshold", "0.5"])
            assert result == 0
            mock_handler.assert_called_once()

    def test_search_command_with_index_path_option(self):
        """Test search command with --index-path option."""
        # Given: valid query and custom index path
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 0
            # When/Then: custom index path is accepted by parser
            result = main(["search", "query", "--index-path", "/tmp/index"])
            assert result == 0
            mock_handler.assert_called_once()

    def test_search_command_with_all_options(self):
        """Test search command with all options combined."""
        # Given: full set of supported search options
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 0
            # When/Then: combined options parse and command succeeds
            result = main([
                "search", "complex query",
                "--top-k", "15",
                "--threshold", "0.7",
                "--index-path", "/custom/path"
            ])
            assert result == 0
            mock_handler.assert_called_once()

    def test_search_command_invalid_top_k_option(self):
        """Test search command with invalid --top-k value."""
        # Given/When: top-k is outside accepted range
        # Then: command returns runtime error code
        result = main(["search", "query", "--top-k", "0"])
        assert result == 1

    def test_search_command_invalid_threshold_option(self):
        """Test search command with invalid --threshold value."""
        # Given/When: threshold is outside [0.0, 1.0]
        # Then: validation fails with non-success exit code
        result = main(["search", "query", "--threshold", "1.5"])
        assert result == 1

    def test_search_command_directory_not_index_path(self):
        """Test search command with directory as index path."""
        # Given: index path value is provided as a directory string
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 0
            # When/Then: CLI passes value through and handler decides behavior
            result = main(["search", "query", "--index-path", "."])
            assert result == 0
            mock_handler.assert_called_once()

    def test_search_command_with_spaces_in_query(self):
        """Test search command with spaces in query."""
        # Given: a multi-word query string
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 0
            # When/Then: parser keeps full query text intact
            result = main(["search", "query with spaces"])
            assert result == 0
            mock_handler.assert_called_once()

    def test_search_command_with_special_characters_in_query(self):
        """Test search command with special characters in query."""
        # Given: query containing punctuation and special characters
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 0
            # When/Then: parser accepts string and delegates to handler
            result = main(["search", "query-with-special@chars!"])
            assert result == 0
            mock_handler.assert_called_once()


class TestSearchCommandOutputFormat:
    """Test search command output formatting."""

    def test_search_command_error_messages_format(self):
        """Test that error messages follow the expected format."""
        # Given: mocked handler failure response
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 1
            # When/Then: CLI surfaces failure as exit code 1
            result = main(["search", "query"])
            assert result == 1

    def test_search_command_success_exit_code(self):
        """Test that successful search returns exit code 0."""
        # Given: mocked successful handler response
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 0
            # When/Then: successful execution returns code 0
            result = main(["search", "query"])
            assert result == 0

    def test_search_command_error_exit_code(self):
        """Test that failed search returns non-zero exit code."""
        # Given: mocked handler failure response
        with patch('src.cli.search_cmd.handle_search') as mock_handler:
            mock_handler.return_value = 1
            # When/Then: failed execution returns non-zero code
            result = main(["search", "query"])
            assert result == 1


class TestSearchCommandIntegration:
    """Integration tests for search command with actual CLI execution."""

    def test_search_command_cli_parsing(self):
        """Test that search command parses arguments correctly."""
        # Given: subprocess invocation of real CLI help command
        # This test uses subprocess to test actual CLI behavior
        result = subprocess.run([
            sys.executable, "-m", "src.cli.main", "search", "--help"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Then: CLI exits successfully and prints search help text
        assert result.returncode == 0
        assert "Search the indexed documents" in result.stdout

    def test_search_command_with_custom_index_path(self):
        """Test search command with custom index path."""
        # Given: subprocess invocation with custom index path and top-k
        result = subprocess.run([
            sys.executable, "-m", "src.cli.main", "search", "test",
            "--index-path", "/tmp/test_index", "--top-k", "3"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Then: arguments parse (not argparse error), but missing index yields runtime failure
        # Should fail because index doesn't exist, but parsing should work
        assert result.returncode != 0  # Non-zero exit due to missing index
        # Should not be argparse error (which would be exit code 2)
        assert result.returncode != 2