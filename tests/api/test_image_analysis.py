"""
Tests for image analysis endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_analyze_image(client: TestClient, auth_headers: dict, sample_image_base64: str):
    """Test image analysis endpoint."""
    request_data = {
        "image_base64": sample_image_base64,
        "analysis_type": "defect_detection"
    }

    response = client.post(
        "/image-analysis/analyze",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "defects" in data
    assert "overall_health_score" in data
    assert "processing_time" in data
    assert "image_dimensions" in data
    assert "recommendations" in data

    assert isinstance(data["defects"], list)
    assert 0 <= data["overall_health_score"] <= 100
    assert "width" in data["image_dimensions"]
    assert "height" in data["image_dimensions"]


def test_analyze_missing_image(client: TestClient, auth_headers: dict):
    """Test analysis without image returns error."""
    request_data = {
        "analysis_type": "defect_detection"
    }

    response = client.post(
        "/image-analysis/analyze",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 400


def test_get_supported_defects(client: TestClient, auth_headers: dict):
    """Test get supported defects endpoint."""
    response = client.get(
        "/image-analysis/supported-defects",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "supported_defects" in data
    assert "defect_types" in data
    assert data["supported_defects"] > 0


def test_analyze_requires_auth(client: TestClient, sample_image_base64: str):
    """Test image analysis requires authentication."""
    request_data = {
        "image_base64": sample_image_base64
    }

    response = client.post(
        "/image-analysis/analyze",
        json=request_data
    )

    assert response.status_code == 403
