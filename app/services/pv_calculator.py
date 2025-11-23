"""
Solar PV Calculator Service.
Provides calculations for PV system performance, output, and efficiency.
"""
import math
from typing import Dict, Tuple
from loguru import logger

from app.models.schemas import PVSystemInput, PVOutputEstimate, PVPerformanceRatio


class PVCalculator:
    """
    Solar PV Calculator for system performance and output calculations.
    Implements industry-standard formulas for solar energy estimation.
    """

    # Constants
    SOLAR_CONSTANT = 1367  # W/m² (solar irradiance at top of atmosphere)
    HOURS_PER_DAY = 24
    DAYS_PER_MONTH = 30.44  # Average
    DAYS_PER_YEAR = 365.25

    def __init__(self):
        """Initialize PV calculator."""
        logger.info("PV Calculator initialized")

    def calculate_solar_irradiance(
        self,
        latitude: float,
        day_of_year: int = 172  # Summer solstice default
    ) -> float:
        """
        Calculate solar irradiance at location.

        Args:
            latitude: Location latitude in degrees
            day_of_year: Day of year (1-365)

        Returns:
            Solar irradiance in kWh/m²/day
        """
        # Simplified calculation - in production, use NREL or similar data
        # This uses a cosine approximation based on latitude
        lat_rad = math.radians(abs(latitude))

        # Declination angle
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
        decl_rad = math.radians(declination)

        # Hour angle at sunrise/sunset
        hour_angle = math.acos(-math.tan(lat_rad) * math.tan(decl_rad))

        # Daily solar irradiance (simplified)
        irradiance = (
            self.SOLAR_CONSTANT
            * (hour_angle * math.sin(lat_rad) * math.sin(decl_rad)
               + math.cos(lat_rad) * math.cos(decl_rad) * math.sin(hour_angle))
            / (math.pi * 1000)  # Convert W to kW
        )

        # Adjust for atmospheric conditions (simplified)
        irradiance *= 0.7  # Atmospheric losses

        return max(0, irradiance)

    def calculate_peak_sun_hours(
        self,
        latitude: float,
        tilt_angle: float = None
    ) -> float:
        """
        Calculate peak sun hours for location.

        Args:
            latitude: Location latitude
            tilt_angle: Panel tilt angle (if None, uses latitude)

        Returns:
            Peak sun hours per day
        """
        if tilt_angle is None:
            tilt_angle = abs(latitude)  # Optimal tilt ≈ latitude

        # Simplified calculation
        # In production, use detailed solar radiation databases
        base_psh = 4.5  # Average baseline

        # Adjust for latitude (more sun near equator)
        lat_factor = 1 - (abs(latitude) / 90) * 0.3

        # Tilt optimization factor
        tilt_factor = 1 + (0.1 if abs(tilt_angle - abs(latitude)) < 15 else 0)

        psh = base_psh * lat_factor * tilt_factor

        return round(psh, 2)

    def estimate_output(
        self,
        system_input: PVSystemInput
    ) -> PVOutputEstimate:
        """
        Estimate PV system output.

        Args:
            system_input: System parameters

        Returns:
            Output estimation
        """
        logger.info(f"Calculating output for {system_input.panel_capacity_kw}kW system")

        # Calculate peak sun hours
        peak_sun_hours = self.calculate_peak_sun_hours(
            system_input.location_lat,
            system_input.tilt_angle
        )

        # Calculate daily energy output
        # E = P * PSH * η * (1 - losses)
        daily_energy = (
            system_input.panel_capacity_kw
            * peak_sun_hours
            * system_input.panel_efficiency
            * (1 - system_input.system_losses)
        )

        # Calculate monthly and annual
        monthly_energy = daily_energy * self.DAYS_PER_MONTH
        annual_energy = daily_energy * self.DAYS_PER_YEAR

        # Calculate capacity factor
        # CF = Actual output / Maximum possible output
        max_possible_daily = system_input.panel_capacity_kw * self.HOURS_PER_DAY
        capacity_factor = (daily_energy / max_possible_daily) if max_possible_daily > 0 else 0

        estimate = PVOutputEstimate(
            daily_energy_kwh=round(daily_energy, 2),
            monthly_energy_kwh=round(monthly_energy, 2),
            annual_energy_kwh=round(annual_energy, 2),
            capacity_factor=round(capacity_factor, 3),
            peak_sun_hours=peak_sun_hours
        )

        logger.info(
            f"Estimated output: {estimate.annual_energy_kwh} kWh/year "
            f"(CF: {estimate.capacity_factor:.1%})"
        )

        return estimate

    def calculate_performance_ratio(
        self,
        actual_output_kwh: float,
        expected_output_kwh: float
    ) -> PVPerformanceRatio:
        """
        Calculate system performance ratio.

        Args:
            actual_output_kwh: Actual measured output
            expected_output_kwh: Expected/theoretical output

        Returns:
            Performance ratio calculation
        """
        if expected_output_kwh <= 0:
            raise ValueError("Expected output must be greater than 0")

        # Performance Ratio (PR) = Actual / Expected
        pr = actual_output_kwh / expected_output_kwh

        # Calculate efficiency loss
        efficiency_loss = (1 - pr) * 100

        result = PVPerformanceRatio(
            actual_output_kwh=actual_output_kwh,
            expected_output_kwh=expected_output_kwh,
            performance_ratio=round(pr, 3),
            efficiency_loss=round(efficiency_loss, 2)
        )

        logger.info(
            f"Performance Ratio: {result.performance_ratio:.1%} "
            f"(Loss: {result.efficiency_loss:.1f}%)"
        )

        return result

    def calculate_optimal_tilt(self, latitude: float) -> Dict[str, float]:
        """
        Calculate optimal panel tilt angles for different seasons.

        Args:
            latitude: Location latitude

        Returns:
            Dict with optimal tilt angles
        """
        # General rule: tilt = latitude ± 15°
        annual_optimal = abs(latitude)
        summer_optimal = max(0, abs(latitude) - 15)
        winter_optimal = min(90, abs(latitude) + 15)

        return {
            "annual_optimal": round(annual_optimal, 1),
            "summer_optimal": round(summer_optimal, 1),
            "winter_optimal": round(winter_optimal, 1),
            "latitude": latitude
        }

    def calculate_payback_period(
        self,
        system_cost: float,
        annual_savings: float,
        annual_degradation: float = 0.005
    ) -> Dict[str, float]:
        """
        Calculate financial payback period.

        Args:
            system_cost: Initial system cost
            annual_savings: Annual energy cost savings
            annual_degradation: Annual system degradation rate

        Returns:
            Payback analysis
        """
        if annual_savings <= 0:
            raise ValueError("Annual savings must be greater than 0")

        # Simple payback (without degradation)
        simple_payback = system_cost / annual_savings

        # Adjusted for degradation
        # More complex calculation considering degrading output
        total_savings = 0
        year = 0
        current_savings = annual_savings

        while total_savings < system_cost and year < 50:
            year += 1
            total_savings += current_savings
            current_savings *= (1 - annual_degradation)

        adjusted_payback = year if total_savings >= system_cost else -1

        return {
            "simple_payback_years": round(simple_payback, 1),
            "adjusted_payback_years": adjusted_payback,
            "total_25year_savings": round(
                sum(annual_savings * (1 - annual_degradation) ** y for y in range(25)),
                2
            )
        }


# Global PV calculator instance
pv_calculator = PVCalculator()
