"""
PV calculation endpoints for solar system performance analysis.
"""
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from app.models.schemas import (
    PVSystemInput,
    PVOutputEstimate,
    PVPerformanceRatio
)
from app.services.pv_calculator import pv_calculator
from app.core.security import verify_api_key

router = APIRouter(prefix="/pv", tags=["PV Calculations"])


@router.post("/estimate-output", response_model=PVOutputEstimate)
async def estimate_output(
    system_input: PVSystemInput,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Estimate PV system energy output.

    Calculate daily, monthly, and annual energy production estimates
    based on system parameters and location.

    **Input Parameters:**
    - Panel capacity (kW)
    - Panel efficiency (0-1)
    - System losses (0-1)
    - Tilt and azimuth angles
    - Geographic location (lat/lon)

    **Returns:**
    - Daily, monthly, annual energy estimates (kWh)
    - Capacity factor
    - Peak sun hours
    """
    try:
        logger.info(f"Calculating output for {system_input.panel_capacity_kw}kW system")

        estimate = pv_calculator.estimate_output(system_input)

        return estimate

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error estimating output: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance-ratio", response_model=PVPerformanceRatio)
async def calculate_performance_ratio(
    actual_output_kwh: float,
    expected_output_kwh: float,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Calculate PV system performance ratio.

    Compare actual vs expected system output to determine
    performance efficiency.

    **Parameters:**
    - actual_output_kwh: Measured system output
    - expected_output_kwh: Theoretical/expected output

    **Returns:**
    - Performance ratio (0-1)
    - Efficiency loss percentage
    """
    try:
        pr = pv_calculator.calculate_performance_ratio(
            actual_output_kwh,
            expected_output_kwh
        )

        return pr

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating performance ratio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/optimal-tilt/{latitude}")
async def get_optimal_tilt(
    latitude: float,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Calculate optimal panel tilt angles.

    Get recommended tilt angles for different seasons
    based on geographic latitude.

    **Parameters:**
    - latitude: Geographic latitude (-90 to 90)

    **Returns:**
    - Annual optimal tilt
    - Summer optimal tilt
    - Winter optimal tilt
    """
    try:
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")

        tilt_angles = pv_calculator.calculate_optimal_tilt(latitude)

        return tilt_angles

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating optimal tilt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payback-period")
async def calculate_payback(
    system_cost: float,
    annual_savings: float,
    annual_degradation: float = 0.005,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Calculate financial payback period.

    Estimate time to recover initial system investment
    considering annual degradation.

    **Parameters:**
    - system_cost: Total system installation cost
    - annual_savings: Annual energy cost savings
    - annual_degradation: Annual efficiency degradation rate (default 0.5%)

    **Returns:**
    - Simple payback period (years)
    - Adjusted payback with degradation (years)
    - Total 25-year savings
    """
    try:
        if system_cost <= 0:
            raise ValueError("System cost must be greater than 0")
        if annual_savings <= 0:
            raise ValueError("Annual savings must be greater than 0")
        if not (0 <= annual_degradation <= 0.1):
            raise ValueError("Annual degradation must be between 0 and 0.1")

        payback = pv_calculator.calculate_payback_period(
            system_cost,
            annual_savings,
            annual_degradation
        )

        return payback

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating payback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peak-sun-hours")
async def get_peak_sun_hours(
    latitude: float,
    tilt_angle: float = None,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Calculate peak sun hours for location.

    Estimate average daily peak sun hours based on
    geographic location and panel tilt.

    **Parameters:**
    - latitude: Geographic latitude
    - tilt_angle: Panel tilt angle (optional, defaults to latitude)

    **Returns:**
    - Peak sun hours per day
    """
    try:
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")

        if tilt_angle is not None and not (0 <= tilt_angle <= 90):
            raise ValueError("Tilt angle must be between 0 and 90")

        psh = pv_calculator.calculate_peak_sun_hours(latitude, tilt_angle)

        return {
            "latitude": latitude,
            "tilt_angle": tilt_angle or abs(latitude),
            "peak_sun_hours": psh
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating peak sun hours: {e}")
        raise HTTPException(status_code=500, detail=str(e))
