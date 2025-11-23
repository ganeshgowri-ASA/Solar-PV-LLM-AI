"""Unit tests for BM25 retriever."""
import pytest
from src.rag_engine.retrieval.bm25_retriever import BM25Retriever
from src.rag_engine.utils.data_models import Document


class TestBM25Retriever:
    """Test BM25Retriever."""

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents."""
        return [
            Document(
                id="doc1",
                content="Solar panels convert sunlight into electricity using photovoltaic cells.",
                metadata={"source": "solar_guide.pdf"}
            ),
            Document(
                id="doc2",
                content="Wind turbines generate power from wind energy.",
                metadata={"source": "wind_guide.pdf"}
            ),
            Document(
                id="doc3",
                content="Photovoltaic systems are a type of solar energy technology.",
                metadata={"source": "pv_systems.pdf"}
            ),
        ]

    def test_initialization(self):
        """Test retriever initialization."""
        retriever = BM25Retriever()
        assert retriever.get_document_count() == 0

    def test_add_documents(self, sample_documents):
        """Test adding documents."""
        retriever = BM25Retriever()
        retriever.add_documents(sample_documents)

        assert retriever.get_document_count() == 3

    def test_retrieve(self, sample_documents):
        """Test document retrieval."""
        retriever = BM25Retriever()
        retriever.add_documents(sample_documents)

        results = retriever.retrieve("solar panels photovoltaic", top_k=2)

        assert len(results) > 0
        assert results[0].document.id in ["doc1", "doc3"]  # Should retrieve solar-related docs
        assert results[0].retrieval_method == "bm25"

    def test_retrieve_empty(self):
        """Test retrieval with empty index."""
        retriever = BM25Retriever()
        results = retriever.retrieve("test query", top_k=5)

        assert len(results) == 0

    def test_tokenization(self, sample_documents):
        """Test tokenization."""
        retriever = BM25Retriever()
        tokens = retriever._tokenize("Solar Panels Are Great")

        assert "solar" in tokens
        assert "panels" in tokens
        assert all(t.islower() for t in tokens)
