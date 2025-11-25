"""Unit tests for data models."""
import pytest
from datetime import datetime
from src.rag_engine.utils.data_models import Document, RetrievalResult, RAGContext


class TestDocument:
    """Test Document model."""

    def test_create_document(self):
        """Test creating a document."""
        doc = Document(
            id="doc1",
            content="This is a test document about solar panels.",
            metadata={"source": "test.pdf", "page": 1}
        )

        assert doc.id == "doc1"
        assert "solar panels" in doc.content
        assert doc.metadata["source"] == "test.pdf"
        assert doc.embedding is None

    def test_document_with_embedding(self):
        """Test document with embedding."""
        embedding = [0.1, 0.2, 0.3]
        doc = Document(
            id="doc2",
            content="Test content",
            embedding=embedding
        )

        assert doc.embedding == embedding


class TestRetrievalResult:
    """Test RetrievalResult model."""

    def test_create_retrieval_result(self):
        """Test creating a retrieval result."""
        doc = Document(id="doc1", content="Test content")
        result = RetrievalResult(
            document=doc,
            score=0.95,
            rank=1,
            retrieval_method="vector_similarity"
        )

        assert result.document.id == "doc1"
        assert result.score == 0.95
        assert result.rank == 1
        assert result.retrieval_method == "vector_similarity"


class TestRAGContext:
    """Test RAGContext model."""

    def test_create_rag_context(self):
        """Test creating RAG context."""
        doc1 = Document(id="doc1", content="Solar panels convert sunlight to electricity.")
        doc2 = Document(id="doc2", content="Photovoltaic cells are key components.")

        results = [
            RetrievalResult(document=doc1, score=0.9, rank=1, retrieval_method="hybrid"),
            RetrievalResult(document=doc2, score=0.8, rank=2, retrieval_method="hybrid"),
        ]

        context = RAGContext(
            query="How do solar panels work?",
            retrieved_docs=results,
            context_text="Test context",
            metadata={"num_docs": 2}
        )

        assert context.query == "How do solar panels work?"
        assert len(context.retrieved_docs) == 2
        assert context.metadata["num_docs"] == 2

    def test_format_context(self):
        """Test context formatting."""
        doc1 = Document(
            id="doc1",
            content="Solar panels work by converting light.",
            metadata={"source": "guide.pdf"}
        )

        result = RetrievalResult(
            document=doc1,
            score=0.9,
            rank=1,
            retrieval_method="vector"
        )

        context = RAGContext(
            query="Test query",
            retrieved_docs=[result],
            context_text=""
        )

        formatted = context.format_context()
        assert "Solar panels work" in formatted
        assert "source: guide.pdf" in formatted
