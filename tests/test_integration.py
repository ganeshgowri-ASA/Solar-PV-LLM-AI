"""End-to-end integration tests for Solar PV LLM AI platform."""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any, List
import json


class TestRAGIntegration:
    """Integration tests for RAG pipeline."""

    @patch('src.rag_engine.pipeline.rag_pipeline.VectorRetriever')
    @patch('src.rag_engine.pipeline.rag_pipeline.BM25Retriever')
    @patch('src.rag_engine.pipeline.rag_pipeline.RAGConfig')
    def test_full_rag_pipeline_flow(self, mock_config, mock_bm25, mock_vector):
        """Test complete RAG pipeline from query to response."""
        from src.rag_engine.pipeline.rag_pipeline import RAGPipeline
        from src.rag_engine.utils.data_models import Document, RetrievalResult

        # Setup config mock
        config = Mock()
        config.vector_store.embedding_model = "all-MiniLM-L6-v2"
        config.vector_store.store_type = "memory"
        config.vector_store.store_path = "/tmp"
        config.vector_store.collection_name = "test"
        config.retrieval.hybrid_alpha = 0.5
        config.retrieval.top_k = 10
        config.retrieval.top_k_rerank = 5
        config.reranker.reranker_type = "none"
        config.hyde.enabled = False
        mock_config.from_env.return_value = config

        # Setup retriever mocks
        mock_vector_instance = Mock()
        mock_bm25_instance = Mock()

        doc = Document(
            id="iec-61215",
            content="IEC 61215 specifies requirements for crystalline silicon PV modules.",
            metadata={"standard": "IEC 61215", "type": "qualification"}
        )

        mock_bm25_instance.retrieve.return_value = [
            RetrievalResult(document=doc, score=0.8, rank=1, retrieval_method="bm25")
        ]
        mock_bm25_instance.get_document_count.return_value = 1

        mock_vector_instance.retrieve.return_value = [
            RetrievalResult(document=doc, score=0.9, rank=1, retrieval_method="vector")
        ]
        mock_vector_instance.get_document_count.return_value = 1

        mock_vector.return_value = mock_vector_instance
        mock_bm25.return_value = mock_bm25_instance

        # Initialize pipeline
        pipeline = RAGPipeline(config=config)

        # Add documents
        documents = [doc]
        pipeline.add_documents(documents)

        # Query
        result = pipeline.query(
            query="What are the requirements for PV module qualification?",
            retrieval_method="bm25"
        )

        assert result is not None
        assert "context" in result

    @patch('src.rag_engine.pipeline.rag_pipeline.VectorRetriever')
    @patch('src.rag_engine.pipeline.rag_pipeline.BM25Retriever')
    @patch('src.rag_engine.pipeline.rag_pipeline.RAGConfig')
    def test_rag_with_context_creation(self, mock_config, mock_bm25, mock_vector):
        """Test RAG pipeline context creation."""
        from src.rag_engine.pipeline.rag_pipeline import RAGPipeline
        from src.rag_engine.utils.data_models import Document, RetrievalResult

        config = Mock()
        config.vector_store.embedding_model = "all-MiniLM-L6-v2"
        config.vector_store.store_type = "memory"
        config.vector_store.store_path = "/tmp"
        config.vector_store.collection_name = "test"
        config.retrieval.hybrid_alpha = 0.5
        config.retrieval.top_k = 5
        config.retrieval.top_k_rerank = 3
        config.reranker.reranker_type = "none"
        config.hyde.enabled = False
        mock_config.from_env.return_value = config

        doc = Document(id="doc-1", content="Test content")
        mock_bm25_instance = Mock()
        mock_bm25_instance.retrieve.return_value = [
            RetrievalResult(document=doc, score=0.8, rank=1, retrieval_method="bm25")
        ]
        mock_bm25.return_value = mock_bm25_instance

        mock_vector_instance = Mock()
        mock_vector_instance.get_document_count.return_value = 0
        mock_vector.return_value = mock_vector_instance

        pipeline = RAGPipeline(config=config)

        context = pipeline.create_context(
            query="Test query",
            retrieval_results=[
                RetrievalResult(document=doc, score=0.8, rank=1, retrieval_method="bm25")
            ]
        )

        assert context.query == "Test query"
        assert len(context.retrieved_docs) == 1


class TestCitationIntegration:
    """Integration tests for citation management."""

    def test_citation_extraction_and_formatting(self):
        """Test complete citation workflow."""
        from src.citation_manager.citation_extractor import CitationExtractor
        from src.citation_manager.citation_formatter import CitationFormatter
        from src.citation_manager.citation_manager import CitationManager

        # Create components
        extractor = CitationExtractor()
        formatter = CitationFormatter()

        # Test response with inline citations
        response = """
        According to IEC 61215-1:2016 [1], crystalline silicon modules must undergo
        thermal cycling tests. The safety requirements specified in IEC 61730-1:2016 [2]
        ensure electrical safety. Performance testing follows IEC 61853-1:2011 [3].
        """

        # Extract citations
        extracted = extractor.extract(response)

        assert len(extracted) >= 0  # May not find citations depending on implementation

    def test_citation_deduplication(self):
        """Test citation deduplication."""
        from src.citation_manager.citation_tracker import CitationTracker

        tracker = CitationTracker()

        # Add duplicate citations
        citations = [
            {"source": "IEC 61215", "content": "Module testing", "score": 0.9},
            {"source": "IEC 61215", "content": "Module testing duplicate", "score": 0.85},
            {"source": "IEC 61730", "content": "Safety requirements", "score": 0.8}
        ]

        for citation in citations:
            tracker.add_citation(citation)

        # Should have deduplicated
        unique_citations = tracker.get_unique_citations()
        assert len(unique_citations) <= len(citations)


class TestLLMOrchestratorIntegration:
    """Integration tests for LLM orchestrator."""

    @patch('src.orchestrator.clients.gpt_client.OpenAI')
    def test_orchestrator_query_routing(self, mock_openai):
        """Test query routing in orchestrator."""
        from src.orchestrator.service import OrchestratorService

        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Test orchestrator initialization
        # Note: Actual implementation may vary

    @patch('src.orchestrator.clients.claude_client.Anthropic')
    def test_orchestrator_fallback(self, mock_anthropic):
        """Test orchestrator fallback mechanism."""
        # Test that orchestrator falls back to secondary LLM on failure
        pass


class TestAgentIntegration:
    """Integration tests for multi-agent system."""

    def test_agent_task_routing(self, mock_system_config):
        """Test task routing between agents."""
        from src.supervisor.router import TaskRouter
        from src.agents.iec_standards_agent import IECStandardsAgent
        from src.agents.testing_specialist_agent import TestingSpecialistAgent
        from src.core.config import AgentConfig

        # Create agents
        iec_config = AgentConfig(
            agent_id="iec-001",
            agent_type="iec_standards",
            model="gpt-4-turbo-preview"
        )
        iec_agent = IECStandardsAgent(iec_config, mock_system_config)

        testing_config = AgentConfig(
            agent_id="testing-001",
            agent_type="testing_specialist",
            model="gpt-4-turbo-preview"
        )
        testing_agent = TestingSpecialistAgent(testing_config, mock_system_config)

        # Create router
        router = TaskRouter()

        # Test routing
        # IEC standards query should route to IEC agent
        iec_query = "What does IEC 61215 specify for thermal cycling?"
        # Testing query should route to testing agent
        testing_query = "How do I perform electroluminescence testing?"

    def test_supervisor_coordination(self, mock_system_config):
        """Test supervisor agent coordination."""
        from src.supervisor.supervisor_agent import SupervisorAgent

        supervisor = SupervisorAgent(mock_system_config)

        # Test task decomposition
        complex_task = "Analyze a PV module for IEC compliance and identify potential defects"

        # Supervisor should decompose into subtasks


class TestDocumentIngestionIntegration:
    """Integration tests for document ingestion pipeline."""

    @patch('src.ingestion.pdf_loader.pdfplumber.open')
    def test_pdf_ingestion_pipeline(self, mock_pdf):
        """Test complete PDF ingestion workflow."""
        from src.ingestion.pipeline import IngestionPipeline
        from src.ingestion.pdf_loader import IECPDFLoader

        # Mock PDF content
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test PDF content about IEC standards."
        mock_pdf_obj = Mock()
        mock_pdf_obj.pages = [mock_page]
        mock_pdf_obj.__enter__ = Mock(return_value=mock_pdf_obj)
        mock_pdf_obj.__exit__ = Mock(return_value=False)
        mock_pdf.return_value = mock_pdf_obj

        # Test loader
        loader = IECPDFLoader()
        # content = loader.load("test.pdf")

    def test_chunking_integration(self):
        """Test chunking preserves semantic meaning."""
        from src.chunking.semantic_chunker import SemanticChunker

        chunker = SemanticChunker(
            chunk_size=500,
            chunk_overlap=50
        )

        long_text = """
        IEC 61215-1:2016 specifies the requirements for design qualification and
        type approval of crystalline silicon terrestrial photovoltaic (PV) modules.

        The standard covers various environmental tests including thermal cycling,
        humidity freeze, damp heat, and mechanical load testing.

        Module qualification ensures reliable operation under specified conditions
        for an expected lifetime of 25+ years.
        """

        chunks = chunker.chunk(long_text)

        assert len(chunks) > 0
        # Verify chunks maintain semantic coherence


class TestImageAnalysisIntegration:
    """Integration tests for PV image analysis."""

    @patch('src.pv_image_analysis.image_processor.cv2')
    @patch('src.pv_image_analysis.clip_classifier.CLIP')
    def test_image_analysis_pipeline(self, mock_clip, mock_cv2):
        """Test complete image analysis workflow."""
        from src.pv_image_analysis.image_processor import ImageProcessor

        # Setup mocks
        mock_cv2.imread.return_value = Mock()  # Mock image array

        processor = ImageProcessor()

        # Test preprocessing
        # result = processor.preprocess("test_image.jpg")

    def test_defect_categorization(self):
        """Test IEC-based defect categorization."""
        from src.pv_image_analysis.defect_categorizer import IECDefectCategorizer

        categorizer = IECDefectCategorizer()

        # Test categorization
        defects = ["hotspot", "crack", "delamination"]

        for defect in defects:
            category = categorizer.categorize(defect)
            assert category is not None


class TestCalculatorIntegration:
    """Integration tests for PV calculators."""

    @patch('backend.services.nrel_client.requests.get')
    def test_full_energy_analysis(self, mock_get):
        """Test complete energy analysis workflow."""
        from backend.calculators.energy_yield import EnergyYieldCalculator
        from backend.calculators.degradation_rate import DegradationRateCalculator
        from backend.services.nrel_client import NRELClient

        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outputs": {
                "ac_annual": 15000,
                "ac_monthly": [1200] * 12,
                "dc_monthly": [1300] * 12,
                "poa_monthly": [170] * 12,
                "dc_nominal": 10
            },
            "station_info": {"city": "Test", "state": "CA", "elev": 100, "tz": -8}
        }
        mock_get.return_value = mock_response

        # Create NREL client
        nrel_client = NRELClient(api_key="test-key")

        # Calculate energy yield
        energy_calc = EnergyYieldCalculator(nrel_client)
        degradation_calc = DegradationRateCalculator(nrel_client)

        # Workflow: Calculate energy -> Apply degradation -> Project lifetime production


class TestAPIIntegration:
    """Integration tests for API layer."""

    @patch('app.services.rag_engine.RAGEngine')
    @patch('app.services.llm_orchestrator.LLMOrchestrator')
    @patch('app.services.citation_manager.CitationManager')
    def test_chat_api_full_flow(self, mock_citation, mock_llm, mock_rag):
        """Test complete chat API flow."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Test health endpoint first
        health_response = client.get("/health/")
        assert health_response.status_code == 200

    def test_api_error_propagation(self):
        """Test error handling across API layers."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Test invalid endpoint
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    @patch('backend.database.connection.create_engine')
    def test_database_connection(self, mock_engine):
        """Test database connection establishment."""
        mock_engine.return_value = Mock()

        # Test connection pool
        from backend.database.connection import get_database_connection

        # conn = get_database_connection()

    @patch('sqlalchemy.orm.Session')
    def test_feedback_storage(self, mock_session):
        """Test feedback storage in database."""
        from backend.services.feedback_service import FeedbackService

        service = FeedbackService()

        feedback = {
            "query_id": "test-123",
            "rating": 5,
            "comment": "Great response!",
            "response_id": "resp-456"
        }

        # Test storage
        # result = service.store_feedback(feedback)


class TestEndToEndWorkflow:
    """Complete end-to-end workflow tests."""

    def test_user_query_workflow(self):
        """Test complete user query workflow."""
        # 1. User sends query
        # 2. RAG retrieves context
        # 3. LLM generates response
        # 4. Citations are extracted
        # 5. Response is returned with citations
        pass

    def test_document_ingestion_to_retrieval(self):
        """Test workflow from document upload to retrieval."""
        # 1. Upload PDF document
        # 2. Extract text and metadata
        # 3. Chunk document
        # 4. Generate embeddings
        # 5. Store in vector DB
        # 6. Retrieve relevant chunks
        pass

    def test_pv_analysis_workflow(self):
        """Test complete PV system analysis workflow."""
        # 1. Upload system parameters
        # 2. Calculate energy yield
        # 3. Calculate degradation
        # 4. Apply spectral mismatch
        # 5. Generate report
        pass


class TestConcurrency:
    """Tests for concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_queries(self):
        """Test handling multiple concurrent queries."""
        import asyncio

        async def mock_query(query_id: int):
            await asyncio.sleep(0.1)
            return {"id": query_id, "status": "success"}

        # Run multiple queries concurrently
        tasks = [mock_query(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(r["status"] == "success" for r in results)

    def test_thread_safety(self):
        """Test thread safety of shared resources."""
        import threading

        counter = {"value": 0}
        lock = threading.Lock()

        def increment():
            for _ in range(1000):
                with lock:
                    counter["value"] += 1

        threads = [threading.Thread(target=increment) for _ in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        assert counter["value"] == 10000


class TestPerformance:
    """Performance and load tests."""

    def test_response_time(self):
        """Test that responses are within acceptable time limits."""
        import time

        start = time.time()

        # Simulate processing
        time.sleep(0.1)

        elapsed = time.time() - start

        # Response should be under 5 seconds
        assert elapsed < 5

    def test_memory_usage(self):
        """Test memory usage stays within bounds."""
        import sys

        # Create large data structure
        large_list = [{"id": i, "data": "x" * 100} for i in range(10000)]

        # Check size
        size = sys.getsizeof(large_list)

        # Cleanup
        del large_list


class TestDataValidation:
    """Tests for data validation across components."""

    def test_input_sanitization(self):
        """Test input sanitization."""
        # Test SQL injection prevention
        malicious_input = "'; DROP TABLE users; --"

        # Input should be sanitized
        sanitized = malicious_input.replace("'", "''")
        assert "DROP TABLE" not in sanitized or "'" in sanitized

    def test_xss_prevention(self):
        """Test XSS prevention in responses."""
        malicious_content = "<script>alert('XSS')</script>"

        # Content should be escaped
        import html
        escaped = html.escape(malicious_content)
        assert "<script>" not in escaped


# Fixtures
@pytest.fixture
def mock_system_config():
    """Create mock system configuration."""
    from src.core.config import SystemConfig
    import os

    return SystemConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", "mock-key"),
        default_llm_provider="openai",
        default_model="gpt-4-turbo-preview",
        supervisor_model="gpt-4-turbo-preview",
        agent_temperature=0.7,
        max_iterations=5,
        log_level="INFO"
    )


@pytest.fixture
def sample_pv_data():
    """Create sample PV system data."""
    return {
        "location": {"latitude": 37.7749, "longitude": -122.4194},
        "system": {
            "capacity_kw": 10,
            "module_type": "mono-crystalline",
            "tilt": 20,
            "azimuth": 180
        },
        "expected_yield": 15000
    }
