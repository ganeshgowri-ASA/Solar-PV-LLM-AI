"""Comprehensive tests for Vector Store components."""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from typing import List, Dict, Any

from src.utils.errors import PineconeIntegrationError


class TestPineconeClient:
    """Tests for PineconeClient with mocked Pinecone SDK."""

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_client_initialization_new_index(self, mock_settings, mock_pinecone):
        """Test client initialization when index doesn't exist."""
        from src.vector_store.pinecone_client import PineconeClient

        # Setup mock settings
        mock_settings.PINECONE_API_KEY = "test-api-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        # Setup mock Pinecone
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = []
        mock_index_status = Mock()
        mock_index_status.status = {'ready': True}
        mock_pc_instance.describe_index.return_value = mock_index_status
        mock_pc_instance.Index.return_value = Mock()
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        assert client is not None
        mock_pc_instance.create_index.assert_called_once()

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_client_initialization_existing_index(self, mock_settings, mock_pinecone):
        """Test client initialization when index already exists."""
        from src.vector_store.pinecone_client import PineconeClient

        # Setup mock settings
        mock_settings.PINECONE_API_KEY = "test-api-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        # Mock existing index
        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = Mock()
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        assert client is not None
        mock_pc_instance.create_index.assert_not_called()

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_upsert_vectors_success(self, mock_settings, mock_pinecone):
        """Test successful vector upsert."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_index = Mock()
        mock_response = Mock()
        mock_response.upserted_count = 2
        mock_index.upsert.return_value = mock_response

        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        vectors = [
            {"id": "vec-1", "values": [0.1, 0.2, 0.3], "metadata": {"key": "value"}},
            {"id": "vec-2", "values": [0.4, 0.5, 0.6], "metadata": {"key": "value2"}}
        ]

        result = client.upsert_vectors(vectors, namespace="test-ns")

        assert result["upserted_count"] == 2
        assert result["namespace"] == "test-ns"
        mock_index.upsert.assert_called_once()

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_upsert_vectors_empty_list_raises(self, mock_settings, mock_pinecone):
        """Test that upserting empty list raises error."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = Mock()
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        with pytest.raises(PineconeIntegrationError):
            client.upsert_vectors([], namespace="test-ns")

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_upsert_batch_success(self, mock_settings, mock_pinecone):
        """Test batch upsert with multiple batches."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536
        mock_settings.BATCH_SIZE = 2

        mock_index = Mock()
        mock_response = Mock()
        mock_response.upserted_count = 2
        mock_index.upsert.return_value = mock_response

        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        ids = ["id-1", "id-2", "id-3", "id-4"]
        embeddings = [[0.1] * 3] * 4
        metadatas = [{"key": f"val-{i}"} for i in range(4)]

        result = client.upsert_batch(ids, embeddings, metadatas, batch_size=2)

        assert result["upserted_count"] == 4
        assert result["batches"] == 2

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_similarity_search(self, mock_settings, mock_pinecone):
        """Test similarity search functionality."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_match = Mock()
        mock_match.id = "vec-1"
        mock_match.score = 0.95
        mock_match.metadata = {"source": "test"}

        mock_response = Mock()
        mock_response.matches = [mock_match]

        mock_index = Mock()
        mock_index.query.return_value = mock_response

        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        query_vector = [0.1, 0.2, 0.3]
        results = client.similarity_search(query_vector, top_k=10)

        assert len(results) == 1
        assert results[0]["id"] == "vec-1"
        assert results[0]["score"] == 0.95
        assert results[0]["metadata"]["source"] == "test"

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_similarity_search_with_filter(self, mock_settings, mock_pinecone):
        """Test similarity search with metadata filter."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_index = Mock()
        mock_response = Mock()
        mock_response.matches = []
        mock_index.query.return_value = mock_response

        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        filter_dict = {"standard": "IEC 61215"}
        client.similarity_search([0.1, 0.2], top_k=5, filter_dict=filter_dict)

        mock_index.query.assert_called_once()
        call_kwargs = mock_index.query.call_args[1]
        assert call_kwargs["filter"] == filter_dict

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_delete_vectors_by_ids(self, mock_settings, mock_pinecone):
        """Test deleting vectors by IDs."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_index = Mock()
        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        result = client.delete_vectors(ids=["vec-1", "vec-2"], namespace="test-ns")

        assert result["deleted_count"] == 2
        assert result["method"] == "by_ids"
        mock_index.delete.assert_called_once()

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_delete_vectors_by_filter(self, mock_settings, mock_pinecone):
        """Test deleting vectors by filter."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_index = Mock()
        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        filter_dict = {"source": "old_data"}
        result = client.delete_vectors(filter_dict=filter_dict)

        assert result["method"] == "by_filter"
        mock_index.delete.assert_called_once()

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_delete_vectors_delete_all(self, mock_settings, mock_pinecone):
        """Test deleting all vectors in namespace."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_index = Mock()
        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        result = client.delete_vectors(delete_all=True, namespace="test-ns")

        assert result["deleted"] == "all"
        mock_index.delete.assert_called_with(delete_all=True, namespace="test-ns")

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_delete_vectors_no_criteria_raises(self, mock_settings, mock_pinecone):
        """Test that delete without criteria raises error."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = Mock()
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        with pytest.raises(PineconeIntegrationError):
            client.delete_vectors()

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_get_index_stats(self, mock_settings, mock_pinecone):
        """Test getting index statistics."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_stats = Mock()
        mock_stats.total_vector_count = 1000
        mock_stats.dimension = 1536
        mock_stats.index_fullness = 0.1
        mock_stats.namespaces = {"default": Mock(vector_count=500), "test": Mock(vector_count=500)}

        mock_index = Mock()
        mock_index.describe_index_stats.return_value = mock_stats

        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        result = client.get_index_stats()

        assert result["total_vector_count"] == 1000
        assert result["dimension"] == 1536
        assert "namespaces" in result

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_fetch_vectors(self, mock_settings, mock_pinecone):
        """Test fetching vectors by ID."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_vector = Mock()
        mock_vector.id = "vec-1"
        mock_vector.values = [0.1, 0.2, 0.3]
        mock_vector.metadata = {"key": "value"}

        mock_response = Mock()
        mock_response.vectors = {"vec-1": mock_vector}

        mock_index = Mock()
        mock_index.fetch.return_value = mock_response

        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        result = client.fetch_vectors(["vec-1"])

        assert "vec-1" in result
        assert result["vec-1"]["values"] == [0.1, 0.2, 0.3]


class TestVectorStoreEmbeddings:
    """Tests for embedding generation."""

    @patch('src.vector_store.embeddings.OpenAI')
    def test_openai_embedding_generation(self, mock_openai):
        """Test OpenAI embedding generation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_embedding = Mock()
        mock_embedding.embedding = [0.1] * 1536
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.vector_store.embeddings import get_openai_embedding

        embedding = get_openai_embedding("Test text for embedding")

        assert embedding is not None
        assert len(embedding) == 1536

    @patch('src.vector_store.embeddings.SentenceTransformer')
    def test_sentence_transformer_embedding(self, mock_st):
        """Test SentenceTransformer embedding generation."""
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1] * 384]
        mock_st.return_value = mock_model

        from src.vector_store.embeddings import get_sentence_embedding

        embedding = get_sentence_embedding("Test text", model_name="all-MiniLM-L6-v2")

        assert embedding is not None
        mock_model.encode.assert_called_once()


class TestVectorStoreHandler:
    """Tests for VectorStoreHandler."""

    @patch('src.vector_store.handler.PineconeClient')
    @patch('src.vector_store.handler.get_openai_embedding')
    def test_handler_store_document(self, mock_embedding, mock_client):
        """Test storing a document."""
        mock_embedding.return_value = [0.1] * 1536
        mock_client_instance = Mock()
        mock_client_instance.upsert_vectors.return_value = {"upserted_count": 1}
        mock_client.return_value = mock_client_instance

        from src.vector_store.handler import VectorStoreHandler

        handler = VectorStoreHandler()
        result = handler.store_document(
            doc_id="test-doc",
            content="Test content",
            metadata={"source": "test"}
        )

        assert result["upserted_count"] == 1

    @patch('src.vector_store.handler.PineconeClient')
    @patch('src.vector_store.handler.get_openai_embedding')
    def test_handler_search_documents(self, mock_embedding, mock_client):
        """Test searching documents."""
        mock_embedding.return_value = [0.1] * 1536
        mock_client_instance = Mock()
        mock_client_instance.similarity_search.return_value = [
            {"id": "doc-1", "score": 0.95, "metadata": {"content": "Test"}}
        ]
        mock_client.return_value = mock_client_instance

        from src.vector_store.handler import VectorStoreHandler

        handler = VectorStoreHandler()
        results = handler.search("test query", top_k=5)

        assert len(results) == 1
        assert results[0]["score"] == 0.95

    @patch('src.vector_store.handler.PineconeClient')
    @patch('src.vector_store.handler.get_openai_embedding')
    def test_handler_batch_store(self, mock_embedding, mock_client):
        """Test batch document storage."""
        mock_embedding.return_value = [0.1] * 1536
        mock_client_instance = Mock()
        mock_client_instance.upsert_batch.return_value = {"upserted_count": 3}
        mock_client.return_value = mock_client_instance

        from src.vector_store.handler import VectorStoreHandler

        handler = VectorStoreHandler()

        documents = [
            {"id": "doc-1", "content": "Content 1", "metadata": {}},
            {"id": "doc-2", "content": "Content 2", "metadata": {}},
            {"id": "doc-3", "content": "Content 3", "metadata": {}}
        ]

        result = handler.batch_store(documents)

        assert result["upserted_count"] == 3


class TestVectorStoreEdgeCases:
    """Edge case tests for vector store components."""

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_connection_failure(self, mock_settings, mock_pinecone):
        """Test handling connection failures."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "invalid-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536

        mock_pinecone.side_effect = Exception("Connection failed")

        with pytest.raises(PineconeIntegrationError):
            PineconeClient()

    @patch('src.vector_store.pinecone_client.Pinecone')
    @patch('src.vector_store.pinecone_client.settings')
    def test_large_batch_processing(self, mock_settings, mock_pinecone):
        """Test processing large batches of vectors."""
        from src.vector_store.pinecone_client import PineconeClient

        mock_settings.PINECONE_API_KEY = "test-key"
        mock_settings.PINECONE_INDEX_NAME = "test-index"
        mock_settings.PINECONE_ENVIRONMENT = "us-west-2"
        mock_settings.EMBEDDING_DIMENSION = 1536
        mock_settings.BATCH_SIZE = 100

        mock_index = Mock()
        mock_response = Mock()
        mock_response.upserted_count = 100
        mock_index.upsert.return_value = mock_response

        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"
        mock_pc_instance = Mock()
        mock_pc_instance.list_indexes.return_value = [mock_index_obj]
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        client = PineconeClient()

        # Create 250 vectors (should result in 3 batches of 100, 100, 50)
        ids = [f"id-{i}" for i in range(250)]
        embeddings = [[0.1] * 3] * 250
        metadatas = [{"index": i} for i in range(250)]

        result = client.upsert_batch(ids, embeddings, metadatas, batch_size=100)

        assert result["total_vectors"] == 250
        assert result["batches"] == 3

    def test_empty_namespace_operations(self):
        """Test operations on empty namespace."""
        # This would typically test actual behavior with empty data
        pass

    def test_special_characters_in_metadata(self):
        """Test handling special characters in metadata."""
        metadata = {
            "title": "IEC 61215-1:2016",
            "section": "5.1 <thermal> & environmental",
            "notes": "Testing \"requirements\" for modules"
        }

        # Verify metadata can be serialized
        import json
        serialized = json.dumps(metadata)
        deserialized = json.loads(serialized)

        assert deserialized == metadata
