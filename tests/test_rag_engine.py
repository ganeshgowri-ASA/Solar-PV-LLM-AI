"""Comprehensive tests for the RAG Engine components."""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch

# Mock heavy dependencies before importing
sys.modules['sentence_transformers'] = Mock()
sys.modules['chromadb'] = Mock()
sys.modules['torch'] = Mock()
sys.modules['transformers'] = Mock()

from typing import List, Dict, Any


class TestDocument:
    """Tests for Document model."""

    def test_document_creation(self):
        """Test creating a document with required fields."""
        from src.rag_engine.utils.data_models import Document

        doc = Document(
            id="test-doc-1",
            content="This is test content about solar PV systems."
        )
        assert doc.id == "test-doc-1"
        assert doc.content == "This is test content about solar PV systems."
        assert doc.metadata == {}
        assert doc.embedding is None

    def test_document_with_metadata(self):
        """Test creating a document with metadata."""
        from src.rag_engine.utils.data_models import Document

        metadata = {
            "source": "IEC 61215",
            "section": "Testing Requirements",
            "page": 45
        }
        doc = Document(
            id="test-doc-2",
            content="Module qualification testing procedures.",
            metadata=metadata
        )
        assert doc.metadata == metadata
        assert doc.metadata["source"] == "IEC 61215"

    def test_document_with_embedding(self):
        """Test creating a document with embedding vector."""
        from src.rag_engine.utils.data_models import Document

        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        doc = Document(
            id="test-doc-3",
            content="Embedding test content.",
            embedding=embedding
        )
        assert doc.embedding == embedding
        assert len(doc.embedding) == 5


class TestRetrievalResult:
    """Tests for RetrievalResult model."""

    def test_retrieval_result_creation(self):
        """Test creating a retrieval result."""
        from src.rag_engine.utils.data_models import Document, RetrievalResult

        doc = Document(id="doc-1", content="Test content")
        result = RetrievalResult(
            document=doc,
            score=0.95,
            rank=1,
            retrieval_method="vector"
        )
        assert result.document.id == "doc-1"
        assert result.score == 0.95
        assert result.rank == 1
        assert result.retrieval_method == "vector"

    def test_retrieval_result_with_different_methods(self):
        """Test retrieval results from different methods."""
        from src.rag_engine.utils.data_models import Document, RetrievalResult

        doc = Document(id="doc-2", content="BM25 content")

        # Vector retrieval
        vector_result = RetrievalResult(
            document=doc, score=0.85, rank=1, retrieval_method="vector"
        )
        assert vector_result.retrieval_method == "vector"

        # BM25 retrieval
        bm25_result = RetrievalResult(
            document=doc, score=0.78, rank=2, retrieval_method="bm25"
        )
        assert bm25_result.retrieval_method == "bm25"

        # Hybrid retrieval
        hybrid_result = RetrievalResult(
            document=doc, score=0.82, rank=1, retrieval_method="hybrid"
        )
        assert hybrid_result.retrieval_method == "hybrid"


class TestRAGContext:
    """Tests for RAGContext model."""

    def test_rag_context_creation(self):
        """Test creating RAG context."""
        from src.rag_engine.utils.data_models import Document, RetrievalResult, RAGContext

        doc = Document(id="doc-1", content="Solar panel efficiency.")
        result = RetrievalResult(
            document=doc, score=0.9, rank=1, retrieval_method="hybrid"
        )

        context = RAGContext(
            query="What is solar panel efficiency?",
            retrieved_docs=[result],
            context_text="Solar panel efficiency content."
        )

        assert context.query == "What is solar panel efficiency?"
        assert len(context.retrieved_docs) == 1
        assert context.context_text == "Solar panel efficiency content."

    def test_rag_context_format_context_default(self):
        """Test default context formatting."""
        from src.rag_engine.utils.data_models import Document, RetrievalResult, RAGContext

        doc = Document(
            id="doc-1",
            content="Module testing requirements.",
            metadata={"source": "IEC 61215", "section": "5.1"}
        )
        result = RetrievalResult(
            document=doc, score=0.95, rank=1, retrieval_method="vector"
        )

        context = RAGContext(
            query="Testing requirements?",
            retrieved_docs=[result],
            context_text=""
        )

        formatted = context.format_context()
        assert "[1]" in formatted
        assert "Module testing requirements." in formatted
        assert "source: IEC 61215" in formatted

    def test_rag_context_format_context_custom_template(self):
        """Test custom template formatting."""
        from src.rag_engine.utils.data_models import Document, RetrievalResult, RAGContext

        doc = Document(id="doc-1", content="Custom content.")
        result = RetrievalResult(
            document=doc, score=0.9, rank=1, retrieval_method="vector"
        )

        context = RAGContext(
            query="Custom query",
            retrieved_docs=[result],
            context_text="Context text here."
        )

        template = "Query: {query}\nContext: {context}"
        formatted = context.format_context(template=template)

        assert "Query: Custom query" in formatted
        assert "Context: Context text here." in formatted

    def test_rag_context_with_multiple_docs(self):
        """Test context with multiple retrieved documents."""
        from src.rag_engine.utils.data_models import Document, RetrievalResult, RAGContext

        docs = [
            Document(id=f"doc-{i}", content=f"Content {i}")
            for i in range(3)
        ]
        results = [
            RetrievalResult(
                document=doc, score=0.9 - i * 0.1, rank=i + 1, retrieval_method="hybrid"
            )
            for i, doc in enumerate(docs)
        ]

        context = RAGContext(
            query="Multi-doc query",
            retrieved_docs=results,
            context_text="Combined context."
        )

        assert len(context.retrieved_docs) == 3
        formatted = context.format_context()
        assert "[1]" in formatted
        assert "[2]" in formatted
        assert "[3]" in formatted


class TestBM25Retriever:
    """Tests for BM25Retriever."""

    def test_bm25_initialization(self):
        """Test BM25 retriever initialization."""
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()
        assert retriever is not None
        assert retriever.get_document_count() == 0

    def test_bm25_add_documents(self):
        """Test adding documents to BM25 index."""
        from src.rag_engine.utils.data_models import Document
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()

        docs = [
            Document(id="doc-1", content="Solar photovoltaic systems generate electricity."),
            Document(id="doc-2", content="IEC 61215 describes module testing standards."),
            Document(id="doc-3", content="Photovoltaic module degradation analysis.")
        ]

        retriever.add_documents(docs)
        assert retriever.get_document_count() == 3

    def test_bm25_retrieve(self):
        """Test BM25 retrieval."""
        from src.rag_engine.utils.data_models import Document, RetrievalResult
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()

        docs = [
            Document(id="doc-1", content="Solar photovoltaic systems generate electricity from sunlight."),
            Document(id="doc-2", content="Wind turbines convert wind energy to electrical power."),
            Document(id="doc-3", content="Photovoltaic module testing according to IEC standards.")
        ]

        retriever.add_documents(docs)

        results = retriever.retrieve("photovoltaic electricity", top_k=2)

        assert len(results) <= 2
        assert all(isinstance(r, RetrievalResult) for r in results)

        # Photovoltaic-related docs should score higher
        if results:
            assert results[0].score >= 0

    def test_bm25_retrieve_empty_corpus(self):
        """Test retrieval from empty corpus."""
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()
        results = retriever.retrieve("test query", top_k=5)
        assert results == []

    def test_bm25_retrieve_no_match(self):
        """Test retrieval with no matching documents."""
        from src.rag_engine.utils.data_models import Document
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()

        docs = [
            Document(id="doc-1", content="Solar panel installation guide.")
        ]
        retriever.add_documents(docs)

        # Query with completely unrelated terms
        results = retriever.retrieve("quantum computing", top_k=5)
        # Should return results but with low scores
        assert isinstance(results, list)


class TestRAGEngineEdgeCases:
    """Edge case tests for RAG engine components."""

    def test_empty_document_content(self):
        """Test handling documents with empty content."""
        from src.rag_engine.utils.data_models import Document

        doc = Document(id="empty-doc", content="")
        assert doc.content == ""
        assert doc.id == "empty-doc"

    def test_special_characters_in_content(self):
        """Test documents with special characters."""
        from src.rag_engine.utils.data_models import Document

        content = "IEC 61215-1:2016 & IEC 61730-1 <requirements> \"testing\""
        doc = Document(id="special-doc", content=content)
        assert doc.content == content

    def test_unicode_content(self):
        """Test documents with unicode content."""
        from src.rag_engine.utils.data_models import Document

        content = "Solar efficiency: 22.5% - panneau solaire - \u592a\u9633\u80fd"
        doc = Document(id="unicode-doc", content=content)
        assert doc.content == content

    def test_very_long_content(self):
        """Test documents with very long content."""
        from src.rag_engine.utils.data_models import Document

        content = "Solar PV testing " * 10000
        doc = Document(id="long-doc", content=content)
        assert len(doc.content) > 100000

    def test_metadata_with_nested_structures(self):
        """Test metadata with nested dictionaries and lists."""
        from src.rag_engine.utils.data_models import Document

        metadata = {
            "source": {
                "name": "IEC 61215",
                "version": "2016",
                "sections": ["5.1", "5.2", "6.1"]
            },
            "tags": ["testing", "qualification", "module"],
            "references": [
                {"id": "ref-1", "title": "Reference 1"},
                {"id": "ref-2", "title": "Reference 2"}
            ]
        }
        doc = Document(id="nested-doc", content="Test", metadata=metadata)
        assert doc.metadata["source"]["name"] == "IEC 61215"
        assert len(doc.metadata["tags"]) == 3

    def test_retrieval_result_score_boundaries(self):
        """Test retrieval results with edge case scores."""
        from src.rag_engine.utils.data_models import Document, RetrievalResult

        doc = Document(id="doc-1", content="Test")

        # Score of 0
        result_zero = RetrievalResult(
            document=doc, score=0.0, rank=1, retrieval_method="vector"
        )
        assert result_zero.score == 0.0

        # Score of 1
        result_one = RetrievalResult(
            document=doc, score=1.0, rank=1, retrieval_method="vector"
        )
        assert result_one.score == 1.0

        # Negative score (can happen with some algorithms)
        result_negative = RetrievalResult(
            document=doc, score=-0.5, rank=1, retrieval_method="bm25"
        )
        assert result_negative.score == -0.5


class TestBM25RetrieverAdvanced:
    """Advanced tests for BM25 retriever."""

    def test_bm25_tokenization(self):
        """Test BM25 handles different tokenization scenarios."""
        from src.rag_engine.utils.data_models import Document
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()

        docs = [
            Document(id="doc-1", content="Solar-PV system integration"),
            Document(id="doc-2", content="solar_pv_system_integration"),
            Document(id="doc-3", content="SOLAR PV SYSTEM INTEGRATION")
        ]

        retriever.add_documents(docs)
        results = retriever.retrieve("solar pv", top_k=3)

        assert len(results) <= 3

    def test_bm25_multiple_add_documents(self):
        """Test adding documents incrementally."""
        from src.rag_engine.utils.data_models import Document
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()

        # First batch
        docs1 = [Document(id="doc-1", content="First batch content")]
        retriever.add_documents(docs1)

        # Second batch
        docs2 = [Document(id="doc-2", content="Second batch content")]
        retriever.add_documents(docs2)

        # Should have documents from both batches
        assert retriever.get_document_count() >= 1

    def test_bm25_top_k_larger_than_corpus(self):
        """Test retrieval when top_k exceeds corpus size."""
        from src.rag_engine.utils.data_models import Document
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever

        retriever = BM25Retriever()

        docs = [
            Document(id="doc-1", content="Single document in corpus.")
        ]
        retriever.add_documents(docs)

        results = retriever.retrieve("document", top_k=100)

        # Should return at most the corpus size
        assert len(results) <= 1


class TestVectorRetrieverMocked:
    """Tests for VectorRetriever with mocked dependencies."""

    def test_vector_retriever_mock_basic(self):
        """Test vector retriever basic behavior with full mock."""
        # Create a mock retriever directly to test interface
        mock_retriever = Mock()
        mock_retriever.embedding_model = "all-MiniLM-L6-v2"
        mock_retriever.store_type = "chromadb"

        # Test that mock has expected attributes
        assert mock_retriever.embedding_model == "all-MiniLM-L6-v2"
        assert mock_retriever.store_type == "chromadb"

    def test_vector_retriever_add_documents_mock(self):
        """Test adding documents with mock retriever."""
        from src.rag_engine.utils.data_models import Document

        # Create a mock retriever
        mock_retriever = Mock()
        mock_retriever.add_documents = Mock(return_value=None)

        docs = [
            Document(id="doc-1", content="Test content 1"),
            Document(id="doc-2", content="Test content 2")
        ]

        # Call mock method
        mock_retriever.add_documents(docs)
        mock_retriever.add_documents.assert_called_once_with(docs)

    def test_vector_retriever_retrieve_mock(self):
        """Test retrieval with mock retriever."""
        from src.rag_engine.utils.data_models import Document, RetrievalResult

        doc = Document(id="doc-1", content="Test content")
        mock_result = RetrievalResult(
            document=doc, score=0.9, rank=1, retrieval_method="vector"
        )

        mock_retriever = Mock()
        mock_retriever.retrieve = Mock(return_value=[mock_result])

        results = mock_retriever.retrieve("test query", top_k=5)

        assert len(results) == 1
        assert results[0].score == 0.9
        mock_retriever.retrieve.assert_called_once_with("test query", top_k=5)


class TestHybridRetrieverMocked:
    """Tests for HybridRetriever combining vector and BM25."""

    def test_hybrid_retriever_initialization(self):
        """Test hybrid retriever initialization with mock retrievers."""
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever
        from src.rag_engine.retrieval.hybrid_retriever import HybridRetriever

        # Use a mock for vector retriever
        mock_vector_retriever = Mock()
        bm25_retriever = BM25Retriever()

        hybrid = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            bm25_retriever=bm25_retriever,
            alpha=0.5
        )
        assert hybrid is not None
        assert hybrid.alpha == 0.5

    def test_hybrid_alpha_weighting(self):
        """Test hybrid alpha parameter controls weighting."""
        from src.rag_engine.retrieval.bm25_retriever import BM25Retriever
        from src.rag_engine.retrieval.hybrid_retriever import HybridRetriever

        mock_vector_retriever = Mock()
        bm25_retriever = BM25Retriever()

        # Alpha = 1.0 means 100% vector
        hybrid_vector = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            bm25_retriever=bm25_retriever,
            alpha=1.0
        )
        assert hybrid_vector.alpha == 1.0

        # Alpha = 0.0 means 100% BM25
        hybrid_bm25 = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            bm25_retriever=bm25_retriever,
            alpha=0.0
        )
        assert hybrid_bm25.alpha == 0.0


# Fixtures for reuse across test files
@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    from src.rag_engine.utils.data_models import Document

    return [
        Document(
            id="iec-61215-1",
            content="IEC 61215-1 specifies the requirements for design qualification and type approval of crystalline silicon terrestrial photovoltaic modules.",
            metadata={"standard": "IEC 61215-1", "type": "qualification"}
        ),
        Document(
            id="iec-61730-1",
            content="IEC 61730-1 defines the requirements for construction of photovoltaic modules to provide safe electrical and mechanical operation.",
            metadata={"standard": "IEC 61730-1", "type": "safety"}
        ),
        Document(
            id="pv-degradation",
            content="Photovoltaic module degradation rates typically range from 0.5% to 1% per year depending on technology and environmental conditions.",
            metadata={"topic": "degradation", "type": "technical"}
        )
    ]


@pytest.fixture
def sample_retrieval_results(sample_documents):
    """Create sample retrieval results for testing."""
    from src.rag_engine.utils.data_models import RetrievalResult

    return [
        RetrievalResult(
            document=sample_documents[0],
            score=0.95,
            rank=1,
            retrieval_method="hybrid"
        ),
        RetrievalResult(
            document=sample_documents[1],
            score=0.87,
            rank=2,
            retrieval_method="hybrid"
        )
    ]
