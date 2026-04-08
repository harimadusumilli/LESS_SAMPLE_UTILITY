"""Unit tests for vector database service.

Tests ChromaDB integration for document storage and metadata management.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.services.vector_db import VectorDB
from src.models.text_chunk import TextChunk


class TestVectorDB:
    """Unit tests for VectorDB class."""

    @pytest.fixture
    def temp_index_dir(self, tmp_path):
        """Create temporary index directory."""
        index_dir = tmp_path / "index"
        index_dir.mkdir()
        return index_dir

    @pytest.fixture
    def vector_db(self, temp_index_dir):
        """Create VectorDB instance with mocked ChromaDB."""
        with patch('src.services.vector_db.chromadb.PersistentClient') as mock_client:
            mock_collection = Mock()
            mock_client.return_value.get_or_create_collection.return_value = mock_collection
            db = VectorDB(index_path=temp_index_dir)
            return db

    @pytest.fixture
    def sample_documents(self, tmp_path):
        """Create sample TextChunk instances."""
        pdf_path = tmp_path / "sample.pdf"

        return [
            TextChunk(
                id="doc1_sent_0",
                document_id="doc1",
                content="This is the first sentence.",
                file_path=pdf_path,
                page_number=1,
                sentence_index=0,
                total_sentences=3
            ),
            TextChunk(
                id="doc1_sent_1",
                document_id="doc1",
                content="This is the second sentence.",
                file_path=pdf_path,
                page_number=1,
                sentence_index=1,
                total_sentences=3
            ),
            TextChunk(
                id="doc1_sent_2",
                document_id="doc1",
                content="This is the third sentence.",
                file_path=pdf_path,
                page_number=2,
                sentence_index=2,
                total_sentences=3
            )
        ]

    def test_init_creates_chroma_client(self, vector_db, temp_index_dir):
        """Test that VectorDB initializes ChromaDB client."""
        # Given/When: a VectorDB instance is created via fixture
        # Then: client/collection state is initialized for use
        assert vector_db.index_path == temp_index_dir
        assert vector_db.client is not None
        # Check that collection exists or can be created
        assert hasattr(vector_db, 'collection')

    def test_init_with_custom_index_path(self, temp_index_dir):
        """Test VectorDB initialization with custom index path."""
        # Given: a custom index directory and mocked Chroma client
        with patch('src.services.vector_db.chromadb.PersistentClient') as mock_client:
            custom_path = temp_index_dir / "custom_index"
            custom_path.mkdir()

            # When: VectorDB is initialized with the custom path
            VectorDB(index_path=custom_path)

            # Then: the path is forwarded to the underlying Chroma client
            mock_client.assert_called_once()
            # Verify the path was passed to the client
            call_args, call_kwargs = mock_client.call_args
            assert call_kwargs['path'] == str(custom_path)

    def test_add_documents_stores_content(self, vector_db, sample_documents):
        """Test that add_text_chunks stores document content in ChromaDB."""
        # Given: a list of prepared text chunks
        # Add text chunks
        vector_db.add_text_chunks(sample_documents)

        # When/Then: collection.add receives ids, metadata, and document text
        # Verify collection.add was called
        vector_db.collection.add.assert_called_once()

        # Check the call arguments
        call_args = vector_db.collection.add.call_args
        assert 'ids' in call_args.kwargs
        assert 'metadatas' in call_args.kwargs
        assert 'documents' in call_args.kwargs

        # Check documents content
        documents = call_args.kwargs['documents']
        assert len(documents) == 3
        assert "This is the first sentence." in documents
        assert "This is the second sentence." in documents
        assert "This is the third sentence." in documents

    def test_add_documents_creates_unique_ids(self, vector_db, sample_documents):
        """Test that add_text_chunks creates unique IDs for each document."""
        # Given/When: chunks are inserted into the vector collection
        vector_db.add_text_chunks(sample_documents)

        # Then: each inserted chunk has a unique string ID
        call_args = vector_db.collection.add.call_args
        ids = call_args.kwargs['ids']

        # Should have 3 unique IDs
        assert len(ids) == 3
        assert len(set(ids)) == 3  # All unique

        # IDs should be strings
        assert all(isinstance(id_val, str) for id_val in ids)

    def test_add_documents_includes_metadata(self, vector_db, sample_documents):
        """Test that add_text_chunks includes proper metadata."""
        # Given/When: chunks are added to storage
        vector_db.add_text_chunks(sample_documents)

        # Then: each chunk metadata payload includes required fields
        call_args = vector_db.collection.add.call_args
        metadatas = call_args.kwargs['metadatas']

        assert len(metadatas) == 3

        # Check first document metadata
        metadata_0 = metadatas[0]
        assert metadata_0['document_id'] == "doc1"
        assert metadata_0['file_path'] == str(sample_documents[0].file_path)
        assert metadata_0['page_number'] == 1
        assert metadata_0['sentence_index'] == 0
        assert metadata_0['total_sentences'] == 3

        # Check second document metadata
        metadata_1 = metadatas[1]
        assert metadata_1['sentence_index'] == 1

    def test_add_documents_empty_list(self, vector_db):
        """Test that add_text_chunks handles empty document list."""
        # Given: no chunks to add
        vector_db.add_text_chunks([])

        # Then: persistence layer is not called unnecessarily
        # Should not call collection.add for empty list
        vector_db.collection.add.assert_not_called()

    def test_update_metadata_updates_collection_metadata(self, vector_db):
        """Test that update_metadata updates collection metadata."""
        # Given: summary metadata describing index state
        # Sample metadata
        metadata = {
            'total_pdfs': 5,
            'total_sentences': 150,
            'indexed_at': '2024-01-01T12:00:00Z',
            'index_version': '1.0.0'
        }

        # When: metadata is updated on the collection
        vector_db.update_metadata(metadata)

        # Then: collection.modify is called with the full metadata payload
        vector_db.collection.modify.assert_called_once_with(metadata=metadata)

    def test_search_returns_search_results(self, vector_db):
        """Test that search method returns SearchResult objects."""
        # Given: mocked query results from ChromaDB
        # Mock search results
        mock_results = {
            'ids': [['chunk1', 'chunk2']],
            'documents': [['Result 1 content', 'Result 2 content']],
            'metadatas': [
                [
                    {'document_id': 'doc1', 'file_path': '/path/doc1.pdf', 'page_number': 1, 'sentence_index': 0},
                    {'document_id': 'doc2', 'file_path': '/path/doc2.pdf', 'page_number': 2, 'sentence_index': 5}
                ]
            ],
            'distances': [[0.1, 0.2]]
        }
        vector_db.collection.query.return_value = mock_results

        # When: a search is executed with explicit n_results
        results = vector_db.search("test query", n_results=2)

        # Then: call args are correct and two typed results are returned
        # Should return SearchResult objects
        assert len(results) == 2

        # Verify search was called with correct parameters
        vector_db.collection.query.assert_called_once()
        call_kwargs = vector_db.collection.query.call_args.kwargs
        assert call_kwargs['query_texts'] == ["test query"]
        assert call_kwargs['n_results'] == 2

    def test_search_with_threshold_filters_results(self, vector_db):
        """Test that search filters results by distance threshold."""
        # Given: search candidates with mixed distance values
        # Mock results with varying distances
        mock_results = {
            'ids': [['chunk1', 'chunk2', 'chunk3']],
            'documents': [['Close match', 'Far match', 'Medium match']],
            'metadatas': [
                [
                    {'document_id': 'doc1', 'file_path': '/path/doc1.pdf', 'page_number': 1},
                    {'document_id': 'doc2', 'file_path': '/path/doc2.pdf', 'page_number': 2},
                    {'document_id': 'doc3', 'file_path': '/path/doc3.pdf', 'page_number': 3}
                ]
            ],
            'distances': [[0.1, 0.8, 0.4]]  # Only first two below threshold 0.5
        }
        vector_db.collection.query.return_value = mock_results

        # When: min_score filtering is applied
        results = vector_db.search("test query", n_results=5, min_score=0.5)

        # Then: only results meeting similarity threshold are kept
        # Should only return results above threshold (similarity = 1 - distance)
        # 1-0.1=0.9 (>0.5), 1-0.8=0.2 (<0.5), 1-0.4=0.6 (>0.5)
        assert len(results) == 2  # First and third results

        # Verify distances are included in results
        assert results[0].relevance_score == 0.9
        assert results[1].relevance_score == 0.6

    def test_get_collection_stats_returns_info(self, vector_db):
        """Test that get_collection_stats returns collection information."""
        # Given: mocked collection count and metadata
        vector_db.collection.count.return_value = 100
        vector_db.collection.metadata = {'total_pdfs': 5, 'indexed_at': '2024-01-01'}

        # When: stats are requested
        stats = vector_db.get_collection_stats()

        # Then: count and metadata are exposed in a stable response shape
        assert stats['document_count'] == 100
        assert stats['metadata'] == {'total_pdfs': 5, 'indexed_at': '2024-01-01'}

        vector_db.collection.count.assert_called_once()

    def test_search_empty_results(self, vector_db):
        """Test search behavior with no results."""
        # Given: an empty result set from the vector database
        # Mock empty results
        mock_results = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        vector_db.collection.query.return_value = mock_results

        # When: search is executed
        results = vector_db.search("test query")

        # Then: an empty list is returned instead of errors or null values
        assert len(results) == 0