"""
Tests for main application
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns health status"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Solar PV LLM AI"
    assert "version" in data


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "services" in data


def test_health_endpoint_shows_services():
    """Test health endpoint shows service statuses"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    services = data["services"]

    assert "openai" in services
    assert "anthropic" in services
    assert "pinecone" in services
    assert "nrel" in services
    assert isinstance(services["openai"], bool)
    assert isinstance(services["anthropic"], bool)
