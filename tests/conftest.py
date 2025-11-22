"""
Pytest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Authentication headers for testing."""
    return {"X-API-Key": settings.API_KEY}


@pytest.fixture
def sample_pv_input():
    """Sample PV system input for testing."""
    return {
        "panel_capacity_kw": 5.0,
        "panel_efficiency": 0.2,
        "system_losses": 0.14,
        "tilt_angle": 30.0,
        "azimuth_angle": 180.0,
        "location_lat": 37.7749,
        "location_lon": -122.4194
    }


@pytest.fixture
def sample_image_base64():
    """Sample base64 encoded image for testing."""
    # Simple 1x1 pixel PNG image
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "query": "What is the optimal tilt angle for solar panels?",
        "use_rag": True,
        "max_tokens": 500,
        "temperature": 0.7
    }
