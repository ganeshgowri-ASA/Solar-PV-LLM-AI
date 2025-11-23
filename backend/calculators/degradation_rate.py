"""
Degradation Rate Calculator using statistical linear regression.

Analyzes time series PV performance data to calculate annual degradation rate
with robust regression methods and uncertainty quantification.
"""
import numpy as np
from typing import Tuple, List
from datetime import datetime, timedelta
from scipy import stats
from sklearn.linear_model import HuberRegressor, LinearRegression
from loguru import logger

from backend.models.schemas import (
    DegradationRateRequest,
    DegradationRateResponse,
    DegradationDataPoint,
    UncertaintyMetrics
)
from backend.config.constants import (
    MIN_DATA_POINTS_DEGRADATION,
    MIN_R_SQUARED_DEGRADATION,
    CONFIDENCE_LEVEL_95,
    ERROR_INSUFFICIENT_DATA
)


class DegradationRateCalculator:
    """
    Calculator for PV system degradation rate using statistical regression.

    Implements both ordinary least squares (OLS) and robust regression
    methods to handle outliers and provide reliable degradation estimates.
    """

    def __init__(self):
        """Initialize Degradation Rate Calculator."""
        pass

    def calculate(self, request: DegradationRateRequest) -> DegradationRateResponse:
        """
        Calculate degradation rate from time series data.

        Args:
            request: Degradation rate calculation request

        Returns:
            Degradation rate response with uncertainty metrics

        Raises:
            ValueError: If insufficient data or invalid parameters
        """
        logger.info(
            f"Calculating degradation rate from {len(request.data_points)} data points"
        )

        # Validate input data
        if len(request.data_points) < MIN_DATA_POINTS_DEGRADATION:
            raise ValueError(
                f"{ERROR_INSUFFICIENT_DATA}. "
                f"Minimum {MIN_DATA_POINTS_DEGRADATION} points required, "
                f"got {len(request.data_points)}"
            )

        # Prepare data
        timestamps, normalized_output = self._prepare_data(request.data_points)

        # Convert timestamps to years since first measurement
        time_years = self._timestamps_to_years(timestamps)

        # Detect and remove outliers if requested
        if request.use_robust_regression:
            clean_indices, outlier_count = self._detect_outliers(
                time_years,
                normalized_output
            )
            time_years_clean = time_years[clean_indices]
            output_clean = normalized_output[clean_indices]
        else:
            time_years_clean = time_years
            output_clean = normalized_output
            outlier_count = 0

        # Perform regression
        degradation_rate, r_squared, regression_stats = self._perform_regression(
            time_years_clean,
            output_clean,
            use_robust=request.use_robust_regression
        )

        # Calculate uncertainty metrics
        uncertainty = self._calculate_uncertainty(
            time_years_clean,
            output_clean,
            degradation_rate,
            regression_stats
        )

        # Calculate analysis period
        analysis_period_years = time_years[-1] - time_years[0]

        # Calculate expected lifetime to 80% capacity
        # P(t) = P0 * (1 + degradation_rate * t)
        # 0.8 = 1 + degradation_rate * t
        # t = -0.2 / degradation_rate
        if degradation_rate < 0:
            expected_lifetime_years = -0.2 / degradation_rate
        else:
            expected_lifetime_years = float('inf')  # No degradation detected

        # Project output at year 25
        projected_output_year_25 = 1.0 + (degradation_rate * 25)

        # Calculate data quality score
        data_quality_score = self._calculate_data_quality_score(
            r_squared,
            len(time_years_clean),
            outlier_count,
            len(request.data_points)
        )

        return DegradationRateResponse(
            degradation_rate_per_year=degradation_rate,
            degradation_rate_percent=degradation_rate * 100,
            expected_lifetime_years=min(expected_lifetime_years, 100),  # Cap at 100 years
            uncertainty=uncertainty,
            data_quality_score=data_quality_score,
            outliers_detected=outlier_count,
            analysis_period_years=analysis_period_years,
            projected_output_year_25=max(0, projected_output_year_25)
        )

    def _prepare_data(
        self,
        data_points: List[DegradationDataPoint]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for regression analysis.

        Args:
            data_points: List of data points

        Returns:
            Tuple of (timestamps, normalized_output) arrays
        """
        # Sort by timestamp
        sorted_points = sorted(data_points, key=lambda p: p.timestamp)

        timestamps = np.array([p.timestamp for p in sorted_points])
        normalized_output = np.array([p.normalized_output for p in sorted_points])

        return timestamps, normalized_output

    def _timestamps_to_years(self, timestamps: np.ndarray) -> np.ndarray:
        """
        Convert timestamps to years since first measurement.

        Args:
            timestamps: Array of datetime objects

        Returns:
            Array of years (float)
        """
        reference_time = timestamps[0]
        time_deltas = np.array([
            (ts - reference_time).total_seconds() / (365.25 * 24 * 3600)
            for ts in timestamps
        ])
        return time_deltas

    def _detect_outliers(
        self,
        time_years: np.ndarray,
        normalized_output: np.ndarray,
        threshold: float = 3.0
    ) -> Tuple[np.ndarray, int]:
        """
        Detect and remove outliers using modified Z-score method.

        Args:
            time_years: Time in years
            normalized_output: Normalized output values
            threshold: Z-score threshold for outlier detection

        Returns:
            Tuple of (clean_indices, outlier_count)
        """
        # First pass: fit a robust regression
        X = time_years.reshape(-1, 1)
        y = normalized_output

        regressor = HuberRegressor(epsilon=1.35, max_iter=100)
        regressor.fit(X, y)
        predictions = regressor.predict(X)

        # Calculate residuals
        residuals = y - predictions

        # Use median absolute deviation (MAD) for robust outlier detection
        mad = np.median(np.abs(residuals - np.median(residuals)))
        modified_z_scores = 0.6745 * (residuals - np.median(residuals)) / mad if mad > 0 else np.zeros_like(residuals)

        # Identify inliers
        inlier_mask = np.abs(modified_z_scores) < threshold
        outlier_count = np.sum(~inlier_mask)

        logger.info(f"Detected {outlier_count} outliers out of {len(time_years)} points")

        return np.where(inlier_mask)[0], int(outlier_count)

    def _perform_regression(
        self,
        time_years: np.ndarray,
        normalized_output: np.ndarray,
        use_robust: bool = True
    ) -> Tuple[float, float, dict]:
        """
        Perform linear regression to estimate degradation rate.

        Args:
            time_years: Time in years
            normalized_output: Normalized output values
            use_robust: Whether to use robust regression

        Returns:
            Tuple of (degradation_rate, r_squared, regression_stats)
        """
        X = time_years.reshape(-1, 1)
        y = normalized_output

        if use_robust:
            # Huber regression is robust to outliers
            regressor = HuberRegressor(epsilon=1.35, max_iter=200)
            regressor.fit(X, y)
            degradation_rate = regressor.coef_[0]
            predictions = regressor.predict(X)

            # Calculate R² manually for robust regression
            ss_res = np.sum((y - predictions) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            # Standard error estimate
            residuals = y - predictions
            n = len(y)
            mse = np.sum(residuals ** 2) / (n - 2) if n > 2 else 0
            std_error = np.sqrt(mse)

        else:
            # Ordinary least squares
            regressor = LinearRegression()
            regressor.fit(X, y)
            degradation_rate = regressor.coef_[0]
            r_squared = regressor.score(X, y)
            predictions = regressor.predict(X)

            residuals = y - predictions
            n = len(y)
            mse = np.sum(residuals ** 2) / (n - 2) if n > 2 else 0
            std_error = np.sqrt(mse)

        # Additional regression statistics
        regression_stats = {
            'intercept': regressor.intercept_,
            'slope': degradation_rate,
            'std_error': std_error,
            'predictions': predictions,
            'residuals': residuals,
            'n_points': len(time_years)
        }

        logger.info(
            f"Regression complete: degradation rate = {degradation_rate:.6f}/year "
            f"({degradation_rate*100:.4f}%/year), R² = {r_squared:.4f}"
        )

        return degradation_rate, r_squared, regression_stats

    def _calculate_uncertainty(
        self,
        time_years: np.ndarray,
        normalized_output: np.ndarray,
        degradation_rate: float,
        regression_stats: dict
    ) -> UncertaintyMetrics:
        """
        Calculate uncertainty metrics for degradation rate estimate.

        Args:
            time_years: Time in years
            normalized_output: Normalized output values
            degradation_rate: Estimated degradation rate
            regression_stats: Regression statistics dictionary

        Returns:
            Uncertainty metrics
        """
        n = regression_stats['n_points']
        std_error = regression_stats['std_error']

        # Standard error of the slope
        # SE(slope) = std_error / sqrt(sum((x - x_mean)^2))
        x_mean = np.mean(time_years)
        ss_x = np.sum((time_years - x_mean) ** 2)
        se_slope = std_error / np.sqrt(ss_x) if ss_x > 0 else 0

        # Confidence intervals for degradation rate
        confidence_level = CONFIDENCE_LEVEL_95
        t_critical = stats.t.ppf((1 + confidence_level) / 2, df=n-2) if n > 2 else 2.0

        ci_margin = t_critical * se_slope
        ci_lower = degradation_rate - ci_margin
        ci_upper = degradation_rate + ci_margin

        # Relative uncertainty
        relative_uncertainty = (abs(se_slope / degradation_rate) * 100) if degradation_rate != 0 else 100

        # R-squared from regression
        r_squared = 1 - (np.sum(regression_stats['residuals']**2) /
                        np.sum((normalized_output - np.mean(normalized_output))**2))

        return UncertaintyMetrics(
            standard_error=se_slope,
            confidence_level=confidence_level,
            confidence_interval_lower=ci_lower,
            confidence_interval_upper=ci_upper,
            r_squared=max(0, min(1, r_squared)),  # Clamp between 0 and 1
            relative_uncertainty=relative_uncertainty
        )

    def _calculate_data_quality_score(
        self,
        r_squared: float,
        n_clean_points: int,
        n_outliers: int,
        n_total_points: int
    ) -> float:
        """
        Calculate overall data quality score (0-1).

        Args:
            r_squared: R-squared value from regression
            n_clean_points: Number of points after outlier removal
            n_outliers: Number of detected outliers
            n_total_points: Total number of original points

        Returns:
            Data quality score (0-1)
        """
        # Component 1: Goodness of fit (R²)
        fit_score = r_squared

        # Component 2: Data completeness (more points = better)
        # Normalize to [0, 1], with 100+ points = perfect
        completeness_score = min(n_clean_points / 100, 1.0)

        # Component 3: Outlier ratio (fewer outliers = better)
        outlier_ratio = n_outliers / n_total_points if n_total_points > 0 else 0
        outlier_score = 1.0 - outlier_ratio

        # Weighted average
        quality_score = (
            0.5 * fit_score +
            0.3 * completeness_score +
            0.2 * outlier_score
        )

        return max(0, min(1, quality_score))


def create_degradation_rate_calculator() -> DegradationRateCalculator:
    """
    Factory function to create DegradationRateCalculator instance.

    Returns:
        Configured DegradationRateCalculator
    """
    return DegradationRateCalculator()
