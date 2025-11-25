"""
Unit tests for Degradation Rate Calculator.
"""
import pytest
import numpy as np
from datetime import datetime, timedelta
from backend.calculators.degradation_rate import DegradationRateCalculator
from backend.models.schemas import (
    DegradationRateRequest,
    DegradationDataPoint
)


class TestDegradationRateCalculator:
    """Test suite for Degradation Rate Calculator."""

    def test_calculate_degradation_rate_success(self, sample_degradation_data):
        """Test successful degradation rate calculation."""
        request = DegradationRateRequest(
            data_points=[DegradationDataPoint(**dp) for dp in sample_degradation_data],
            system_capacity_kw=4.0,
            use_robust_regression=True
        )

        calculator = DegradationRateCalculator()
        result = calculator.calculate(request)

        # Assertions
        assert result.degradation_rate_per_year < 0  # Should be negative (degradation)
        assert -0.02 < result.degradation_rate_per_year < 0  # Reasonable range
        assert abs(result.degradation_rate_percent) < 2.0  # Less than 2%/year
        assert result.expected_lifetime_years > 0
        assert 0 <= result.data_quality_score <= 1
        assert result.analysis_period_years > 0

    def test_degradation_rate_known_degradation(self):
        """Test with synthetic data with known degradation rate."""
        # Create synthetic data with -0.5%/year degradation
        degradation_rate = -0.005
        start_date = datetime(2020, 1, 1)
        data_points = []

        for month in range(36):  # 3 years
            timestamp = start_date + timedelta(days=30 * month)
            years = month / 12
            # Perfect linear degradation
            normalized_output = 1.0 + (degradation_rate * years)

            data_points.append(DegradationDataPoint(
                timestamp=timestamp,
                normalized_output=normalized_output
            ))

        request = DegradationRateRequest(
            data_points=data_points,
            system_capacity_kw=4.0,
            use_robust_regression=False  # Use OLS for perfect data
        )

        calculator = DegradationRateCalculator()
        result = calculator.calculate(request)

        # Should be very close to -0.5%/year
        assert abs(result.degradation_rate_percent - (-0.5)) < 0.1  # Within 0.1%

    def test_outlier_detection(self):
        """Test robust regression with outliers."""
        # Create data with some outliers
        degradation_rate = -0.005
        start_date = datetime(2020, 1, 1)
        data_points = []

        for month in range(36):
            timestamp = start_date + timedelta(days=30 * month)
            years = month / 12
            normalized_output = 1.0 + (degradation_rate * years)

            # Add outliers at specific points
            if month in [10, 20]:
                normalized_output *= 0.7  # 30% drop (outlier)

            data_points.append(DegradationDataPoint(
                timestamp=timestamp,
                normalized_output=normalized_output
            ))

        request = DegradationRateRequest(
            data_points=data_points,
            system_capacity_kw=4.0,
            use_robust_regression=True
        )

        calculator = DegradationRateCalculator()
        result = calculator.calculate(request)

        # Should detect the outliers
        assert result.outliers_detected > 0

        # Degradation rate should still be close despite outliers
        assert abs(result.degradation_rate_percent - (-0.5)) < 0.3

    def test_minimum_data_points_requirement(self):
        """Test that minimum data points requirement is enforced."""
        # Create insufficient data (only 10 points, need 12)
        start_date = datetime(2020, 1, 1)
        data_points = [
            DegradationDataPoint(
                timestamp=start_date + timedelta(days=30 * i),
                normalized_output=1.0 - 0.01 * i
            )
            for i in range(10)
        ]

        request = DegradationRateRequest(
            data_points=data_points,
            system_capacity_kw=4.0
        )

        calculator = DegradationRateCalculator()

        with pytest.raises(ValueError, match="Insufficient data"):
            calculator.calculate(request)

    def test_expected_lifetime_calculation(self):
        """Test expected lifetime to 80% capacity calculation."""
        # -0.5%/year degradation
        # Time to 80%: -20% / -0.5% = 40 years
        degradation_rate = -0.005
        start_date = datetime(2020, 1, 1)

        data_points = [
            DegradationDataPoint(
                timestamp=start_date + timedelta(days=30 * i),
                normalized_output=1.0 + degradation_rate * (i / 12)
            )
            for i in range(24)  # 2 years of monthly data
        ]

        request = DegradationRateRequest(
            data_points=data_points,
            system_capacity_kw=4.0,
            use_robust_regression=False
        )

        calculator = DegradationRateCalculator()
        result = calculator.calculate(request)

        # Expected lifetime should be around 40 years
        assert 35 < result.expected_lifetime_years < 45

    def test_projected_output_year_25(self):
        """Test projected output at year 25."""
        # -0.5%/year degradation
        # At year 25: 1.0 + (-0.005 * 25) = 0.875 (87.5%)
        degradation_rate = -0.005
        start_date = datetime(2020, 1, 1)

        data_points = [
            DegradationDataPoint(
                timestamp=start_date + timedelta(days=30 * i),
                normalized_output=1.0 + degradation_rate * (i / 12)
            )
            for i in range(24)
        ]

        request = DegradationRateRequest(
            data_points=data_points,
            system_capacity_kw=4.0,
            use_robust_regression=False
        )

        calculator = DegradationRateCalculator()
        result = calculator.calculate(request)

        # Should be around 87.5%
        assert 0.85 < result.projected_output_year_25 < 0.90

    def test_uncertainty_metrics(self, sample_degradation_data):
        """Test uncertainty calculation."""
        request = DegradationRateRequest(
            data_points=[DegradationDataPoint(**dp) for dp in sample_degradation_data],
            system_capacity_kw=4.0,
            use_robust_regression=True
        )

        calculator = DegradationRateCalculator()
        result = calculator.calculate(request)

        # Check uncertainty metrics
        assert result.uncertainty.standard_error > 0
        assert result.uncertainty.confidence_level == 0.95
        assert result.uncertainty.confidence_interval_lower < result.degradation_rate_per_year
        assert result.uncertainty.confidence_interval_upper > result.degradation_rate_per_year
        assert result.uncertainty.r_squared is not None
        assert 0 <= result.uncertainty.r_squared <= 1

    def test_data_quality_score(self, sample_degradation_data):
        """Test data quality scoring."""
        request = DegradationRateRequest(
            data_points=[DegradationDataPoint(**dp) for dp in sample_degradation_data],
            system_capacity_kw=4.0,
            use_robust_regression=True
        )

        calculator = DegradationRateCalculator()
        result = calculator.calculate(request)

        # Quality score should be between 0 and 1
        assert 0 <= result.data_quality_score <= 1

        # With good synthetic data, quality should be reasonably high
        assert result.data_quality_score > 0.5

    def test_no_degradation_scenario(self):
        """Test scenario with no degradation (stable performance)."""
        start_date = datetime(2020, 1, 1)
        data_points = [
            DegradationDataPoint(
                timestamp=start_date + timedelta(days=30 * i),
                normalized_output=1.0 + np.random.normal(0, 0.01)  # Only noise
            )
            for i in range(24)
        ]

        request = DegradationRateRequest(
            data_points=data_points,
            system_capacity_kw=4.0,
            use_robust_regression=True
        )

        calculator = DegradationRateCalculator()
        result = calculator.calculate(request)

        # Degradation rate should be close to zero
        assert abs(result.degradation_rate_percent) < 0.5  # Less than 0.5%/year

    def test_comparison_robust_vs_ols(self):
        """Compare robust regression vs OLS with outliers."""
        # Create data with outliers
        degradation_rate = -0.005
        start_date = datetime(2020, 1, 1)
        data_points = []

        for month in range(36):
            timestamp = start_date + timedelta(days=30 * month)
            years = month / 12
            normalized_output = 1.0 + (degradation_rate * years)

            # Add severe outliers
            if month in [5, 15, 25]:
                normalized_output *= 0.6

            data_points.append(DegradationDataPoint(
                timestamp=timestamp,
                normalized_output=normalized_output
            ))

        # Test with robust regression
        request_robust = DegradationRateRequest(
            data_points=data_points,
            system_capacity_kw=4.0,
            use_robust_regression=True
        )

        calculator = DegradationRateCalculator()
        result_robust = calculator.calculate(request_robust)

        # Test with OLS
        request_ols = DegradationRateRequest(
            data_points=data_points,
            system_capacity_kw=4.0,
            use_robust_regression=False
        )

        result_ols = calculator.calculate(request_ols)

        # Robust should be closer to true degradation rate
        true_rate_percent = degradation_rate * 100
        error_robust = abs(result_robust.degradation_rate_percent - true_rate_percent)
        error_ols = abs(result_ols.degradation_rate_percent - true_rate_percent)

        # Robust regression should have lower error with outliers
        assert error_robust <= error_ols * 1.5  # Allow some margin
