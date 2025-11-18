"""Integration tests for the API."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.orchestrator.api import create_app
from src.orchestrator.models import QueryRequest, QueryType, LLMProvider


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_orchestrator_response():
    """Mock orchestrator response."""
    from src.orchestrator.models import OrchestratorResponse, LLMResponse

    return OrchestratorResponse(
        response="This is a test response about solar panels.",
        primary_llm=LLMProvider.GPT,
        query_type=QueryType.STANDARD_INTERPRETATION,
        classification_confidence=0.85,
        responses=[
            LLMResponse(
                provider=LLMProvider.GPT,
                content="Test response",
                model="gpt-4o",
                tokens_used=100,
            )
        ],
        is_hybrid=False,
        fallback_used=False,
        total_latency_ms=500.0,
    )


class TestAPI:
    """Test suite for REST API."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Solar PV Multi-LLM Orchestrator"
        assert data["status"] == "operational"
        assert "endpoints" in data

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data

    def test_list_models(self, client):
        """Test models listing endpoint."""
        response = client.get("/api/v1/models")

        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "gpt" in data["models"]
        assert "claude" in data["models"]
        assert "routing" in data

    def test_list_query_types(self, client):
        """Test query types listing endpoint."""
        response = client.get("/api/v1/query-types")

        assert response.status_code == 200
        data = response.json()
        assert "query_types" in data
        assert "calculation" in data["query_types"]
        assert "image_analysis" in data["query_types"]

    @patch("src.orchestrator.service.OrchestratorService.process_query")
    def test_process_query_success(
        self, mock_process, client, mock_orchestrator_response
    ):
        """Test successful query processing."""
        mock_process.return_value = mock_orchestrator_response

        request_data = {
            "query": "What is a solar inverter?",
            "max_tokens": 2000,
            "temperature": 0.7,
        }

        response = client.post("/api/v1/query", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "primary_llm" in data
        assert "query_type" in data

    def test_process_query_empty(self, client):
        """Test query with empty input."""
        request_data = {"query": ""}

        response = client.post("/api/v1/query", json=request_data)

        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_process_query_missing_field(self, client):
        """Test query with missing required field."""
        request_data = {}

        response = client.post("/api/v1/query", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_openapi_docs_available(self, client):
        """Test that OpenAPI docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/redoc")
        assert response.status_code == 200


class TestAPIQueryProcessing:
    """Test suite for query processing through API."""

    @patch("src.orchestrator.service.OrchestratorService.process_query")
    def test_calculation_query(self, mock_process, client, mock_orchestrator_response):
        """Test processing a calculation query."""
        mock_orchestrator_response.query_type = QueryType.CALCULATION
        mock_process.return_value = mock_orchestrator_response

        request_data = {
            "query": "Calculate energy yield for 10kW system",
            "query_type": "calculation",
        }

        response = client.post("/api/v1/query", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["query_type"] == "calculation"

    @patch("src.orchestrator.service.OrchestratorService.process_query")
    def test_preferred_llm(self, mock_process, client, mock_orchestrator_response):
        """Test query with preferred LLM."""
        mock_orchestrator_response.primary_llm = LLMProvider.CLAUDE
        mock_process.return_value = mock_orchestrator_response

        request_data = {
            "query": "Explain solar panels",
            "preferred_llm": "claude",
        }

        response = client.post("/api/v1/query", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["primary_llm"] == "claude"
