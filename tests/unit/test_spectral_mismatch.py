"""
Unit tests for Spectral Mismatch Calculator.
"""
import pytest
import numpy as np
from backend.calculators.spectral_mismatch import SpectralMismatchCalculator
from backend.models.schemas import SpectralMismatchRequest


class TestSpectralMismatchCalculator:
    """Test suite for Spectral Mismatch Calculator."""

    def test_calculate_spectral_mismatch_success(self, sample_spectral_data):
        """Test successful spectral mismatch calculation."""
        request = SpectralMismatchRequest(**sample_spectral_data)

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        # Assertions
        assert result.mismatch_factor > 0
        assert result.corrected_irradiance > 0
        assert result.uncorrected_irradiance > 0
        assert result.uncertainty.standard_error > 0
        assert result.iec_compliant is not None
        assert len(result.wavelength_range) == 2
        assert result.wavelength_range[0] < result.wavelength_range[1]

    def test_identical_spectra_gives_unity_mismatch(self):
        """Test that identical test and reference spectra give M=1."""
        # Create identical spectra
        wavelengths = np.linspace(300, 1200, 100).tolist()
        spectrum = np.ones(100).tolist()
        cell_response = np.ones(100).tolist()

        request = SpectralMismatchRequest(
            wavelengths=wavelengths,
            incident_spectrum=spectrum,
            reference_spectrum=spectrum,  # Same as incident
            cell_spectral_response=cell_response
        )

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        # Mismatch factor should be very close to 1.0
        assert abs(result.mismatch_factor - 1.0) < 0.01

    def test_correction_percentage_calculation(self, sample_spectral_data):
        """Test correction percentage calculation."""
        request = SpectralMismatchRequest(**sample_spectral_data)

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        # Correction percentage should match (M - 1) * 100
        expected_correction = (result.mismatch_factor - 1.0) * 100
        assert abs(result.correction_percentage - expected_correction) < 0.01

    def test_corrected_irradiance_calculation(self, sample_spectral_data):
        """Test that corrected irradiance = uncorrected * M."""
        request = SpectralMismatchRequest(**sample_spectral_data)

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        expected_corrected = result.uncorrected_irradiance * result.mismatch_factor
        assert abs(result.corrected_irradiance - expected_corrected) < 0.01

    def test_minimum_data_points_validation(self):
        """Test validation of minimum data points."""
        # Too few points
        wavelengths = [400, 500, 600]
        spectrum = [1.0, 1.5, 1.0]
        response = [0.5, 0.8, 0.6]

        request = SpectralMismatchRequest(
            wavelengths=wavelengths,
            incident_spectrum=spectrum,
            reference_spectrum=spectrum,
            cell_spectral_response=response
        )

        calculator = SpectralMismatchCalculator()

        with pytest.raises(ValueError, match="Insufficient spectral data"):
            calculator.calculate(request)

    def test_array_length_validation(self):
        """Test that all arrays must have same length."""
        wavelengths = np.linspace(300, 1200, 100).tolist()
        spectrum = np.ones(100).tolist()
        response = np.ones(50).tolist()  # Wrong length!

        with pytest.raises(ValueError):
            SpectralMismatchRequest(
                wavelengths=wavelengths,
                incident_spectrum=spectrum,
                reference_spectrum=spectrum,
                cell_spectral_response=response
            )

    def test_negative_wavelength_validation(self):
        """Test that negative wavelengths are rejected."""
        wavelengths = [-100, 400, 500]  # Negative wavelength
        spectrum = [1.0, 1.5, 1.0]
        response = [0.5, 0.8, 0.6]

        # Extend to meet minimum length
        wavelengths.extend(range(600, 1200, 60))
        spectrum.extend([1.0] * 10)
        response.extend([0.5] * 10)

        request = SpectralMismatchRequest(
            wavelengths=wavelengths,
            incident_spectrum=spectrum,
            reference_spectrum=spectrum,
            cell_spectral_response=response
        )

        calculator = SpectralMismatchCalculator()

        with pytest.raises(ValueError, match="Wavelengths must be positive"):
            calculator.calculate(request)

    def test_wavelength_ordering_validation(self):
        """Test that wavelengths must be sorted."""
        wavelengths = [1200, 400, 800, 600]  # Not sorted
        spectrum = [1.0, 1.5, 1.2, 1.0]
        response = [0.5, 0.8, 0.7, 0.6]

        # Extend to meet minimum length
        wavelengths.extend(range(300, 360, 10))
        spectrum.extend([1.0] * 6)
        response.extend([0.5] * 6)

        request = SpectralMismatchRequest(
            wavelengths=wavelengths,
            incident_spectrum=spectrum,
            reference_spectrum=spectrum,
            cell_spectral_response=response
        )

        calculator = SpectralMismatchCalculator()

        with pytest.raises(ValueError, match="ascending order"):
            calculator.calculate(request)

    def test_iec_compliance_check(self, sample_spectral_data):
        """Test IEC 60904-7 compliance checking."""
        # Good spectral data should be compliant
        request = SpectralMismatchRequest(**sample_spectral_data)

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        # Sample data covers 300-1200 nm, should be compliant
        assert result.iec_compliant is True

    def test_iec_compliance_narrow_range(self):
        """Test IEC compliance with narrow wavelength range."""
        # Narrow range (only 500-700 nm) - not compliant
        wavelengths = np.linspace(500, 700, 50).tolist()
        spectrum = np.ones(50).tolist()
        response = np.ones(50).tolist()

        request = SpectralMismatchRequest(
            wavelengths=wavelengths,
            incident_spectrum=spectrum,
            reference_spectrum=spectrum,
            cell_spectral_response=response
        )

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        # Should not be IEC compliant (doesn't cover 350-1100 nm)
        assert result.iec_compliant is False

    def test_uncertainty_quantification(self, sample_spectral_data):
        """Test uncertainty calculation."""
        request = SpectralMismatchRequest(**sample_spectral_data)

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        # Check uncertainty metrics
        assert result.uncertainty.standard_error > 0
        assert result.uncertainty.confidence_level == 0.95
        assert result.uncertainty.confidence_interval_lower < result.mismatch_factor
        assert result.uncertainty.confidence_interval_upper > result.mismatch_factor

        # Relative uncertainty should be reasonable (typically 2-5% for spectral mismatch)
        assert result.uncertainty.relative_uncertainty < 10

    def test_reference_cell_response_optional(self, sample_spectral_data):
        """Test that reference cell response is optional."""
        # Don't provide reference cell response
        data = sample_spectral_data.copy()
        data.pop('reference_cell_response', None)

        request = SpectralMismatchRequest(**data)

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        # Should still work (uses test cell response as reference)
        assert result.mismatch_factor > 0

    def test_silicon_cell_typical_mismatch(self):
        """Test with typical silicon cell scenario."""
        # Wavelengths from 300 to 1200 nm
        wavelengths = np.linspace(300, 1200, 200)

        # AM1.5G reference spectrum (simplified)
        reference_spectrum = np.exp(-((wavelengths - 500) / 300) ** 2) * 1.5

        # Cloudy sky spectrum (more blue light)
        incident_spectrum = np.exp(-((wavelengths - 450) / 250) ** 2) * 1.5

        # Silicon spectral response (peak ~900 nm)
        cell_response = np.exp(-((wavelengths - 900) / 200) ** 2) * 0.8

        request = SpectralMismatchRequest(
            wavelengths=wavelengths.tolist(),
            incident_spectrum=incident_spectrum.tolist(),
            reference_spectrum=reference_spectrum.tolist(),
            cell_spectral_response=cell_response.tolist()
        )

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        # For silicon cells, mismatch is typically between 0.9 and 1.1
        assert 0.8 < result.mismatch_factor < 1.2

    def test_integration_method_reported(self, sample_spectral_data):
        """Test that integration method is reported."""
        request = SpectralMismatchRequest(**sample_spectral_data)

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        assert result.integration_method == "trapezoidal"

    def test_wavelength_range_reported(self, sample_spectral_data):
        """Test that wavelength range is correctly reported."""
        request = SpectralMismatchRequest(**sample_spectral_data)

        calculator = SpectralMismatchCalculator()
        result = calculator.calculate(request)

        wavelengths = sample_spectral_data["wavelengths"]
        assert result.wavelength_range[0] == min(wavelengths)
        assert result.wavelength_range[1] == max(wavelengths)
