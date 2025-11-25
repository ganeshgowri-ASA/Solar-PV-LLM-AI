"""
API routes for PV calculators.

Provides endpoints for:
- Energy Yield Calculator (PVWatts wrapper)
- Degradation Rate Calculator
- Spectral Mismatch Correction Calculator
"""
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from backend.models.schemas import (
    EnergyYieldRequest,
    EnergyYieldResponse,
    DegradationRateRequest,
    DegradationRateResponse,
    SpectralMismatchRequest,
    SpectralMismatchResponse,
    ErrorResponse
)
from backend.calculators.energy_yield import create_energy_yield_calculator
from backend.calculators.degradation_rate import create_degradation_rate_calculator
from backend.calculators.spectral_mismatch import create_spectral_mismatch_calculator
from backend.services.nrel_client import NRELAPIError


router = APIRouter(prefix="/calculators", tags=["Calculators"])


@router.post(
    "/energy-yield",
    response_model=EnergyYieldResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate PV system energy yield",
    description="""
    Calculate annual and monthly energy yield for a PV system using NREL PVWatts API.

    Returns energy production estimates with uncertainty quantification and
    confidence intervals. Based on typical meteorological year (TMY) data.

    **Features:**
    - Annual and monthly energy production (kWh)
    - Capacity factor and specific yield
    - Performance ratio estimation
    - Uncertainty metrics with 95% confidence intervals
    - Location-based solar resource data
    """
)
async def calculate_energy_yield(
    request: EnergyYieldRequest
) -> EnergyYieldResponse:
    """
    Calculate energy yield for a PV system.

    Args:
        request: Energy yield calculation parameters

    Returns:
        Energy yield response with uncertainty metrics

    Raises:
        HTTPException: If calculation fails
    """
    try:
        logger.info(
            f"Energy yield calculation requested for "
            f"({request.location.latitude}, {request.location.longitude})"
        )

        calculator = create_energy_yield_calculator()
        result = calculator.calculate(request)

        logger.info(
            f"Energy yield calculated: {result.annual_energy_kwh:.2f} kWh/year"
        )

        return result

    except NRELAPIError as e:
        logger.error(f"NREL API error in energy yield calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"NREL API error: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Validation error in energy yield calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error in energy yield calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/degradation-rate",
    response_model=DegradationRateResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate PV system degradation rate",
    description="""
    Analyze time series performance data to calculate annual degradation rate
    using robust statistical linear regression.

    **Features:**
    - Annual degradation rate estimation (% per year)
    - Robust regression with outlier detection
    - Expected lifetime to 80% capacity
    - Statistical uncertainty metrics with confidence intervals
    - Data quality scoring
    - Projected performance at year 25

    **Requirements:**
    - Minimum 12 data points (recommended: monthly data for 1+ years)
    - Normalized output values (relative to initial performance)
    """
)
async def calculate_degradation_rate(
    request: DegradationRateRequest
) -> DegradationRateResponse:
    """
    Calculate degradation rate from time series data.

    Args:
        request: Degradation rate calculation parameters

    Returns:
        Degradation rate response with uncertainty metrics

    Raises:
        HTTPException: If calculation fails
    """
    try:
        logger.info(
            f"Degradation rate calculation requested for "
            f"{len(request.data_points)} data points"
        )

        calculator = create_degradation_rate_calculator()
        result = calculator.calculate(request)

        logger.info(
            f"Degradation rate calculated: {result.degradation_rate_percent:.4f}%/year"
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error in degradation rate calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error in degradation rate calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/spectral-mismatch",
    response_model=SpectralMismatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate spectral mismatch correction",
    description="""
    Calculate spectral mismatch correction factor according to IEC 60904-7 standard.

    Used to correct PV device measurements for differences between test and
    reference spectral conditions.

    **IEC 60904-7 Formula:**

    M = (∫E_ref·S_ref dλ · ∫E_test·S_test dλ) / (∫E_test·S_ref dλ · ∫E_ref·S_test dλ)

    **Features:**
    - IEC 60904-7 compliant calculation
    - Spectral mismatch factor M
    - Corrected irradiance values
    - Uncertainty quantification
    - Compliance verification

    **Requirements:**
    - Wavelength array (nm)
    - Incident and reference spectral irradiance (W/m²/nm)
    - Cell spectral response (A/W)
    - Minimum 10 spectral data points
    - Wavelengths in ascending order
    """
)
async def calculate_spectral_mismatch(
    request: SpectralMismatchRequest
) -> SpectralMismatchResponse:
    """
    Calculate spectral mismatch correction factor.

    Args:
        request: Spectral mismatch calculation parameters

    Returns:
        Spectral mismatch response with correction factor

    Raises:
        HTTPException: If calculation fails
    """
    try:
        logger.info(
            f"Spectral mismatch calculation requested for "
            f"{len(request.wavelengths)} spectral points"
        )

        calculator = create_spectral_mismatch_calculator()
        result = calculator.calculate(request)

        logger.info(
            f"Spectral mismatch factor calculated: M = {result.mismatch_factor:.6f}"
        )

        return result

    except ValueError as e:
        logger.error(f"Validation error in spectral mismatch calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error in spectral mismatch calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
