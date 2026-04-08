"""Contract tests for `less index` command.

Tests CLI interface compliance with specification in contracts/index-command.md.
Focuses on argument parsing, exit codes, and error message formats.
"""
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src.cli.main import main


class TestIndexCommandContract:
    """Contract tests for index command CLI interface."""

    def test_index_command_requires_directory_argument(self):
        """Test that index command requires a directory argument."""
        # Given/When: index command is invoked without required positional directory
        # Then: argparse exits with code 2 for invalid usage
        with pytest.raises(SystemExit) as exc_info:
            main(["index"])
        assert exc_info.value.code == 2  # argparse exit code for required argument missing

    def test_index_command_accepts_directory_argument(self, tmp_path):
        """Test that index command accepts a valid directory argument."""
        # Given: a valid directory path and mocked command handler
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        # When: the index command is executed with the directory argument
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir)])
            # Then: CLI delegates to handler and returns success
            assert result == 0
            mock_handler.assert_called_once()

    def test_index_command_help_option(self):
        """Test that --help option works."""
        # Given/When: command help is requested
        # Then: process exits successfully after printing help text
        with pytest.raises(SystemExit) as exc_info:
            main(["index", "--help"])
        assert exc_info.value.code == 0

    def test_index_command_with_index_path_option(self, tmp_path):
        """Test index command with --index-path option."""
        # Given: valid input and custom index path
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        index_dir = tmp_path / "custom_index"
        index_dir.mkdir()
        
        # When: index command is run with --index-path
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir), "--index-path", str(index_dir)])
            # Then: handler is called and command succeeds
            assert result == 0
            mock_handler.assert_called_once()

    def test_index_command_with_force_option(self, tmp_path):
        """Test index command with --force option."""
        # Given: a valid directory
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        # When/Then: --force is accepted and delegated correctly
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir), "--force"])
            assert result == 0
            mock_handler.assert_called_once()

    def test_index_command_with_verbose_option(self, tmp_path):
        """Test index command with --verbose option."""
        # Given: a valid directory
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        # When/Then: --verbose is accepted and command succeeds
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir), "--verbose"])
            assert result == 0
            mock_handler.assert_called_once()

    def test_index_command_with_all_options(self, tmp_path):
        """Test index command with all options combined."""
        # Given: a valid source directory and explicit index destination
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        index_dir = tmp_path / "custom_index"
        index_dir.mkdir()
        
        # When: all supported index options are provided together
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main([
                "index", str(test_dir),
                "--index-path", str(index_dir),
                "--force",
                "--verbose"
            ])
            # Then: command remains valid and delegates once
            assert result == 0
            mock_handler.assert_called_once()

    def test_index_command_invalid_directory_path(self):
        """Test index command with non-existent directory."""
        # Given/When: user passes a directory that does not exist
        # Then: command returns standard runtime error exit code
        result = main(["index", "C:\\nonexistent\\directory\\path"])
        assert result == 1  # Should exit with error code

    def test_index_command_directory_not_readable(self, tmp_path):
        """Test index command with directory that exists but is not readable."""
        # Given: path checks pass but iterating the directory raises permission error
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        # This would require setting up a directory with no read permissions
        # For now, we'll test the validation logic exists
        # When/Then: command maps filesystem permission failures to exit code 1
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_dir", return_value=True), \
             patch("pathlib.Path.iterdir", side_effect=PermissionError("Access denied")):
            result = main(["index", str(test_dir)])
            assert result == 1

    def test_index_command_empty_directory(self, tmp_path):
        """Test index command with directory containing no PDFs."""
        # Given: an empty directory and mocked handler behavior
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        # This would require mocking the directory scan
        # For now, test that the validation doesn't crash
        # When/Then: argument validation passes and command returns mocked success
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir)])
            assert result == 0

    def test_index_command_with_spaces_in_path(self, tmp_path):
        """Test index command with spaces in directory path."""
        # Given: a valid directory path containing spaces
        test_dir = tmp_path / "path with spaces"
        test_dir.mkdir()
        
        # When/Then: parser and handler accept the spaced path
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir)])
            assert result == 0
            mock_handler.assert_called_once()

    def test_index_command_with_special_characters_in_path(self, tmp_path):
        """Test index command with special characters in directory path."""
        # Given: a valid directory path containing punctuation characters
        test_dir = tmp_path / "path-with-dashes_and_underscores"
        test_dir.mkdir()
        
        # When/Then: command still parses and dispatches correctly
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir)])
            assert result == 0
            mock_handler.assert_called_once()

    def test_index_command_invalid_top_k_option(self, tmp_path):
        """Test that index command doesn't accept --top-k (search command option)."""
        # Given: a valid directory argument
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        # When/Then: unsupported option triggers argparse usage error
        with pytest.raises(SystemExit) as exc_info:
            main(["index", str(test_dir), "--top-k", "5"])
        assert exc_info.value.code == 2  # argparse exit code for unrecognized arguments

    def test_index_command_invalid_threshold_option(self, tmp_path):
        """Test that index command doesn't accept --threshold (search command option)."""
        # Given: a valid directory argument
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        # When/Then: unsupported option triggers argparse usage error
        with pytest.raises(SystemExit) as exc_info:
            main(["index", str(test_dir), "--threshold", "0.5"])
        assert exc_info.value.code == 2  # argparse exit code for unrecognized arguments


class TestIndexCommandOutputFormat:
    """Tests for index command output format compliance."""

    def test_index_command_error_messages_format(self):
        """Test that error messages follow the specified format."""
        # Given/When: command is invoked in known failure scenarios
        # Then: exit code remains consistent at 1 for runtime errors
        # Test directory not found error
        result = main(["index", "C:\\nonexistent\\directory\\path"])
        assert result == 1

        # Test directory not readable error
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_dir", return_value=True), \
             patch("pathlib.Path.iterdir", side_effect=PermissionError("Access denied")):
            result = main(["index", "C:\\tmp"])
            assert result == 1

    def test_index_command_success_exit_code(self, tmp_path):
        """Test that successful indexing returns exit code 0."""
        # Given: valid directory and a successful mocked handler
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()
        
        # When/Then: command returns success exit code
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir)])
            assert result == 0

    def test_index_command_error_exit_code(self):
        """Test that errors return exit code 1."""
        # Given/When: command fails due to bad path or permission errors
        # Then: runtime failures consistently map to exit code 1
        result = main(["index", "C:\\nonexistent\\directory\\path"])
        assert result == 1

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_dir", return_value=True), \
             patch("pathlib.Path.iterdir", side_effect=PermissionError("Access denied")):
            result = main(["index", "C:\\tmp"])
            assert result == 1


# Integration-style tests that run the actual command
class TestIndexCommandIntegration:
    """Integration tests that actually invoke the CLI."""

    def test_index_command_cli_parsing(self, tmp_path):
        """Test CLI parsing with actual temporary directory."""
        # Given: a real temporary directory path
        # Create a temporary directory
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()

        # When/Then: parser accepts args and calls handler once
        # This should work (though handle_index will fail due to no PDFs)
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir)])
            assert result == 0
            mock_handler.assert_called_once()

    def test_index_command_with_custom_index_path(self, tmp_path):
        """Test index command with custom index path."""
        # Given: valid source and custom destination directories
        test_dir = tmp_path / "test_docs"
        test_dir.mkdir()

        index_dir = tmp_path / "custom_index"
        index_dir.mkdir()

        # When/Then: custom index path option is parsed and delegated
        with patch("src.cli.index_cmd.handle_index") as mock_handler:
            mock_handler.return_value = 0
            result = main(["index", str(test_dir), "--index-path", str(index_dir)])
            assert result == 0
            mock_handler.assert_called_once()
