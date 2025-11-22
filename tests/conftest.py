"""
Pytest configuration and shared fixtures.
"""
import pytest
from datetime import datetime, timedelta
import numpy as np
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def sample_location():
    """Sample location coordinates (Boulder, CO)."""
    return {
        "latitude": 40.0150,
        "longitude": -105.2705
    }


@pytest.fixture
def sample_system_parameters():
    """Sample PV system parameters."""
    return {
        "system_capacity": 4.0,  # 4 kW
        "module_type": 0,  # Standard
        "array_type": 0,  # Fixed
        "tilt": 20,
        "azimuth": 180,  # South
        "losses": 14.08,
        "albedo": 0.2
    }


@pytest.fixture
def sample_degradation_data():
    """Generate sample degradation data with realistic degradation."""
    # Simulate 3 years of monthly data with -0.5%/year degradation
    start_date = datetime(2020, 1, 1)
    degradation_rate = -0.005  # -0.5% per year

    data_points = []
    for month in range(36):  # 3 years
        timestamp = start_date + timedelta(days=30 * month)
        years_elapsed = month / 12

        # Base normalized output with degradation
        normalized_output = 1.0 + (degradation_rate * years_elapsed)

        # Add small random noise (±2%)
        noise = np.random.normal(0, 0.02)
        normalized_output += noise

        data_points.append({
            "timestamp": timestamp.isoformat(),
            "normalized_output": max(0.5, min(1.1, normalized_output))  # Clamp
        })

    return data_points


@pytest.fixture
def sample_spectral_data():
    """Generate sample spectral data for mismatch calculation."""
    # Wavelength range from 300 to 1200 nm (typical for silicon cells)
    wavelengths = np.linspace(300, 1200, 100).tolist()

    # Simplified AM1.5G reference spectrum (normalized)
    # Peak around 500 nm (green light)
    reference_spectrum = []
    for wl in wavelengths:
        if wl < 300:
            irradiance = 0
        elif wl < 500:
            irradiance = (wl - 300) / 200 * 1.5
        elif wl < 800:
            irradiance = 1.5 - (wl - 500) / 300 * 0.5
        else:
            irradiance = 1.0 - (wl - 800) / 400 * 0.8
        reference_spectrum.append(max(0, irradiance))

    # Test spectrum (slightly different - more blue light)
    incident_spectrum = []
    for wl in wavelengths:
        if wl < 300:
            irradiance = 0
        elif wl < 500:
            irradiance = (wl - 300) / 200 * 1.7  # More blue
        elif wl < 800:
            irradiance = 1.7 - (wl - 500) / 300 * 0.7
        else:
            irradiance = 1.0 - (wl - 800) / 400 * 0.8
        incident_spectrum.append(max(0, irradiance))

    # Silicon cell spectral response (simplified)
    # Peak quantum efficiency around 800-900 nm
    cell_response = []
    for wl in wavelengths:
        if wl < 300:
            response = 0
        elif wl < 400:
            response = (wl - 300) / 100 * 0.5
        elif wl < 900:
            response = 0.5 + (wl - 400) / 500 * 0.3
        elif wl < 1100:
            response = 0.8 - (wl - 900) / 200 * 0.4
        else:
            response = max(0, 0.4 - (wl - 1100) / 100 * 0.4)
        cell_response.append(max(0, response))

    return {
        "wavelengths": wavelengths,
        "incident_spectrum": incident_spectrum,
        "reference_spectrum": reference_spectrum,
        "cell_spectral_response": cell_response
    }


@pytest.fixture
def mock_pvwatts_response():
    """Mock PVWatts API response."""
    return {
        "inputs": {
            "lat": 40.0150,
            "lon": -105.2705,
            "system_capacity": 4.0,
            "module_type": 0,
            "array_type": 0,
            "tilt": 20,
            "azimuth": 180,
            "losses": 14.08
        },
        "outputs": {
            "ac_monthly": [
                443.2, 465.3, 571.4, 586.2, 618.7, 637.4,
                651.9, 623.5, 567.8, 512.3, 432.1, 409.6
            ],
            "poa_monthly": [
                128.5, 135.2, 167.8, 173.2, 184.5, 191.3,
                196.7, 188.9, 172.1, 154.8, 129.7, 122.3
            ],
            "dc_monthly": [
                458.3, 481.2, 591.5, 606.8, 640.5, 660.1,
                675.2, 645.6, 587.9, 530.4, 447.3, 423.9
            ],
            "ac_annual": 6519.4,
            "solrad_annual": 5.18,
            "capacity_factor": 18.6,
            "dc_nominal": 4.0
        },
        "station_info": {
            "lat": 40.02,
            "lon": -105.25,
            "elev": 1655,
            "tz": -7.0,
            "location": "94018",
            "city": "Boulder",
            "state": "Colorado",
            "dataset": "nsrdb"
        },
        "version": "1.1.0",
        "errors": []
    }
