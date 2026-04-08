"""Configuration module for LESS PDF Index and Search CLI.

Handles index path resolution, default settings, and environment configuration.
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration container for LESS application."""

    # Default index path (local directory in user's home or working directory)
    DEFAULT_INDEX_PATH = Path.home() / ".less" / "index"

    # Environment variable for custom index path
    INDEX_PATH_ENV_VAR = "LESS_INDEX_PATH"

    @staticmethod
    def get_index_path(custom_path: Optional[str] = None) -> Path:
        """Resolve the index path with precedence: custom > env var > default.

        Args:
            custom_path: User-provided path (highest precedence)

        Returns:
            Resolved Path object for the vector database index
        """
        if custom_path:
            return Path(custom_path).expanduser().resolve()

        env_path = os.environ.get(Config.INDEX_PATH_ENV_VAR)
        if env_path:
            return Path(env_path).expanduser().resolve()

        return Config.DEFAULT_INDEX_PATH.expanduser().resolve()

    @staticmethod
    def ensure_index_directory(index_path: Path) -> None:
        """Create index directory if it doesn't exist.

        Args:
            index_path: Path where the index should be stored

        Raises:
            OSError: If directory cannot be created or is not writable
        """
        try:
            index_path.mkdir(parents=True, exist_ok=True)
            # Verify write permissions
            test_file = index_path / ".write_test"
            test_file.touch()
            test_file.unlink()
        except (OSError, PermissionError) as e:
            raise OSError(
                f"Cannot create or write to index directory '{index_path}': {e}"
            )


# Singleton instance
config = Config()
