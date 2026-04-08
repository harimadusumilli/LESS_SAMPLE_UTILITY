"""Unit tests for vector_store module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestVectorStore:
    """Tests that exercise VectorStore logic without requiring ChromaDB."""

    @patch("less_sample_utility.vector_store.chromadb.PersistentClient")
    @patch(
        "less_sample_utility.vector_store.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_add_chunks_calls_collection_add(self, mock_ef_cls, mock_client_cls):
        mock_ef = MagicMock()
        mock_ef_cls.return_value = mock_ef

        mock_collection = MagicMock()
        mock_collection.count.return_value = 3

        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_cls.return_value = mock_client

        from less_sample_utility.vector_store import VectorStore

        store = VectorStore(persist_dir="/tmp/test_chroma")
        chunks = ["chunk1", "chunk2", "chunk3"]
        store.add_chunks(chunks, source="doc.pdf")

        mock_collection.add.assert_called_once()
        call_kwargs = mock_collection.add.call_args.kwargs
        assert call_kwargs["documents"] == chunks
        assert all(m["source"] == "doc.pdf" for m in call_kwargs["metadatas"])

    @patch("less_sample_utility.vector_store.chromadb.PersistentClient")
    @patch(
        "less_sample_utility.vector_store.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_add_empty_chunks_is_noop(self, mock_ef_cls, mock_client_cls):
        mock_ef = MagicMock()
        mock_ef_cls.return_value = mock_ef

        mock_collection = MagicMock()
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_cls.return_value = mock_client

        from less_sample_utility.vector_store import VectorStore

        store = VectorStore(persist_dir="/tmp/test_chroma")
        store.add_chunks([], source="empty.pdf")
        mock_collection.add.assert_not_called()

    @patch("less_sample_utility.vector_store.chromadb.PersistentClient")
    @patch(
        "less_sample_utility.vector_store.embedding_functions.SentenceTransformerEmbeddingFunction"
    )
    def test_count_delegates_to_collection(self, mock_ef_cls, mock_client_cls):
        mock_ef_cls.return_value = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 42
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_cls.return_value = mock_client

        from less_sample_utility.vector_store import VectorStore

        store = VectorStore(persist_dir="/tmp/test_chroma")
        assert store.count() == 42
