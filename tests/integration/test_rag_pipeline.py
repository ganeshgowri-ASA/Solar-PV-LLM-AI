"""Integration tests for RAG pipeline."""
import pytest
import tempfile
from pathlib import Path
from src.rag_engine.pipeline.rag_pipeline import RAGPipeline
from src.rag_engine.utils.data_models import Document
from config.rag_config import RAGConfig, RetrievalConfig, VectorStoreConfig


class TestRAGPipeline:
    """Integration tests for RAG pipeline."""

    @pytest.fixture
    def temp_vector_store(self):
        """Create temporary vector store directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents about solar PV."""
        return [
            Document(
                id="doc1",
                content="Solar photovoltaic (PV) panels convert sunlight directly into electricity using semiconductor materials. The most common type uses silicon-based cells.",
                metadata={"source": "solar_basics.pdf", "page": 1, "topic": "fundamentals"}
            ),
            Document(
                id="doc2",
                content="The efficiency of solar panels typically ranges from 15% to 22% for residential applications. Premium panels can achieve higher efficiency rates.",
                metadata={"source": "efficiency_guide.pdf", "page": 3, "topic": "performance"}
            ),
            Document(
                id="doc3",
                content="Solar panel installation requires proper roof orientation, ideally facing south in the northern hemisphere with minimal shading.",
                metadata={"source": "installation_manual.pdf", "page": 5, "topic": "installation"}
            ),
            Document(
                id="doc4",
                content="Inverters convert the DC electricity from solar panels into AC electricity for home use. Microinverters and string inverters are common types.",
                metadata={"source": "components.pdf", "page": 2, "topic": "equipment"}
            ),
            Document(
                id="doc5",
                content="Solar energy systems can significantly reduce electricity bills and carbon footprint while increasing property value.",
                metadata={"source": "benefits.pdf", "page": 1, "topic": "economics"}
            ),
        ]

    @pytest.fixture
    def rag_pipeline(self, temp_vector_store):
        """Create RAG pipeline with test configuration."""
        config = RAGConfig(
            retrieval=RetrievalConfig(
                top_k=3,
                top_k_rerank=2,
                hybrid_alpha=0.5,
                use_hyde=False
            ),
            vector_store=VectorStoreConfig(
                store_type="chromadb",
                store_path=temp_vector_store,
                collection_name="test_collection"
            )
        )

        pipeline = RAGPipeline(config=config)
        return pipeline

    def test_pipeline_initialization(self, rag_pipeline):
        """Test pipeline initializes correctly."""
        assert rag_pipeline is not None
        assert rag_pipeline.vector_retriever is not None
        assert rag_pipeline.bm25_retriever is not None
        assert rag_pipeline.hybrid_retriever is not None

    def test_add_documents(self, rag_pipeline, sample_documents):
        """Test adding documents to pipeline."""
        rag_pipeline.add_documents(sample_documents)

        stats = rag_pipeline.get_stats()
        assert stats["vector_store"]["document_count"] == 5
        assert stats["bm25"]["document_count"] == 5

    def test_vector_retrieval(self, rag_pipeline, sample_documents):
        """Test vector-based retrieval."""
        rag_pipeline.add_documents(sample_documents)

        results = rag_pipeline.retrieve(
            query="How efficient are solar panels?",
            top_k=3,
            retrieval_method="vector",
            use_reranker=False
        )

        assert len(results) > 0
        assert len(results) <= 3
        # Should retrieve efficiency-related document
        assert any("efficiency" in r.document.content.lower() for r in results)

    def test_bm25_retrieval(self, rag_pipeline, sample_documents):
        """Test BM25 keyword retrieval."""
        rag_pipeline.add_documents(sample_documents)

        results = rag_pipeline.retrieve(
            query="inverter DC AC electricity",
            top_k=3,
            retrieval_method="bm25",
            use_reranker=False
        )

        assert len(results) > 0
        # Should retrieve inverter document
        assert any("inverter" in r.document.content.lower() for r in results[:2])

    def test_hybrid_retrieval(self, rag_pipeline, sample_documents):
        """Test hybrid retrieval."""
        rag_pipeline.add_documents(sample_documents)

        results = rag_pipeline.retrieve(
            query="solar panel installation orientation",
            top_k=3,
            retrieval_method="hybrid",
            use_reranker=False
        )

        assert len(results) > 0
        assert all(r.retrieval_method.startswith("hybrid") for r in results)

    def test_create_context(self, rag_pipeline, sample_documents):
        """Test context creation."""
        rag_pipeline.add_documents(sample_documents)

        context = rag_pipeline.create_context(
            query="What are the benefits of solar energy?",
            top_k=2,
            retrieval_method="vector",
            use_reranker=False
        )

        assert context.query == "What are the benefits of solar energy?"
        assert len(context.retrieved_docs) <= 2
        assert len(context.context_text) > 0
        assert context.metadata["num_docs"] <= 2

    def test_full_query_pipeline(self, rag_pipeline, sample_documents):
        """Test complete query pipeline."""
        rag_pipeline.add_documents(sample_documents)

        result = rag_pipeline.query(
            query="How do photovoltaic cells work?",
            top_k=2,
            retrieval_method="hybrid",
            use_reranker=False,
            return_context_only=False
        )

        assert "query" in result
        assert "context" in result
        assert "retrieved_docs" in result
        assert "formatted_context" in result
        assert result["query"] == "How do photovoltaic cells work?"
        assert len(result["retrieved_docs"]) <= 2

    def test_context_formatting(self, rag_pipeline, sample_documents):
        """Test that context is properly formatted with metadata."""
        rag_pipeline.add_documents(sample_documents)

        context = rag_pipeline.create_context(
            query="solar panels",
            top_k=2,
            retrieval_method="vector",
            use_reranker=False
        )

        formatted = context.context_text
        # Should include rank numbers
        assert "[1]" in formatted
        # Should include metadata
        assert "source:" in formatted.lower() or "Metadata:" in formatted

    def test_get_stats(self, rag_pipeline, sample_documents):
        """Test getting pipeline statistics."""
        rag_pipeline.add_documents(sample_documents)

        stats = rag_pipeline.get_stats()

        assert "vector_store" in stats
        assert "bm25" in stats
        assert "config" in stats
        assert stats["vector_store"]["document_count"] == 5
        assert stats["bm25"]["document_count"] == 5
        assert stats["config"]["top_k"] == 3
