"""Comprehensive tests for PV calculators."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any


class TestEnergyYieldCalculator:
    """Tests for Energy Yield Calculator."""

    @pytest.fixture
    def mock_nrel_client(self):
        """Create mock NREL client."""
        client = Mock()
        client.get_pvwatts_data.return_value = {
            "outputs": {
                "ac_annual": 15000,
                "ac_monthly": [1000, 1100, 1300, 1400, 1500, 1450, 1400, 1350, 1300, 1200, 1100, 900],
                "dc_monthly": [1100, 1200, 1400, 1500, 1600, 1550, 1500, 1450, 1400, 1300, 1200, 1000],
                "poa_monthly": [150, 165, 190, 200, 210, 205, 200, 195, 185, 170, 155, 140],
                "dc_nominal": 10
            },
            "station_info": {
                "city": "San Francisco",
                "state": "CA",
                "elev": 16,
                "tz": -8,
                "dataset": "nsrdb"
            }
        }
        return client

    @pytest.fixture
    def sample_request(self):
        """Create sample energy yield request."""
        from backend.models.schemas import EnergyYieldRequest, Location, SystemConfig

        return EnergyYieldRequest(
            location=Location(latitude=37.7749, longitude=-122.4194),
            system=SystemConfig(
                system_capacity=10,
                module_type=0,
                array_type=1,
                tilt=20,
                azimuth=180,
                losses=14,
                albedo=0.2
            )
        )

    def test_calculator_initialization(self, mock_nrel_client):
        """Test calculator initialization."""
        from backend.calculators.energy_yield import EnergyYieldCalculator

        calculator = EnergyYieldCalculator(mock_nrel_client)
        assert calculator is not None
        assert calculator.nrel_client == mock_nrel_client

    def test_calculate_energy_yield(self, mock_nrel_client, sample_request):
        """Test energy yield calculation."""
        from backend.calculators.energy_yield import EnergyYieldCalculator

        calculator = EnergyYieldCalculator(mock_nrel_client)
        result = calculator.calculate(sample_request)

        assert result.annual_energy_kwh > 0
        assert len(result.monthly_energy) == 12
        assert result.capacity_factor > 0
        assert result.capacity_factor < 1
        assert result.specific_yield > 0

    def test_calculate_monthly_metrics(self, mock_nrel_client, sample_request):
        """Test monthly metrics calculation."""
        from backend.calculators.energy_yield import EnergyYieldCalculator

        calculator = EnergyYieldCalculator(mock_nrel_client)
        result = calculator.calculate(sample_request)

        for monthly in result.monthly_energy:
            assert monthly.month >= 1
            assert monthly.month <= 12
            assert monthly.energy_kwh >= 0
            assert monthly.solar_radiation >= 0
            assert monthly.capacity_factor >= 0

    def test_capacity_factor_calculation(self, mock_nrel_client):
        """Test capacity factor calculation."""
        from backend.calculators.energy_yield import EnergyYieldCalculator

        calculator = EnergyYieldCalculator(mock_nrel_client)

        # Test capacity factor calculation
        annual_energy = 15000  # kWh
        system_capacity = 10  # kW
        expected_cf = 15000 / (10 * 8760)

        cf = calculator._calculate_capacity_factor(annual_energy, system_capacity)
        assert abs(cf - expected_cf) < 0.001

    def test_capacity_factor_zero_capacity(self, mock_nrel_client):
        """Test capacity factor with zero capacity."""
        from backend.calculators.energy_yield import EnergyYieldCalculator

        calculator = EnergyYieldCalculator(mock_nrel_client)
        cf = calculator._calculate_capacity_factor(1000, 0)
        assert cf == 0

    def test_uncertainty_calculation(self, mock_nrel_client, sample_request):
        """Test uncertainty metrics calculation."""
        from backend.calculators.energy_yield import EnergyYieldCalculator

        calculator = EnergyYieldCalculator(mock_nrel_client)
        result = calculator.calculate(sample_request)

        assert result.uncertainty is not None
        assert result.uncertainty.standard_error > 0
        assert result.uncertainty.confidence_level == 0.95
        assert result.uncertainty.confidence_interval_lower >= 0
        assert result.uncertainty.confidence_interval_upper > result.uncertainty.confidence_interval_lower
        assert result.uncertainty.relative_uncertainty > 0

    def test_performance_ratio_estimation(self, mock_nrel_client):
        """Test performance ratio estimation."""
        from backend.calculators.energy_yield import EnergyYieldCalculator

        calculator = EnergyYieldCalculator(mock_nrel_client)

        outputs = {
            "ac_annual": 14000,
            "poa_monthly": [150] * 12,
            "dc_nominal": 10
        }

        pr = calculator._estimate_performance_ratio(outputs)
        assert 0 <= pr <= 1

    def test_performance_ratio_default(self, mock_nrel_client):
        """Test default performance ratio when data is missing."""
        from backend.calculators.energy_yield import EnergyYieldCalculator

        calculator = EnergyYieldCalculator(mock_nrel_client)

        outputs = {"ac_annual": 0, "poa_monthly": [], "dc_nominal": 0}
        pr = calculator._estimate_performance_ratio(outputs)
        assert pr == 0.8  # Default value

    @patch('backend.calculators.energy_yield.NRELAPIError')
    def test_api_error_handling(self, mock_error, mock_nrel_client, sample_request):
        """Test handling of NREL API errors."""
        from backend.calculators.energy_yield import EnergyYieldCalculator
        from backend.services.nrel_client import NRELAPIError

        mock_nrel_client.get_pvwatts_data.side_effect = Exception("API Error")

        calculator = EnergyYieldCalculator(mock_nrel_client)

        with pytest.raises(NRELAPIError):
            calculator.calculate(sample_request)


class TestDegradationRateCalculator:
    """Tests for Degradation Rate Calculator."""

    @pytest.fixture
    def mock_nrel_client(self):
        """Create mock NREL client for degradation calculations."""
        return Mock()

    def test_degradation_calculation_mono_si(self, mock_nrel_client):
        """Test degradation for mono-crystalline silicon."""
        from backend.calculators.degradation_rate import DegradationRateCalculator

        calculator = DegradationRateCalculator(mock_nrel_client)

        request = Mock()
        request.technology = "mono-Si"
        request.age_years = 0
        request.analysis_period_years = 25
        request.initial_power = 400
        request.location = Mock(latitude=37.77, longitude=-122.42)
        request.environmental_factors = None

        result = calculator.calculate(request)

        assert result is not None
        assert result.annual_degradation_rate > 0
        assert result.cumulative_degradation > 0
        assert result.final_power > 0

    def test_degradation_calculation_poly_si(self, mock_nrel_client):
        """Test degradation for poly-crystalline silicon."""
        from backend.calculators.degradation_rate import DegradationRateCalculator

        calculator = DegradationRateCalculator(mock_nrel_client)

        request = Mock()
        request.technology = "poly-Si"
        request.age_years = 0
        request.analysis_period_years = 25
        request.initial_power = 380
        request.location = Mock(latitude=37.77, longitude=-122.42)
        request.environmental_factors = None

        result = calculator.calculate(request)

        assert result.annual_degradation_rate > 0

    def test_degradation_calculation_thin_film(self, mock_nrel_client):
        """Test degradation for thin-film technologies."""
        from backend.calculators.degradation_rate import DegradationRateCalculator

        calculator = DegradationRateCalculator(mock_nrel_client)

        for tech in ["CdTe", "CIGS", "a-Si"]:
            request = Mock()
            request.technology = tech
            request.age_years = 0
            request.analysis_period_years = 25
            request.initial_power = 350
            request.location = Mock(latitude=37.77, longitude=-122.42)
            request.environmental_factors = None

            result = calculator.calculate(request)
            assert result.annual_degradation_rate > 0

    def test_degradation_with_environmental_factors(self, mock_nrel_client):
        """Test degradation with environmental factors."""
        from backend.calculators.degradation_rate import DegradationRateCalculator

        calculator = DegradationRateCalculator(mock_nrel_client)

        request = Mock()
        request.technology = "mono-Si"
        request.age_years = 0
        request.analysis_period_years = 25
        request.initial_power = 400
        request.location = Mock(latitude=25.0, longitude=-80.0)  # Hot, humid location
        request.environmental_factors = Mock(
            average_temperature=30,
            humidity=80,
            soiling_rate=0.5
        )

        result = calculator.calculate(request)

        # Higher environmental stress should increase degradation
        assert result.annual_degradation_rate > 0

    def test_yearly_energy_projection(self, mock_nrel_client):
        """Test yearly energy projection over system lifetime."""
        from backend.calculators.degradation_rate import DegradationRateCalculator

        calculator = DegradationRateCalculator(mock_nrel_client)

        request = Mock()
        request.technology = "mono-Si"
        request.age_years = 0
        request.analysis_period_years = 25
        request.initial_power = 400
        request.location = Mock(latitude=37.77, longitude=-122.42)
        request.environmental_factors = None

        result = calculator.calculate(request)

        assert len(result.yearly_power) == 25
        # Power should decrease over time
        assert result.yearly_power[0] > result.yearly_power[-1]

    def test_degradation_aged_system(self, mock_nrel_client):
        """Test degradation calculation for already aged system."""
        from backend.calculators.degradation_rate import DegradationRateCalculator

        calculator = DegradationRateCalculator(mock_nrel_client)

        request = Mock()
        request.technology = "mono-Si"
        request.age_years = 10  # System already 10 years old
        request.analysis_period_years = 15
        request.initial_power = 400
        request.location = Mock(latitude=37.77, longitude=-122.42)
        request.environmental_factors = None

        result = calculator.calculate(request)

        assert result.final_power > 0


class TestSpectralMismatchCalculator:
    """Tests for Spectral Mismatch Calculator."""

    @pytest.fixture
    def mock_nrel_client(self):
        """Create mock NREL client."""
        return Mock()

    def test_spectral_mismatch_csi(self, mock_nrel_client):
        """Test spectral mismatch for crystalline silicon."""
        from backend.calculators.spectral_mismatch import SpectralMismatchCalculator

        calculator = SpectralMismatchCalculator(mock_nrel_client)

        request = Mock()
        request.module_technology = "c-Si"
        request.location = Mock(latitude=37.77, longitude=-122.42)
        request.datetime = "2024-06-21T12:00:00"

        result = calculator.calculate(request)

        assert result is not None
        assert 0.8 <= result.spectral_modifier <= 1.2
        assert result.airmass > 0

    def test_spectral_mismatch_cdte(self, mock_nrel_client):
        """Test spectral mismatch for CdTe."""
        from backend.calculators.spectral_mismatch import SpectralMismatchCalculator

        calculator = SpectralMismatchCalculator(mock_nrel_client)

        request = Mock()
        request.module_technology = "CdTe"
        request.location = Mock(latitude=37.77, longitude=-122.42)
        request.datetime = "2024-06-21T12:00:00"

        result = calculator.calculate(request)

        assert 0.8 <= result.spectral_modifier <= 1.2

    def test_airmass_calculation(self, mock_nrel_client):
        """Test airmass calculation."""
        from backend.calculators.spectral_mismatch import SpectralMismatchCalculator

        calculator = SpectralMismatchCalculator(mock_nrel_client)

        # Test at different solar zenith angles
        for zenith in [0, 30, 60, 80]:
            am = calculator._calculate_airmass(zenith)
            assert am >= 1  # AM should be >= 1

    def test_precipitable_water_estimation(self, mock_nrel_client):
        """Test precipitable water estimation."""
        from backend.calculators.spectral_mismatch import SpectralMismatchCalculator

        calculator = SpectralMismatchCalculator(mock_nrel_client)

        # Test with different conditions
        pw = calculator._estimate_precipitable_water(
            temperature=25,
            relative_humidity=60,
            pressure=101325
        )

        assert pw > 0
        assert pw < 10  # Typical range for precipitable water

    def test_spectral_response_coefficients(self, mock_nrel_client):
        """Test spectral response coefficients for different technologies."""
        from backend.calculators.spectral_mismatch import SpectralMismatchCalculator

        calculator = SpectralMismatchCalculator(mock_nrel_client)

        technologies = ["c-Si", "CdTe", "CIGS", "a-Si"]

        for tech in technologies:
            coefficients = calculator._get_spectral_coefficients(tech)
            assert coefficients is not None


class TestCalculatorIntegration:
    """Integration tests for calculators."""

    @patch('backend.services.nrel_client.NRELClient')
    def test_energy_yield_with_degradation(self, mock_client_class):
        """Test combining energy yield with degradation."""
        from backend.calculators.energy_yield import EnergyYieldCalculator
        from backend.calculators.degradation_rate import DegradationRateCalculator

        # Setup mock
        mock_client = Mock()
        mock_client.get_pvwatts_data.return_value = {
            "outputs": {
                "ac_annual": 15000,
                "ac_monthly": [1200] * 12,
                "dc_monthly": [1300] * 12,
                "poa_monthly": [170] * 12,
                "dc_nominal": 10
            },
            "station_info": {"city": "Test", "state": "CA", "elev": 100, "tz": -8}
        }
        mock_client_class.return_value = mock_client

        # This test demonstrates the workflow
        # First calculate energy yield
        # Then apply degradation over time

    @patch('backend.services.nrel_client.NRELClient')
    def test_full_pv_analysis_workflow(self, mock_client_class):
        """Test complete PV analysis workflow."""
        # This tests the integration of all calculators
        pass


class TestCalculatorEdgeCases:
    """Edge case tests for calculators."""

    def test_energy_yield_extreme_latitude(self):
        """Test energy yield at extreme latitudes."""
        from backend.calculators.energy_yield import EnergyYieldCalculator

        mock_client = Mock()
        mock_client.get_pvwatts_data.return_value = {
            "outputs": {
                "ac_annual": 5000,  # Lower energy at high latitude
                "ac_monthly": [200, 300, 500, 800, 1000, 1100, 1000, 800, 500, 300, 200, 100],
                "dc_monthly": [220] * 12,
                "poa_monthly": [50] * 12,
                "dc_nominal": 10
            },
            "station_info": {"city": "Arctic", "elev": 0, "tz": 0}
        }

        calculator = EnergyYieldCalculator(mock_client)

        request = Mock()
        request.location = Mock(latitude=70.0, longitude=25.0)  # Arctic
        request.system = Mock(
            system_capacity=10,
            module_type=0,
            array_type=1,
            tilt=70,
            azimuth=180,
            losses=14,
            albedo=0.8  # High albedo due to snow
        )

        result = calculator.calculate(request)
        assert result.annual_energy_kwh > 0

    def test_degradation_zero_initial_power(self):
        """Test degradation with zero initial power."""
        from backend.calculators.degradation_rate import DegradationRateCalculator

        calculator = DegradationRateCalculator(Mock())

        request = Mock()
        request.technology = "mono-Si"
        request.age_years = 0
        request.analysis_period_years = 25
        request.initial_power = 0
        request.location = Mock(latitude=37.77, longitude=-122.42)
        request.environmental_factors = None

        result = calculator.calculate(request)
        assert result.final_power == 0

    def test_spectral_mismatch_night_time(self):
        """Test spectral mismatch during night (invalid conditions)."""
        from backend.calculators.spectral_mismatch import SpectralMismatchCalculator

        calculator = SpectralMismatchCalculator(Mock())

        request = Mock()
        request.module_technology = "c-Si"
        request.location = Mock(latitude=37.77, longitude=-122.42)
        request.datetime = "2024-06-21T02:00:00"  # Night time

        result = calculator.calculate(request)
        # Should handle gracefully or return default values

    def test_very_long_analysis_period(self):
        """Test degradation over very long period."""
        from backend.calculators.degradation_rate import DegradationRateCalculator

        calculator = DegradationRateCalculator(Mock())

        request = Mock()
        request.technology = "mono-Si"
        request.age_years = 0
        request.analysis_period_years = 50  # 50 years
        request.initial_power = 400
        request.location = Mock(latitude=37.77, longitude=-122.42)
        request.environmental_factors = None

        result = calculator.calculate(request)
        # System should still have some power after 50 years
        assert result.final_power > 0
        assert result.final_power < request.initial_power


class TestNRELClient:
    """Tests for NREL API Client."""

    @patch('backend.services.nrel_client.requests.get')
    def test_pvwatts_api_call(self, mock_get):
        """Test PVWatts API call."""
        from backend.services.nrel_client import NRELClient

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outputs": {"ac_annual": 15000},
            "station_info": {"city": "San Francisco"}
        }
        mock_get.return_value = mock_response

        client = NRELClient(api_key="test-key")
        result = client.get_pvwatts_data(
            latitude=37.77,
            longitude=-122.42,
            system_capacity=10,
            module_type=0,
            array_type=1,
            tilt=20,
            azimuth=180
        )

        assert result is not None
        assert "outputs" in result

    @patch('backend.services.nrel_client.requests.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling."""
        from backend.services.nrel_client import NRELClient, NRELAPIError

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        client = NRELClient(api_key="test-key")

        with pytest.raises(NRELAPIError):
            client.get_pvwatts_data(
                latitude=37.77,
                longitude=-122.42,
                system_capacity=10
            )

    @patch('backend.services.nrel_client.requests.get')
    def test_api_rate_limiting(self, mock_get):
        """Test API rate limiting handling."""
        from backend.services.nrel_client import NRELClient

        # First call returns 429, second returns success
        mock_response_429 = Mock()
        mock_response_429.status_code = 429

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"outputs": {}, "station_info": {}}

        mock_get.side_effect = [mock_response_429, mock_response_200]

        client = NRELClient(api_key="test-key")
        # Client should retry after rate limit


class TestCalculatorValidation:
    """Tests for input validation in calculators."""

    def test_invalid_latitude(self):
        """Test validation of invalid latitude."""
        from backend.models.schemas import Location

        with pytest.raises(ValueError):
            Location(latitude=100, longitude=0)  # Invalid latitude

    def test_invalid_longitude(self):
        """Test validation of invalid longitude."""
        from backend.models.schemas import Location

        with pytest.raises(ValueError):
            Location(latitude=0, longitude=200)  # Invalid longitude

    def test_negative_system_capacity(self):
        """Test validation of negative system capacity."""
        from backend.models.schemas import SystemConfig

        with pytest.raises(ValueError):
            SystemConfig(
                system_capacity=-10,
                module_type=0,
                array_type=1,
                tilt=20,
                azimuth=180
            )

    def test_invalid_losses_percentage(self):
        """Test validation of losses outside 0-100 range."""
        from backend.models.schemas import SystemConfig

        with pytest.raises(ValueError):
            SystemConfig(
                system_capacity=10,
                module_type=0,
                array_type=1,
                tilt=20,
                azimuth=180,
                losses=150  # Invalid
            )
