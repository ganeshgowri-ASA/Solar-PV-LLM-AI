"""
Unit tests for Energy Yield Calculator.
"""
import pytest
from unittest.mock import Mock, patch
from backend.calculators.energy_yield import EnergyYieldCalculator
from backend.models.schemas import EnergyYieldRequest, LocationInput, SystemParameters
from backend.services.nrel_client import NRELAPIError


class TestEnergyYieldCalculator:
    """Test suite for Energy Yield Calculator."""

    def test_calculate_energy_yield_success(
        self,
        sample_location,
        sample_system_parameters,
        mock_pvwatts_response
    ):
        """Test successful energy yield calculation."""
        # Create request
        request = EnergyYieldRequest(
            location=LocationInput(**sample_location),
            system=SystemParameters(**sample_system_parameters)
        )

        # Mock NREL client
        mock_client = Mock()
        mock_client.get_pvwatts_data.return_value = mock_pvwatts_response

        # Calculate
        calculator = EnergyYieldCalculator(mock_client)
        result = calculator.calculate(request)

        # Assertions
        assert result.annual_energy_kwh > 0
        assert len(result.monthly_energy) == 12
        assert 0 <= result.capacity_factor <= 1
        assert result.specific_yield > 0
        assert 0 <= result.performance_ratio <= 1

        # Check uncertainty metrics
        assert result.uncertainty.standard_error > 0
        assert result.uncertainty.confidence_level == 0.95
        assert result.uncertainty.confidence_interval_lower < result.annual_energy_kwh
        assert result.uncertainty.confidence_interval_upper > result.annual_energy_kwh

        # Verify NREL client was called correctly
        mock_client.get_pvwatts_data.assert_called_once()

    def test_calculate_monthly_metrics(
        self,
        sample_location,
        sample_system_parameters,
        mock_pvwatts_response
    ):
        """Test monthly metrics calculation."""
        request = EnergyYieldRequest(
            location=LocationInput(**sample_location),
            system=SystemParameters(**sample_system_parameters)
        )

        mock_client = Mock()
        mock_client.get_pvwatts_data.return_value = mock_pvwatts_response

        calculator = EnergyYieldCalculator(mock_client)
        result = calculator.calculate(request)

        # Check each month
        for i, month_data in enumerate(result.monthly_energy, 1):
            assert month_data.month == i
            assert month_data.energy_kwh > 0
            assert month_data.solar_radiation > 0
            assert 0 <= month_data.capacity_factor <= 1

        # Summer months should have higher production
        summer_months = [result.monthly_energy[i] for i in [5, 6, 7]]  # Jun, Jul, Aug
        winter_months = [result.monthly_energy[i] for i in [0, 1, 11]]  # Jan, Feb, Dec

        avg_summer = sum(m.energy_kwh for m in summer_months) / 3
        avg_winter = sum(m.energy_kwh for m in winter_months) / 3

        assert avg_summer > avg_winter

    def test_capacity_factor_calculation(
        self,
        sample_location,
        sample_system_parameters,
        mock_pvwatts_response
    ):
        """Test capacity factor calculation."""
        request = EnergyYieldRequest(
            location=LocationInput(**sample_location),
            system=SystemParameters(**sample_system_parameters)
        )

        mock_client = Mock()
        mock_client.get_pvwatts_data.return_value = mock_pvwatts_response

        calculator = EnergyYieldCalculator(mock_client)
        result = calculator.calculate(request)

        # Manual calculation
        annual_energy = result.annual_energy_kwh
        capacity = sample_system_parameters["system_capacity"]
        hours_per_year = 8760
        expected_cf = annual_energy / (capacity * hours_per_year)

        assert abs(result.capacity_factor - expected_cf) < 0.001

    def test_uncertainty_quantification(
        self,
        sample_location,
        sample_system_parameters,
        mock_pvwatts_response
    ):
        """Test uncertainty metrics calculation."""
        request = EnergyYieldRequest(
            location=LocationInput(**sample_location),
            system=SystemParameters(**sample_system_parameters)
        )

        mock_client = Mock()
        mock_client.get_pvwatts_data.return_value = mock_pvwatts_response

        calculator = EnergyYieldCalculator(mock_client)
        result = calculator.calculate(request)

        # Check uncertainty is reasonable (typically 5-15% for PVWatts)
        relative_uncertainty = (
            result.uncertainty.standard_error / result.annual_energy_kwh * 100
        )
        assert 5 <= relative_uncertainty <= 20

        # Check confidence interval width
        ci_width = (
            result.uncertainty.confidence_interval_upper -
            result.uncertainty.confidence_interval_lower
        )
        assert ci_width > 0
        assert ci_width < result.annual_energy_kwh * 0.5  # Less than 50% of estimate

    def test_nrel_api_error_handling(self, sample_location, sample_system_parameters):
        """Test error handling for NREL API failures."""
        request = EnergyYieldRequest(
            location=LocationInput(**sample_location),
            system=SystemParameters(**sample_system_parameters)
        )

        mock_client = Mock()
        mock_client.get_pvwatts_data.side_effect = NRELAPIError("API error")

        calculator = EnergyYieldCalculator(mock_client)

        with pytest.raises(NRELAPIError):
            calculator.calculate(request)

    def test_metadata_population(
        self,
        sample_location,
        sample_system_parameters,
        mock_pvwatts_response
    ):
        """Test that metadata is properly populated."""
        request = EnergyYieldRequest(
            location=LocationInput(**sample_location),
            system=SystemParameters(**sample_system_parameters)
        )

        mock_client = Mock()
        mock_client.get_pvwatts_data.return_value = mock_pvwatts_response

        calculator = EnergyYieldCalculator(mock_client)
        result = calculator.calculate(request)

        # Check metadata structure
        assert "location" in result.metadata
        assert "system" in result.metadata
        assert "data_source" in result.metadata

        # Check location metadata
        assert result.metadata["location"]["latitude"] == sample_location["latitude"]
        assert result.metadata["location"]["longitude"] == sample_location["longitude"]

        # Check system metadata
        assert result.metadata["system"]["capacity_kw"] == sample_system_parameters["system_capacity"]
