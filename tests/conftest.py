"""Comprehensive pytest configuration and fixtures for Solar PV LLM AI testing."""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables before imports
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("PINECONE_API_KEY", "test-pinecone-key")
os.environ.setdefault("PINECONE_ENVIRONMENT", "us-east-1")
os.environ.setdefault("PINECONE_INDEX_NAME", "test-index")
os.environ.setdefault("NREL_API_KEY", "test-nrel-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


# ============================================================================
# Agent Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_system_config():
    """Create a mock system configuration."""
    from src.core.config import SystemConfig

    config = SystemConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", "mock-key"),
        default_llm_provider="openai",
        default_model="gpt-4-turbo-preview",
        supervisor_model="gpt-4-turbo-preview",
        agent_temperature=0.7,
        max_iterations=5,
        log_level="INFO"
    )
    return config


@pytest.fixture
def mock_agent_config():
    """Create a mock agent configuration."""
    from src.core.config import AgentConfig

    return AgentConfig(
        agent_id="test_agent_001",
        agent_type="test_agent",
        model="gpt-4-turbo-preview",
        temperature=0.7,
        max_tokens=2000
    )


@pytest.fixture
def iec_agent(mock_system_config):
    """Create an IEC standards agent for testing."""
    from src.core.config import AgentConfig
    from src.agents.iec_standards_agent import IECStandardsAgent

    config = AgentConfig(
        agent_id="iec_standards_001",
        agent_type="iec_standards_expert",
        model="gpt-4-turbo-preview",
        temperature=0.7
    )
    return IECStandardsAgent(config, mock_system_config)


@pytest.fixture
def testing_agent(mock_system_config):
    """Create a testing specialist agent for testing."""
    from src.core.config import AgentConfig
    from src.agents.testing_specialist_agent import TestingSpecialistAgent

    config = AgentConfig(
        agent_id="testing_specialist_001",
        agent_type="testing_specialist",
        model="gpt-4-turbo-preview",
        temperature=0.7
    )
    return TestingSpecialistAgent(config, mock_system_config)


@pytest.fixture
def performance_agent(mock_system_config):
    """Create a performance analyst agent for testing."""
    from src.core.config import AgentConfig
    from src.agents.performance_analyst_agent import PerformanceAnalystAgent

    config = AgentConfig(
        agent_id="performance_analyst_001",
        agent_type="performance_analyst",
        model="gpt-4-turbo-preview",
        temperature=0.7
    )
    return PerformanceAnalystAgent(config, mock_system_config)


@pytest.fixture
def all_agents(iec_agent, testing_agent, performance_agent):
    """Return all agents as a list."""
    return [iec_agent, testing_agent, performance_agent]


# ============================================================================
# LLM Response Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    mock = Mock()
    mock.content = "This is a test response from the LLM."
    return mock


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""
    mock_response = Mock()
    mock_choice = Mock()
    mock_choice.message.content = "Test OpenAI response about solar PV."
    mock_choice.finish_reason = "stop"
    mock_response.choices = [mock_choice]
    mock_response.usage = Mock(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150
    )
    return mock_response


@pytest.fixture
def mock_anthropic_response():
    """Create a mock Anthropic API response."""
    mock_response = Mock()
    mock_response.content = [Mock(text="Test Anthropic response about solar PV.")]
    mock_response.stop_reason = "end_turn"
    mock_response.usage = Mock(
        input_tokens=100,
        output_tokens=50
    )
    return mock_response


# ============================================================================
# Document and RAG Fixtures
# ============================================================================

@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    from src.rag_engine.utils.data_models import Document

    return [
        Document(
            id="iec-61215-1",
            content="IEC 61215-1 specifies the requirements for design qualification and type approval of crystalline silicon terrestrial photovoltaic modules.",
            metadata={"standard": "IEC 61215-1", "type": "qualification", "year": 2016}
        ),
        Document(
            id="iec-61730-1",
            content="IEC 61730-1 defines the requirements for construction of photovoltaic modules to provide safe electrical and mechanical operation.",
            metadata={"standard": "IEC 61730-1", "type": "safety", "year": 2016}
        ),
        Document(
            id="pv-degradation",
            content="Photovoltaic module degradation rates typically range from 0.5% to 1% per year depending on technology and environmental conditions.",
            metadata={"topic": "degradation", "type": "technical"}
        ),
        Document(
            id="iec-61853-1",
            content="IEC 61853-1 describes requirements for measuring the power rating of photovoltaic devices at various operating conditions.",
            metadata={"standard": "IEC 61853-1", "type": "performance", "year": 2011}
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
        ),
        RetrievalResult(
            document=sample_documents[2],
            score=0.82,
            rank=3,
            retrieval_method="hybrid"
        )
    ]


@pytest.fixture
def mock_rag_config():
    """Create a mock RAG configuration."""
    config = Mock()
    config.vector_store.embedding_model = "all-MiniLM-L6-v2"
    config.vector_store.store_type = "memory"
    config.vector_store.store_path = "/tmp/test_vector_store"
    config.vector_store.collection_name = "test_collection"
    config.retrieval.hybrid_alpha = 0.5
    config.retrieval.top_k = 10
    config.retrieval.top_k_rerank = 5
    config.reranker.reranker_type = "none"
    config.reranker.cohere_api_key = None
    config.reranker.cross_encoder_model = None
    config.hyde.enabled = False
    config.hyde.openai_api_key = None
    config.hyde.llm_model = None
    config.hyde.prompt_template = None
    return config


# ============================================================================
# Calculator Fixtures
# ============================================================================

@pytest.fixture
def mock_nrel_client():
    """Create a mock NREL API client."""
    client = Mock()
    client.get_pvwatts_data.return_value = {
        "outputs": {
            "ac_annual": 15000,
            "ac_monthly": [1000, 1100, 1300, 1400, 1500, 1450, 1400, 1350, 1300, 1200, 1100, 900],
            "dc_monthly": [1100, 1200, 1400, 1500, 1600, 1550, 1500, 1450, 1400, 1300, 1200, 1000],
            "poa_monthly": [150, 165, 190, 200, 210, 205, 200, 195, 185, 170, 155, 140],
            "dc_nominal": 10
        },
        "station_info": {
            "city": "San Francisco",
            "state": "CA",
            "elev": 16,
            "tz": -8,
            "dataset": "nsrdb"
        }
    }
    return client


@pytest.fixture
def sample_pv_system():
    """Create sample PV system configuration."""
    return {
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194
        },
        "system": {
            "system_capacity": 10,  # kW
            "module_type": 0,  # Standard
            "array_type": 1,  # Fixed open rack
            "tilt": 20,  # degrees
            "azimuth": 180,  # degrees
            "losses": 14,  # percent
            "albedo": 0.2
        }
    }


# ============================================================================
# API Testing Fixtures
# ============================================================================

@pytest.fixture
def test_client():
    """Create a FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)


@pytest.fixture
def authenticated_client(test_client):
    """Create an authenticated test client."""
    test_client.headers["X-API-Key"] = "test-api-key"
    return test_client


@pytest.fixture
def mock_api_key_verification():
    """Mock API key verification to always pass."""
    with patch('app.core.security.verify_api_key', return_value=True):
        yield


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = Mock()
    session.query.return_value.filter.return_value.first.return_value = None
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


# ============================================================================
# Vector Store Fixtures
# ============================================================================

@pytest.fixture
def mock_pinecone_client():
    """Create a mock Pinecone client."""
    with patch('src.vector_store.pinecone_client.Pinecone') as mock_pc:
        mock_instance = Mock()
        mock_index = Mock()
        mock_index_obj = Mock()
        mock_index_obj.name = "test-index"

        mock_instance.list_indexes.return_value = [mock_index_obj]
        mock_instance.Index.return_value = mock_index

        mock_pc.return_value = mock_instance

        yield mock_instance


@pytest.fixture
def mock_embedding_model():
    """Create a mock embedding model."""
    with patch('src.vector_store.embeddings.SentenceTransformer') as mock_st:
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1] * 384]
        mock_st.return_value = mock_model
        yield mock_model


# ============================================================================
# Citation Fixtures
# ============================================================================

@pytest.fixture
def sample_citations():
    """Create sample citations for testing."""
    return [
        {
            "source": "IEC 61215-1:2016",
            "content": "Module qualification requirements",
            "score": 0.95,
            "section": "5.1"
        },
        {
            "source": "IEC 61730-1:2016",
            "content": "Safety requirements for PV modules",
            "score": 0.87,
            "section": "4.2"
        },
        {
            "source": "IEC 61853-1:2011",
            "content": "Performance testing standards",
            "score": 0.82,
            "section": "6.3"
        }
    ]


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test."""
    yield
    # Cleanup code here if needed


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before all tests."""
    # Create necessary test directories
    test_dirs = [
        project_root / "data" / "test",
        project_root / "data" / "test" / "vector_store"
    ]
    for dir_path in test_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)

    yield

    # Cleanup after all tests
    import shutil
    for dir_path in test_dirs:
        if dir_path.exists():
            shutil.rmtree(dir_path, ignore_errors=True)


# ============================================================================
# Async Fixtures
# ============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_async_client():
    """Create a mock async HTTP client."""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    return mock_client


# ============================================================================
# Marker Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "asyncio: Async tests")
