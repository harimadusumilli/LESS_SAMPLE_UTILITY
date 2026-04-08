"""Unit tests for the semantic search module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestSemanticSearch:
    @patch("less_sample_utility.search.VectorStore")
    def test_search_returns_results(self, mock_store_cls):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["chunk A", "chunk B"]],
            "metadatas": [
                [
                    {"source": "a.pdf", "chunk_index": 0},
                    {"source": "a.pdf", "chunk_index": 1},
                ]
            ],
            "distances": [[0.1, 0.3]],
        }
        mock_store = MagicMock()
        mock_store._collection = mock_collection
        mock_store.count.return_value = 2
        mock_store_cls.return_value = mock_store

        from less_sample_utility.search import SemanticSearch

        searcher = SemanticSearch()
        results = searcher.search("test query", n_results=2)

        assert len(results) == 2
        assert results[0].document == "chunk A"
        assert results[0].source == "a.pdf"
        assert results[0].chunk_index == 0
        assert results[0].distance == pytest.approx(0.1)

    @patch("less_sample_utility.search.VectorStore")
    def test_search_empty_store_returns_empty(self, mock_store_cls):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
        mock_store = MagicMock()
        mock_store._collection = mock_collection
        mock_store.count.return_value = 0
        mock_store_cls.return_value = mock_store

        from less_sample_utility.search import SemanticSearch

        searcher = SemanticSearch()
        results = searcher.search("anything")
        assert results == []
