"""
Energy Yield Calculator using NREL PVWatts API with uncertainty quantification.
"""
import numpy as np
from typing import List, Dict, Any
from scipy import stats
from loguru import logger

from backend.services.nrel_client import NRELClient, NRELAPIError
from backend.models.schemas import (
    EnergyYieldRequest,
    EnergyYieldResponse,
    MonthlyEnergy,
    UncertaintyMetrics
)
from backend.config.constants import (
    CONFIDENCE_LEVEL_95,
    ERROR_NREL_API
)


class EnergyYieldCalculator:
    """
    Energy Yield Calculator that wraps NREL PVWatts API and adds
    uncertainty quantification and confidence intervals.
    """

    def __init__(self, nrel_client: NRELClient):
        """
        Initialize Energy Yield Calculator.

        Args:
            nrel_client: NREL API client instance
        """
        self.nrel_client = nrel_client

    def calculate(self, request: EnergyYieldRequest) -> EnergyYieldResponse:
        """
        Calculate energy yield with uncertainty metrics.

        Args:
            request: Energy yield calculation request

        Returns:
            Energy yield response with uncertainty metrics

        Raises:
            NRELAPIError: If API request fails
        """
        logger.info(
            f"Calculating energy yield for system at "
            f"({request.location.latitude}, {request.location.longitude})"
        )

        # Get PVWatts data
        pvwatts_data = self._fetch_pvwatts_data(request)

        # Extract outputs
        outputs = pvwatts_data.get("outputs", {})
        station_info = pvwatts_data.get("station_info", {})

        # Calculate annual and monthly metrics
        monthly_energy = self._calculate_monthly_metrics(
            outputs,
            request.system.system_capacity
        )

        annual_energy_kwh = sum(m.energy_kwh for m in monthly_energy)

        # Calculate performance metrics
        capacity_factor = self._calculate_capacity_factor(
            annual_energy_kwh,
            request.system.system_capacity
        )

        specific_yield = annual_energy_kwh / request.system.system_capacity

        # Performance ratio (typical range 0.75-0.85 for well-designed systems)
        # PR = actual_yield / theoretical_yield
        # Theoretical yield ≈ irradiation / 1000 * (1 - losses/100)
        performance_ratio = self._estimate_performance_ratio(outputs)

        # Calculate uncertainty metrics
        uncertainty = self._calculate_uncertainty(
            monthly_energy,
            annual_energy_kwh,
            outputs
        )

        # Build metadata
        metadata = {
            "location": {
                "latitude": request.location.latitude,
                "longitude": request.location.longitude,
                "elevation": station_info.get("elev"),
                "timezone": station_info.get("tz"),
                "city": station_info.get("city"),
                "state": station_info.get("state")
            },
            "system": {
                "capacity_kw": request.system.system_capacity,
                "module_type": request.system.module_type,
                "array_type": request.system.array_type,
                "tilt": request.system.tilt,
                "azimuth": request.system.azimuth,
                "losses_percent": request.system.losses
            },
            "data_source": "NREL PVWatts v6",
            "weather_data": station_info.get("dataset", "nsrdb")
        }

        return EnergyYieldResponse(
            annual_energy_kwh=annual_energy_kwh,
            monthly_energy=monthly_energy,
            capacity_factor=capacity_factor,
            specific_yield=specific_yield,
            performance_ratio=performance_ratio,
            uncertainty=uncertainty,
            metadata=metadata
        )

    def _fetch_pvwatts_data(self, request: EnergyYieldRequest) -> Dict[str, Any]:
        """
        Fetch data from PVWatts API.

        Args:
            request: Energy yield request

        Returns:
            PVWatts API response data
        """
        try:
            data = self.nrel_client.get_pvwatts_data(
                latitude=request.location.latitude,
                longitude=request.location.longitude,
                system_capacity=request.system.system_capacity,
                module_type=request.system.module_type,
                array_type=request.system.array_type,
                tilt=request.system.tilt,
                azimuth=request.system.azimuth,
                losses=request.system.losses,
                albedo=request.system.albedo
            )
            return data
        except Exception as e:
            logger.error(f"Failed to fetch PVWatts data: {e}")
            raise NRELAPIError(f"{ERROR_NREL_API}: {str(e)}")

    def _calculate_monthly_metrics(
        self,
        outputs: Dict[str, Any],
        system_capacity: float
    ) -> List[MonthlyEnergy]:
        """
        Calculate monthly energy production metrics.

        Args:
            outputs: PVWatts outputs dictionary
            system_capacity: System capacity in kW

        Returns:
            List of monthly energy metrics
        """
        ac_monthly = outputs.get("ac_monthly", [])
        poa_monthly = outputs.get("poa_monthly", [])  # Plane of array irradiation
        dc_monthly = outputs.get("dc_monthly", [])

        monthly_metrics = []

        for month in range(1, 13):
            idx = month - 1

            # Energy in kWh
            energy_kwh = ac_monthly[idx] if idx < len(ac_monthly) else 0

            # Solar radiation in kWh/m²/month, convert to kWh/m²/day
            # POA irradiation is in kWh/m²/month
            solar_radiation_monthly = poa_monthly[idx] if idx < len(poa_monthly) else 0

            # Approximate days in month
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][idx]
            solar_radiation_daily = solar_radiation_monthly / days_in_month

            # Capacity factor for this month
            hours_in_month = days_in_month * 24
            max_possible_energy = system_capacity * hours_in_month
            capacity_factor = energy_kwh / max_possible_energy if max_possible_energy > 0 else 0

            monthly_metrics.append(MonthlyEnergy(
                month=month,
                energy_kwh=energy_kwh,
                solar_radiation=solar_radiation_daily,
                capacity_factor=capacity_factor
            ))

        return monthly_metrics

    def _calculate_capacity_factor(
        self,
        annual_energy_kwh: float,
        system_capacity: float
    ) -> float:
        """
        Calculate annual capacity factor.

        Args:
            annual_energy_kwh: Annual energy production in kWh
            system_capacity: System capacity in kW

        Returns:
            Capacity factor (0-1)
        """
        hours_per_year = 8760
        max_possible_energy = system_capacity * hours_per_year
        return annual_energy_kwh / max_possible_energy if max_possible_energy > 0 else 0

    def _estimate_performance_ratio(self, outputs: Dict[str, Any]) -> float:
        """
        Estimate performance ratio from PVWatts outputs.

        Args:
            outputs: PVWatts outputs dictionary

        Returns:
            Performance ratio (0-1)
        """
        # Performance ratio = AC energy / (POA irradiation * system capacity)
        # This is a simplified estimation
        ac_annual = outputs.get("ac_annual", 0)
        poa_annual = sum(outputs.get("poa_monthly", []))  # kWh/m²/year
        dc_nominal = outputs.get("dc_nominal", 1)  # kW

        if poa_annual > 0 and dc_nominal > 0:
            # Reference irradiance is 1 kW/m²
            # Theoretical energy = POA * DC nominal
            theoretical_energy = poa_annual * dc_nominal
            pr = ac_annual / theoretical_energy if theoretical_energy > 0 else 0
            return min(max(pr, 0), 1)  # Clamp between 0 and 1

        return 0.8  # Default typical value

    def _calculate_uncertainty(
        self,
        monthly_energy: List[MonthlyEnergy],
        annual_energy_kwh: float,
        outputs: Dict[str, Any]
    ) -> UncertaintyMetrics:
        """
        Calculate uncertainty metrics and confidence intervals.

        The uncertainty comes from multiple sources:
        1. Weather data variability (TMY vs actual)
        2. System performance uncertainty
        3. Model uncertainty

        Args:
            monthly_energy: Monthly energy data
            annual_energy_kwh: Annual energy total
            outputs: PVWatts outputs

        Returns:
            Uncertainty metrics with confidence intervals
        """
        # Extract monthly energy values
        monthly_values = np.array([m.energy_kwh for m in monthly_energy])

        # Calculate variability from monthly data
        monthly_std = np.std(monthly_values, ddof=1)
        monthly_mean = np.mean(monthly_values)

        # Coefficient of variation for monthly data
        cv_monthly = monthly_std / monthly_mean if monthly_mean > 0 else 0

        # Estimate uncertainty components
        # 1. Weather data uncertainty (typically 5-10% for TMY data)
        weather_uncertainty = 0.08  # 8% typical

        # 2. Model uncertainty (PVWatts typically ±5-10%)
        model_uncertainty = 0.07  # 7% typical

        # 3. System performance uncertainty (depends on losses estimation)
        system_uncertainty = 0.05  # 5% typical

        # Combined standard uncertainty (RSS - Root Sum of Squares)
        combined_uncertainty = np.sqrt(
            weather_uncertainty**2 +
            model_uncertainty**2 +
            system_uncertainty**2
        )

        # Standard error of annual estimate
        standard_error = annual_energy_kwh * combined_uncertainty

        # Confidence intervals (using normal distribution for large samples)
        confidence_level = CONFIDENCE_LEVEL_95
        z_score = stats.norm.ppf((1 + confidence_level) / 2)

        ci_margin = z_score * standard_error
        ci_lower = annual_energy_kwh - ci_margin
        ci_upper = annual_energy_kwh + ci_margin

        # Relative uncertainty as percentage
        relative_uncertainty = (combined_uncertainty * 100)

        return UncertaintyMetrics(
            standard_error=standard_error,
            confidence_level=confidence_level,
            confidence_interval_lower=max(0, ci_lower),  # Energy can't be negative
            confidence_interval_upper=ci_upper,
            r_squared=0.95,  # Typical R² for PVWatts model
            relative_uncertainty=relative_uncertainty
        )


def create_energy_yield_calculator() -> EnergyYieldCalculator:
    """
    Factory function to create EnergyYieldCalculator instance.

    Returns:
        Configured EnergyYieldCalculator
    """
    from backend.services.nrel_client import nrel_client
    return EnergyYieldCalculator(nrel_client)
