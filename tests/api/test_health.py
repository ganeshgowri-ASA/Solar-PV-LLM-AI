"""
Tests for health and metrics endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert "services" in data

    assert data["status"] in ["healthy", "degraded", "unhealthy"]


def test_metrics_endpoint(client: TestClient):
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_root_redirect(client: TestClient):
    """Test root endpoint redirects to docs."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/docs"


def test_ping(client: TestClient):
    """Test ping endpoint."""
    response = client.get("/ping")
    assert response.status_code == 200

    data = response.json()
    assert "pong" in data
    assert "status" in data
    assert data["status"] == "ok"
