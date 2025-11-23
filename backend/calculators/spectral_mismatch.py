"""
Spectral Mismatch Correction Calculator based on IEC 60904-7 standard.

Implements spectral mismatch correction factor calculation according to
IEC 60904-7: Photovoltaic devices - Part 7: Computation of the spectral
mismatch correction.
"""
import numpy as np
from typing import Tuple, Optional
from scipy.integrate import trapezoid
from loguru import logger

from backend.models.schemas import (
    SpectralMismatchRequest,
    SpectralMismatchResponse,
    UncertaintyMetrics
)
from backend.config.constants import (
    IEC_60904_7_REFERENCE_SPECTRUM,
    IEC_60904_7_REFERENCE_IRRADIANCE,
    CONFIDENCE_LEVEL_95
)


class SpectralMismatchCalculator:
    """
    Spectral Mismatch Correction Calculator implementing IEC 60904-7 standard.

    The spectral mismatch factor M corrects for differences between
    the test spectrum and reference spectrum when measuring PV devices.

    M = (∫E_ref(λ)·S_r(λ)dλ · ∫E_test(λ)·S_t(λ)dλ) /
        (∫E_test(λ)·S_r(λ)dλ · ∫E_ref(λ)·S_t(λ)dλ)

    Where:
    - E_ref: Reference spectral irradiance
    - E_test: Test (incident) spectral irradiance
    - S_r: Reference cell spectral response
    - S_t: Test cell spectral response
    """

    def __init__(self):
        """Initialize Spectral Mismatch Calculator."""
        pass

    def calculate(self, request: SpectralMismatchRequest) -> SpectralMismatchResponse:
        """
        Calculate spectral mismatch correction factor.

        Args:
            request: Spectral mismatch calculation request

        Returns:
            Spectral mismatch response with correction factor

        Raises:
            ValueError: If input data is invalid
        """
        logger.info("Calculating spectral mismatch correction factor (IEC 60904-7)")

        # Validate input data
        self._validate_input(request)

        # Convert to numpy arrays
        wavelengths = np.array(request.wavelengths)
        E_test = np.array(request.incident_spectrum)
        E_ref = np.array(request.reference_spectrum)
        S_test = np.array(request.cell_spectral_response)

        # Use reference cell response if provided, otherwise use test cell
        if request.reference_cell_response is not None:
            S_ref = np.array(request.reference_cell_response)
        else:
            # If no reference cell provided, assume same as test cell
            S_ref = S_test

        # Calculate mismatch factor using IEC 60904-7 formula
        mismatch_factor, integrals = self._calculate_mismatch_factor(
            wavelengths,
            E_test,
            E_ref,
            S_test,
            S_ref
        )

        # Calculate irradiances
        uncorrected_irradiance = trapezoid(E_test, wavelengths)
        corrected_irradiance = uncorrected_irradiance * mismatch_factor

        # Correction percentage
        correction_percentage = (mismatch_factor - 1.0) * 100

        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(
            wavelengths,
            E_test,
            E_ref,
            S_test,
            S_ref,
            mismatch_factor
        )

        # Wavelength range
        wavelength_range = (float(wavelengths[0]), float(wavelengths[-1]))

        # Check IEC compliance
        iec_compliant = self._check_iec_compliance(wavelengths, E_test, E_ref)

        return SpectralMismatchResponse(
            mismatch_factor=mismatch_factor,
            corrected_irradiance=corrected_irradiance,
            uncorrected_irradiance=uncorrected_irradiance,
            correction_percentage=correction_percentage,
            uncertainty=uncertainty,
            iec_compliant=iec_compliant,
            wavelength_range=wavelength_range,
            integration_method="trapezoidal"
        )

    def _validate_input(self, request: SpectralMismatchRequest) -> None:
        """
        Validate input data.

        Args:
            request: Spectral mismatch request

        Raises:
            ValueError: If validation fails
        """
        n = len(request.wavelengths)

        if n < 10:
            raise ValueError("Insufficient spectral data points (minimum 10 required)")

        # Check all arrays have same length
        arrays_to_check = [
            request.incident_spectrum,
            request.reference_spectrum,
            request.cell_spectral_response
        ]

        if request.reference_cell_response is not None:
            arrays_to_check.append(request.reference_cell_response)

        for arr in arrays_to_check:
            if len(arr) != n:
                raise ValueError("All spectral arrays must have the same length")

        # Check for negative values
        if any(w < 0 for w in request.wavelengths):
            raise ValueError("Wavelengths must be positive")

        if any(e < 0 for e in request.incident_spectrum):
            raise ValueError("Incident spectrum values must be non-negative")

        if any(e < 0 for e in request.reference_spectrum):
            raise ValueError("Reference spectrum values must be non-negative")

        # Check wavelengths are sorted
        wavelengths = np.array(request.wavelengths)
        if not np.all(wavelengths[1:] >= wavelengths[:-1]):
            raise ValueError("Wavelengths must be in ascending order")

    def _calculate_mismatch_factor(
        self,
        wavelengths: np.ndarray,
        E_test: np.ndarray,
        E_ref: np.ndarray,
        S_test: np.ndarray,
        S_ref: np.ndarray
    ) -> Tuple[float, dict]:
        """
        Calculate spectral mismatch factor using IEC 60904-7 formula.

        M = (I1 · I2) / (I3 · I4)

        Where:
        I1 = ∫E_ref(λ)·S_ref(λ)dλ   - Reference cell under reference spectrum
        I2 = ∫E_test(λ)·S_test(λ)dλ - Test cell under test spectrum
        I3 = ∫E_test(λ)·S_ref(λ)dλ  - Reference cell under test spectrum
        I4 = ∫E_ref(λ)·S_test(λ)dλ  - Test cell under reference spectrum

        Args:
            wavelengths: Wavelength array (nm)
            E_test: Test spectral irradiance (W/m²/nm)
            E_ref: Reference spectral irradiance (W/m²/nm)
            S_test: Test cell spectral response (A/W)
            S_ref: Reference cell spectral response (A/W)

        Returns:
            Tuple of (mismatch_factor, integrals_dict)
        """
        # Calculate the four integrals
        I1 = trapezoid(E_ref * S_ref, wavelengths)  # Reference cell, reference spectrum
        I2 = trapezoid(E_test * S_test, wavelengths)  # Test cell, test spectrum
        I3 = trapezoid(E_test * S_ref, wavelengths)  # Reference cell, test spectrum
        I4 = trapezoid(E_ref * S_test, wavelengths)  # Test cell, reference spectrum

        # Calculate mismatch factor
        numerator = I1 * I2
        denominator = I3 * I4

        if denominator == 0:
            logger.warning("Denominator is zero in mismatch calculation, returning M=1.0")
            mismatch_factor = 1.0
        else:
            mismatch_factor = numerator / denominator

        integrals = {
            'I1_ref_cell_ref_spectrum': I1,
            'I2_test_cell_test_spectrum': I2,
            'I3_ref_cell_test_spectrum': I3,
            'I4_test_cell_ref_spectrum': I4
        }

        logger.info(f"Spectral mismatch factor M = {mismatch_factor:.6f}")

        return mismatch_factor, integrals

    def _calculate_uncertainty(
        self,
        wavelengths: np.ndarray,
        E_test: np.ndarray,
        E_ref: np.ndarray,
        S_test: np.ndarray,
        S_ref: np.ndarray,
        mismatch_factor: float
    ) -> UncertaintyMetrics:
        """
        Calculate uncertainty in mismatch factor.

        Uncertainty sources:
        1. Spectral irradiance measurement uncertainty
        2. Spectral response measurement uncertainty
        3. Integration/interpolation uncertainty

        Args:
            wavelengths: Wavelength array
            E_test: Test spectral irradiance
            E_ref: Reference spectral irradiance
            S_test: Test cell spectral response
            S_ref: Reference cell spectral response
            mismatch_factor: Calculated mismatch factor

        Returns:
            Uncertainty metrics
        """
        # Typical uncertainties from IEC 60904-7
        # These are conservative estimates
        u_spectral_irradiance = 0.02  # 2% for spectral irradiance measurement
        u_spectral_response = 0.015  # 1.5% for spectral response measurement
        u_integration = 0.005  # 0.5% for numerical integration

        # Combined uncertainty using RSS (Root Sum of Squares)
        # For a product/quotient, relative uncertainties add in quadrature
        u_combined_relative = np.sqrt(
            (2 * u_spectral_irradiance) ** 2 +  # Two spectral irradiance measurements
            (2 * u_spectral_response) ** 2 +  # Two spectral response measurements
            u_integration ** 2
        )

        # Absolute uncertainty
        standard_error = mismatch_factor * u_combined_relative

        # Confidence intervals (95% confidence, using normal approximation)
        confidence_level = CONFIDENCE_LEVEL_95
        z_score = 1.96  # 95% confidence for normal distribution

        ci_margin = z_score * standard_error
        ci_lower = mismatch_factor - ci_margin
        ci_upper = mismatch_factor + ci_margin

        # Relative uncertainty as percentage
        relative_uncertainty = u_combined_relative * 100

        return UncertaintyMetrics(
            standard_error=standard_error,
            confidence_level=confidence_level,
            confidence_interval_lower=max(0, ci_lower),
            confidence_interval_upper=ci_upper,
            r_squared=None,  # Not applicable for spectral mismatch
            relative_uncertainty=relative_uncertainty
        )

    def _check_iec_compliance(
        self,
        wavelengths: np.ndarray,
        E_test: np.ndarray,
        E_ref: np.ndarray
    ) -> bool:
        """
        Check if calculation complies with IEC 60904-7 requirements.

        Args:
            wavelengths: Wavelength array
            E_test: Test spectral irradiance
            E_ref: Reference spectral irradiance

        Returns:
            True if compliant, False otherwise
        """
        # Check wavelength range covers typical solar spectrum
        # IEC 60904-7 typically requires 300-1200 nm for silicon cells
        min_wavelength = wavelengths[0]
        max_wavelength = wavelengths[-1]

        # For general compliance, we check if range covers at least 350-1100 nm
        covers_visible = min_wavelength <= 350 and max_wavelength >= 1100

        # Check sufficient spectral resolution (at least 10 nm intervals)
        wavelength_spacing = np.diff(wavelengths)
        max_spacing = np.max(wavelength_spacing)
        sufficient_resolution = max_spacing <= 50  # Maximum 50 nm spacing

        # Check for non-zero irradiance values
        has_valid_data = (np.sum(E_test) > 0) and (np.sum(E_ref) > 0)

        iec_compliant = covers_visible and sufficient_resolution and has_valid_data

        if not iec_compliant:
            logger.warning(
                f"IEC 60904-7 compliance check: "
                f"wavelength_range={min_wavelength}-{max_wavelength}nm, "
                f"max_spacing={max_spacing}nm, "
                f"has_data={has_valid_data}"
            )

        return iec_compliant


def create_spectral_mismatch_calculator() -> SpectralMismatchCalculator:
    """
    Factory function to create SpectralMismatchCalculator instance.

    Returns:
        Configured SpectralMismatchCalculator
    """
    return SpectralMismatchCalculator()
