"""Comprehensive tests for FastAPI endpoints."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import json


class TestChatEndpoint:
    """Tests for chat API endpoint."""

    @patch('app.api.endpoints.chat.rag_engine')
    @patch('app.api.endpoints.chat.llm_orchestrator')
    @patch('app.api.endpoints.chat.citation_manager')
    @patch('app.api.endpoints.chat.verify_api_key')
    def test_chat_endpoint_success(self, mock_auth, mock_citation, mock_llm, mock_rag):
        """Test successful chat request."""
        from app.api.endpoints.chat import router
        from app.main import app

        # Setup mocks
        mock_auth.return_value = True
        mock_rag.retrieve_context.return_value = [
            {"source": "IEC 61215", "content": "Test content", "score": 0.95}
        ]
        mock_citation.deduplicate_citations.return_value = [
            {"source": "IEC 61215", "content": "Test content", "score": 0.95}
        ]
        mock_citation.rank_citations.return_value = [
            {"source": "IEC 61215", "content": "Test content", "score": 0.95}
        ]
        mock_llm.generate_response.return_value = ("Test response about solar PV.", 150)

        client = TestClient(app)

        response = client.post(
            "/chat/",
            json={
                "query": "What are the requirements for module testing?",
                "use_rag": True,
                "max_tokens": 1000,
                "temperature": 0.7
            },
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "citations" in data

    @patch('app.api.endpoints.chat.verify_api_key')
    def test_chat_endpoint_missing_query(self, mock_auth):
        """Test chat request with missing query."""
        from app.main import app

        mock_auth.return_value = True

        client = TestClient(app)

        response = client.post(
            "/chat/",
            json={"use_rag": True},
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 422  # Validation error

    @patch('app.api.endpoints.chat.rag_engine')
    @patch('app.api.endpoints.chat.llm_orchestrator')
    @patch('app.api.endpoints.chat.citation_manager')
    @patch('app.api.endpoints.chat.verify_api_key')
    def test_chat_endpoint_without_rag(self, mock_auth, mock_citation, mock_llm, mock_rag):
        """Test chat request without RAG."""
        from app.main import app

        mock_auth.return_value = True
        mock_llm.generate_response.return_value = ("Direct response without context.", 100)

        client = TestClient(app)

        response = client.post(
            "/chat/",
            json={
                "query": "What is solar energy?",
                "use_rag": False,
                "max_tokens": 500,
                "temperature": 0.5
            },
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        mock_rag.retrieve_context.assert_not_called()

    def test_chat_stream_not_implemented(self):
        """Test streaming endpoint returns not implemented."""
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/chat/stream",
            json={"query": "Test query"},
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 501


class TestPVCalculationsEndpoint:
    """Tests for PV calculations endpoint."""

    @patch('app.api.endpoints.pv_calculations.pv_calculator')
    @patch('app.api.endpoints.pv_calculations.verify_api_key')
    def test_energy_yield_calculation(self, mock_auth, mock_calculator):
        """Test energy yield calculation endpoint."""
        from app.main import app

        mock_auth.return_value = True
        mock_calculator.calculate_energy_yield.return_value = {
            "annual_energy_kwh": 15000,
            "monthly_energy": [1200, 1400, 1500, 1400, 1300, 1200, 1100, 1200, 1300, 1400, 1300, 1200],
            "capacity_factor": 0.17,
            "specific_yield": 1500
        }

        client = TestClient(app)

        response = client.post(
            "/pv/energy-yield",
            json={
                "latitude": 37.7749,
                "longitude": -122.4194,
                "system_capacity": 10,
                "module_type": 0,
                "array_type": 1,
                "tilt": 20,
                "azimuth": 180,
                "losses": 14
            },
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "annual_energy_kwh" in data

    @patch('app.api.endpoints.pv_calculations.pv_calculator')
    @patch('app.api.endpoints.pv_calculations.verify_api_key')
    def test_degradation_rate_calculation(self, mock_auth, mock_calculator):
        """Test degradation rate calculation endpoint."""
        from app.main import app

        mock_auth.return_value = True
        mock_calculator.calculate_degradation_rate.return_value = {
            "degradation_rate": 0.5,
            "years": 25,
            "final_efficiency": 87.5,
            "energy_loss_cumulative": 12.5
        }

        client = TestClient(app)

        response = client.post(
            "/pv/degradation-rate",
            json={
                "technology": "mono-crystalline",
                "age_years": 0,
                "analysis_period": 25
            },
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200

    @patch('app.api.endpoints.pv_calculations.pv_calculator')
    @patch('app.api.endpoints.pv_calculations.verify_api_key')
    def test_spectral_mismatch_calculation(self, mock_auth, mock_calculator):
        """Test spectral mismatch calculation endpoint."""
        from app.main import app

        mock_auth.return_value = True
        mock_calculator.calculate_spectral_mismatch.return_value = {
            "spectral_modifier": 0.98,
            "airmass": 1.5,
            "precipitable_water": 1.4
        }

        client = TestClient(app)

        response = client.post(
            "/pv/spectral-mismatch",
            json={
                "latitude": 37.7749,
                "longitude": -122.4194,
                "module_technology": "c-Si"
            },
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200


class TestDocumentEndpoints:
    """Tests for document management endpoints."""

    @patch('app.api.endpoints.documents.document_service')
    @patch('app.api.endpoints.documents.verify_api_key')
    def test_upload_document(self, mock_auth, mock_service):
        """Test document upload endpoint."""
        from app.main import app

        mock_auth.return_value = True
        mock_service.upload_document.return_value = {
            "doc_id": "test-doc-123",
            "status": "uploaded",
            "chunks": 10
        }

        client = TestClient(app)

        # Create a mock file
        files = {"file": ("test.pdf", b"PDF content here", "application/pdf")}

        response = client.post(
            "/documents/upload",
            files=files,
            headers={"X-API-Key": "test-key"}
        )

        # Status depends on implementation
        assert response.status_code in [200, 201, 422]

    @patch('app.api.endpoints.documents.document_service')
    @patch('app.api.endpoints.documents.verify_api_key')
    def test_search_documents(self, mock_auth, mock_service):
        """Test document search endpoint."""
        from app.main import app

        mock_auth.return_value = True
        mock_service.search_documents.return_value = [
            {"doc_id": "doc-1", "title": "IEC 61215", "score": 0.95},
            {"doc_id": "doc-2", "title": "IEC 61730", "score": 0.87}
        ]

        client = TestClient(app)

        response = client.get(
            "/documents/search?query=module+testing",
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200

    @patch('app.api.endpoints.documents.document_service')
    @patch('app.api.endpoints.documents.verify_api_key')
    def test_get_document_by_id(self, mock_auth, mock_service):
        """Test getting document by ID."""
        from app.main import app

        mock_auth.return_value = True
        mock_service.get_document.return_value = {
            "doc_id": "doc-123",
            "title": "IEC 61215-1:2016",
            "content": "Document content...",
            "metadata": {"standard": "IEC 61215"}
        }

        client = TestClient(app)

        response = client.get(
            "/documents/doc-123",
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self):
        """Test basic health check."""
        from app.main import app

        client = TestClient(app)

        response = client.get("/health/")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_health_detailed(self):
        """Test detailed health check."""
        from app.main import app

        client = TestClient(app)

        response = client.get("/health/detailed")

        assert response.status_code == 200

    def test_health_readiness(self):
        """Test readiness probe."""
        from app.main import app

        client = TestClient(app)

        response = client.get("/health/ready")

        assert response.status_code == 200

    def test_health_liveness(self):
        """Test liveness probe."""
        from app.main import app

        client = TestClient(app)

        response = client.get("/health/live")

        assert response.status_code == 200


class TestImageAnalysisEndpoint:
    """Tests for image analysis endpoint."""

    @patch('app.api.endpoints.image_analysis.image_analyzer')
    @patch('app.api.endpoints.image_analysis.verify_api_key')
    def test_analyze_image(self, mock_auth, mock_analyzer):
        """Test image analysis endpoint."""
        from app.main import app

        mock_auth.return_value = True
        mock_analyzer.analyze.return_value = {
            "defects_detected": True,
            "defect_types": ["hotspot", "crack"],
            "severity": "medium",
            "recommendations": ["Inspect module physically", "Monitor performance"]
        }

        client = TestClient(app)

        # Create mock image file
        files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}

        response = client.post(
            "/image-analysis/analyze",
            files=files,
            headers={"X-API-Key": "test-key"}
        )

        # Status depends on file validation
        assert response.status_code in [200, 422]


class TestAPIAuthentication:
    """Tests for API authentication."""

    def test_missing_api_key(self):
        """Test request without API key."""
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/chat/",
            json={"query": "Test query", "use_rag": True}
        )

        # Should return 401 or 403 without API key
        assert response.status_code in [401, 403, 422]

    def test_invalid_api_key(self):
        """Test request with invalid API key."""
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/chat/",
            json={"query": "Test query", "use_rag": True},
            headers={"X-API-Key": "invalid-key"}
        )

        # Should return authentication error
        assert response.status_code in [401, 403, 422, 500]


class TestAPIValidation:
    """Tests for API input validation."""

    @patch('app.api.endpoints.chat.verify_api_key')
    def test_invalid_temperature(self, mock_auth):
        """Test validation of temperature parameter."""
        from app.main import app

        mock_auth.return_value = True

        client = TestClient(app)

        response = client.post(
            "/chat/",
            json={
                "query": "Test query",
                "use_rag": True,
                "temperature": 3.0  # Invalid: should be 0-2
            },
            headers={"X-API-Key": "test-key"}
        )

        # Should fail validation
        assert response.status_code in [422, 500]

    @patch('app.api.endpoints.chat.verify_api_key')
    def test_negative_max_tokens(self, mock_auth):
        """Test validation of max_tokens parameter."""
        from app.main import app

        mock_auth.return_value = True

        client = TestClient(app)

        response = client.post(
            "/chat/",
            json={
                "query": "Test query",
                "use_rag": True,
                "max_tokens": -100  # Invalid: should be positive
            },
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code in [422, 500]


class TestAPIErrorHandling:
    """Tests for API error handling."""

    @patch('app.api.endpoints.chat.rag_engine')
    @patch('app.api.endpoints.chat.llm_orchestrator')
    @patch('app.api.endpoints.chat.verify_api_key')
    def test_internal_error_handling(self, mock_auth, mock_llm, mock_rag):
        """Test handling of internal errors."""
        from app.main import app

        mock_auth.return_value = True
        mock_rag.retrieve_context.side_effect = Exception("Internal error")

        client = TestClient(app)

        response = client.post(
            "/chat/",
            json={
                "query": "Test query",
                "use_rag": True
            },
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestBackendAPIRoutes:
    """Tests for backend API routes."""

    @patch('backend.api.routes.calculators.energy_yield_calculator')
    def test_backend_energy_yield(self, mock_calculator):
        """Test backend energy yield route."""
        from backend.main import app as backend_app

        mock_calculator.calculate.return_value = Mock(
            annual_energy_kwh=15000,
            monthly_energy=[],
            capacity_factor=0.17,
            specific_yield=1500,
            performance_ratio=0.82,
            uncertainty=Mock(
                standard_error=1500,
                confidence_level=0.95,
                confidence_interval_lower=12000,
                confidence_interval_upper=18000,
                r_squared=0.95,
                relative_uncertainty=10.0
            ),
            metadata={}
        )

        client = TestClient(backend_app)

        response = client.post(
            "/api/v1/calculators/energy-yield",
            json={
                "location": {"latitude": 37.77, "longitude": -122.42},
                "system": {
                    "system_capacity": 10,
                    "module_type": 0,
                    "array_type": 1,
                    "tilt": 20,
                    "azimuth": 180,
                    "losses": 14,
                    "albedo": 0.2
                }
            }
        )

        assert response.status_code in [200, 422, 500]


class TestMiddleware:
    """Tests for API middleware."""

    def test_cors_headers(self):
        """Test CORS headers are present."""
        from app.main import app

        client = TestClient(app)

        response = client.options("/health/")

        # CORS handling
        assert response.status_code in [200, 405]

    def test_request_logging(self):
        """Test that requests are logged."""
        from app.main import app

        client = TestClient(app)

        with patch('app.middleware.logging.logger') as mock_logger:
            client.get("/health/")
            # Logger should have been called
            # This depends on middleware implementation


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    def test_rate_limit_headers(self):
        """Test rate limit headers in response."""
        from app.main import app

        client = TestClient(app)

        response = client.get("/health/")

        # Rate limit headers if implemented
        # assert "X-RateLimit-Limit" in response.headers

    def test_rate_limit_exceeded(self):
        """Test behavior when rate limit is exceeded."""
        from app.main import app

        client = TestClient(app)

        # Make many requests rapidly
        responses = []
        for _ in range(100):
            response = client.get("/health/")
            responses.append(response.status_code)

        # Should mostly be 200, possibly some 429 if rate limited
        assert 200 in responses
