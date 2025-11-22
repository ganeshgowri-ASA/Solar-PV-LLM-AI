"""
Integration tests for API endpoints.
"""
import pytest
from unittest.mock import patch
from fastapi import status


class TestHealthCheckEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, test_client):
        """Test health check endpoint returns healthy status."""
        response = test_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "nrel_api_available" in data

    def test_root_endpoint(self, test_client):
        """Test root endpoint returns API info."""
        response = test_client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestEnergyYieldEndpoint:
    """Test Energy Yield Calculator API endpoint."""

    @patch('backend.services.nrel_client.nrel_client.get_pvwatts_data')
    def test_energy_yield_calculation(
        self,
        mock_pvwatts,
        test_client,
        sample_location,
        sample_system_parameters,
        mock_pvwatts_response
    ):
        """Test energy yield calculation endpoint."""
        mock_pvwatts.return_value = mock_pvwatts_response

        payload = {
            "location": sample_location,
            "system": sample_system_parameters
        }

        response = test_client.post(
            "/api/v1/calculators/energy-yield",
            json=payload
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "annual_energy_kwh" in data
        assert "monthly_energy" in data
        assert "capacity_factor" in data
        assert "specific_yield" in data
        assert "performance_ratio" in data
        assert "uncertainty" in data
        assert "metadata" in data

        # Check monthly energy is array of 12
        assert len(data["monthly_energy"]) == 12

        # Check uncertainty structure
        assert "standard_error" in data["uncertainty"]
        assert "confidence_interval_lower" in data["uncertainty"]
        assert "confidence_interval_upper" in data["uncertainty"]

    def test_energy_yield_invalid_location(self, test_client, sample_system_parameters):
        """Test energy yield with invalid location."""
        payload = {
            "location": {
                "latitude": 100,  # Invalid (> 90)
                "longitude": -105
            },
            "system": sample_system_parameters
        }

        response = test_client.post(
            "/api/v1/calculators/energy-yield",
            json=payload
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_energy_yield_missing_required_field(self, test_client, sample_location):
        """Test energy yield with missing required field."""
        payload = {
            "location": sample_location
            # Missing 'system' field
        }

        response = test_client.post(
            "/api/v1/calculators/energy-yield",
            json=payload
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDegradationRateEndpoint:
    """Test Degradation Rate Calculator API endpoint."""

    def test_degradation_rate_calculation(
        self,
        test_client,
        sample_degradation_data
    ):
        """Test degradation rate calculation endpoint."""
        payload = {
            "data_points": sample_degradation_data,
            "system_capacity_kw": 4.0,
            "use_robust_regression": True
        }

        response = test_client.post(
            "/api/v1/calculators/degradation-rate",
            json=payload
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "degradation_rate_per_year" in data
        assert "degradation_rate_percent" in data
        assert "expected_lifetime_years" in data
        assert "uncertainty" in data
        assert "data_quality_score" in data
        assert "outliers_detected" in data
        assert "analysis_period_years" in data
        assert "projected_output_year_25" in data

    def test_degradation_rate_insufficient_data(self, test_client):
        """Test degradation rate with insufficient data points."""
        payload = {
            "data_points": [
                {
                    "timestamp": "2020-01-01T00:00:00",
                    "normalized_output": 1.0
                },
                {
                    "timestamp": "2020-02-01T00:00:00",
                    "normalized_output": 0.99
                }
            ],  # Only 2 points (need 12)
            "system_capacity_kw": 4.0
        }

        response = test_client.post(
            "/api/v1/calculators/degradation-rate",
            json=payload
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_degradation_rate_invalid_normalized_output(self, test_client):
        """Test degradation rate with invalid normalized output."""
        payload = {
            "data_points": [
                {
                    "timestamp": f"2020-{i+1:02d}-01T00:00:00",
                    "normalized_output": 2.0  # Invalid (> 1.5)
                }
                for i in range(12)
            ],
            "system_capacity_kw": 4.0
        }

        response = test_client.post(
            "/api/v1/calculators/degradation-rate",
            json=payload
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSpectralMismatchEndpoint:
    """Test Spectral Mismatch Calculator API endpoint."""

    def test_spectral_mismatch_calculation(
        self,
        test_client,
        sample_spectral_data
    ):
        """Test spectral mismatch calculation endpoint."""
        response = test_client.post(
            "/api/v1/calculators/spectral-mismatch",
            json=sample_spectral_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "mismatch_factor" in data
        assert "corrected_irradiance" in data
        assert "uncorrected_irradiance" in data
        assert "correction_percentage" in data
        assert "uncertainty" in data
        assert "iec_compliant" in data
        assert "wavelength_range" in data
        assert "integration_method" in data

    def test_spectral_mismatch_insufficient_points(self, test_client):
        """Test spectral mismatch with too few data points."""
        payload = {
            "wavelengths": [400, 500, 600],
            "incident_spectrum": [1.0, 1.5, 1.0],
            "reference_spectrum": [1.0, 1.5, 1.0],
            "cell_spectral_response": [0.5, 0.8, 0.5]
        }

        response = test_client.post(
            "/api/v1/calculators/spectral-mismatch",
            json=payload
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_spectral_mismatch_mismatched_lengths(self, test_client):
        """Test spectral mismatch with mismatched array lengths."""
        payload = {
            "wavelengths": list(range(300, 400, 10)),  # 10 points
            "incident_spectrum": [1.0] * 10,
            "reference_spectrum": [1.0] * 10,
            "cell_spectral_response": [0.5] * 5  # Wrong length!
        }

        response = test_client.post(
            "/api/v1/calculators/spectral-mismatch",
            json=payload
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_schema(self, test_client):
        """Test OpenAPI schema is accessible."""
        response = test_client.get("/openapi.json")

        assert response.status_code == status.HTTP_200_OK
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_docs_endpoint(self, test_client):
        """Test Swagger UI docs endpoint."""
        response = test_client.get("/docs")

        assert response.status_code == status.HTTP_200_OK

    def test_redoc_endpoint(self, test_client):
        """Test ReDoc endpoint."""
        response = test_client.get("/redoc")

        assert response.status_code == status.HTTP_200_OK
