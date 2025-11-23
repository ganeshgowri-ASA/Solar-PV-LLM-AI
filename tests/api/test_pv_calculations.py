"""
Tests for PV calculation endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_estimate_output(client: TestClient, auth_headers: dict, sample_pv_input: dict):
    """Test PV output estimation."""
    response = client.post(
        "/pv/estimate-output",
        json=sample_pv_input,
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "daily_energy_kwh" in data
    assert "monthly_energy_kwh" in data
    assert "annual_energy_kwh" in data
    assert "capacity_factor" in data
    assert "peak_sun_hours" in data

    assert data["daily_energy_kwh"] > 0
    assert data["annual_energy_kwh"] > data["monthly_energy_kwh"]
    assert 0 <= data["capacity_factor"] <= 1


def test_performance_ratio(client: TestClient, auth_headers: dict):
    """Test performance ratio calculation."""
    response = client.post(
        "/pv/performance-ratio?actual_output_kwh=8500&expected_output_kwh=10000",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "performance_ratio" in data
    assert "efficiency_loss" in data

    assert 0 <= data["performance_ratio"] <= 1
    assert data["performance_ratio"] == 0.85  # 8500/10000


def test_optimal_tilt(client: TestClient, auth_headers: dict):
    """Test optimal tilt calculation."""
    latitude = 37.7749  # San Francisco

    response = client.get(
        f"/pv/optimal-tilt/{latitude}",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "annual_optimal" in data
    assert "summer_optimal" in data
    assert "winter_optimal" in data

    assert 0 <= data["annual_optimal"] <= 90
    assert data["summer_optimal"] < data["winter_optimal"]


def test_payback_period(client: TestClient, auth_headers: dict):
    """Test payback period calculation."""
    response = client.get(
        "/pv/payback-period?system_cost=15000&annual_savings=2000&annual_degradation=0.005",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "simple_payback_years" in data
    assert "adjusted_payback_years" in data
    assert "total_25year_savings" in data

    assert data["simple_payback_years"] == 7.5  # 15000/2000
    assert data["adjusted_payback_years"] > data["simple_payback_years"]


def test_peak_sun_hours(client: TestClient, auth_headers: dict):
    """Test peak sun hours calculation."""
    response = client.get(
        "/pv/peak-sun-hours?latitude=37.7749&tilt_angle=30",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "peak_sun_hours" in data
    assert data["peak_sun_hours"] > 0


def test_invalid_latitude(client: TestClient, auth_headers: dict):
    """Test invalid latitude returns error."""
    response = client.get(
        "/pv/optimal-tilt/999",
        headers=auth_headers
    )

    assert response.status_code == 400
