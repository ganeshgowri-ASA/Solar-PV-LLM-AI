"""
Pydantic models for API request/response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class LocationInput(BaseModel):
    """Location coordinates for PV calculations."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")


class SystemParameters(BaseModel):
    """PV System parameters."""
    system_capacity: float = Field(..., gt=0, description="System capacity in kW (DC)")
    module_type: int = Field(default=0, ge=0, le=2, description="Module type: 0=Standard, 1=Premium, 2=Thin film")
    array_type: int = Field(default=0, ge=0, le=4, description="Array type: 0=Fixed, 1=1-axis, 2=1-axis backtracking, 3=2-axis, 4=Azimuth axis")
    tilt: float = Field(default=20, ge=0, le=90, description="Tilt angle in degrees")
    azimuth: float = Field(default=180, ge=0, le=360, description="Azimuth angle in degrees (180=South in N. hemisphere)")
    losses: float = Field(default=14.08, ge=0, le=99, description="System losses in %")
    albedo: float = Field(default=0.2, ge=0, le=1, description="Ground reflectance (albedo)")


class EnergyYieldRequest(BaseModel):
    """Request model for Energy Yield Calculator."""
    location: LocationInput
    system: SystemParameters
    year: Optional[int] = Field(default=None, description="Year for TMY data (optional)")


class UncertaintyMetrics(BaseModel):
    """Statistical uncertainty and confidence intervals."""
    standard_error: float = Field(..., description="Standard error of estimate")
    confidence_level: float = Field(default=0.95, description="Confidence level (e.g., 0.95 for 95%)")
    confidence_interval_lower: float = Field(..., description="Lower bound of confidence interval")
    confidence_interval_upper: float = Field(..., description="Upper bound of confidence interval")
    r_squared: Optional[float] = Field(default=None, description="R-squared value (coefficient of determination)")
    relative_uncertainty: float = Field(..., description="Relative uncertainty as percentage")


class MonthlyEnergy(BaseModel):
    """Monthly energy production data."""
    month: int = Field(..., ge=1, le=12)
    energy_kwh: float = Field(..., description="Energy production in kWh")
    solar_radiation: float = Field(..., description="Solar radiation in kWh/m²/day")
    capacity_factor: float = Field(..., description="Capacity factor (0-1)")


class EnergyYieldResponse(BaseModel):
    """Response model for Energy Yield Calculator."""
    annual_energy_kwh: float = Field(..., description="Annual energy production in kWh")
    monthly_energy: List[MonthlyEnergy] = Field(..., description="Monthly breakdown")
    capacity_factor: float = Field(..., description="Annual capacity factor")
    specific_yield: float = Field(..., description="Specific yield in kWh/kWp/year")
    performance_ratio: float = Field(..., description="Performance ratio (0-1)")
    uncertainty: UncertaintyMetrics = Field(..., description="Uncertainty metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DegradationDataPoint(BaseModel):
    """Single data point for degradation analysis."""
    timestamp: datetime = Field(..., description="Measurement timestamp")
    normalized_output: float = Field(..., description="Normalized output (relative to initial)")

    @field_validator('normalized_output')
    @classmethod
    def validate_normalized_output(cls, v):
        if v <= 0 or v > 1.5:  # Allow some margin for measurement errors
            raise ValueError('Normalized output must be between 0 and 1.5')
        return v


class DegradationRateRequest(BaseModel):
    """Request model for Degradation Rate Calculator."""
    data_points: List[DegradationDataPoint] = Field(..., min_length=12, description="Time series data (minimum 12 points)")
    system_capacity_kw: float = Field(..., gt=0, description="System capacity in kW")
    installation_date: Optional[datetime] = Field(default=None, description="System installation date")
    use_robust_regression: bool = Field(default=True, description="Use robust regression to handle outliers")


class DegradationRateResponse(BaseModel):
    """Response model for Degradation Rate Calculator."""
    degradation_rate_per_year: float = Field(..., description="Annual degradation rate (e.g., -0.005 = -0.5%/year)")
    degradation_rate_percent: float = Field(..., description="Annual degradation rate as percentage")
    expected_lifetime_years: float = Field(..., description="Expected lifetime to 80% capacity")
    uncertainty: UncertaintyMetrics = Field(..., description="Statistical uncertainty metrics")
    data_quality_score: float = Field(..., ge=0, le=1, description="Data quality score (0-1)")
    outliers_detected: int = Field(..., description="Number of outliers detected and excluded")
    analysis_period_years: float = Field(..., description="Length of analysis period in years")
    projected_output_year_25: float = Field(..., description="Projected output at year 25 (relative to initial)")


class SpectralMismatchRequest(BaseModel):
    """Request model for Spectral Mismatch Calculator."""
    wavelengths: List[float] = Field(..., min_length=10, description="Wavelength array in nm")
    incident_spectrum: List[float] = Field(..., min_length=10, description="Incident spectral irradiance (W/m²/nm)")
    reference_spectrum: List[float] = Field(..., min_length=10, description="Reference spectral irradiance (W/m²/nm)")
    cell_spectral_response: List[float] = Field(..., min_length=10, description="Cell spectral response (A/W)")
    reference_cell_response: Optional[List[float]] = Field(default=None, description="Reference cell spectral response (A/W)")

    @field_validator('incident_spectrum', 'reference_spectrum', 'cell_spectral_response', 'reference_cell_response')
    @classmethod
    def validate_same_length(cls, v, info):
        if v is None:
            return v
        wavelengths_len = len(info.data.get('wavelengths', []))
        if len(v) != wavelengths_len:
            raise ValueError(f'All spectral arrays must have the same length as wavelengths')
        return v


class SpectralMismatchResponse(BaseModel):
    """Response model for Spectral Mismatch Calculator."""
    mismatch_factor: float = Field(..., description="Spectral mismatch factor M (dimensionless)")
    corrected_irradiance: float = Field(..., description="Spectral mismatch corrected irradiance (W/m²)")
    uncorrected_irradiance: float = Field(..., description="Broadband irradiance without correction (W/m²)")
    correction_percentage: float = Field(..., description="Correction as percentage")
    uncertainty: UncertaintyMetrics = Field(..., description="Uncertainty in mismatch factor")
    iec_compliant: bool = Field(..., description="Whether calculation follows IEC 60904-7")
    wavelength_range: tuple[float, float] = Field(..., description="Wavelength range used (min, max) in nm")
    integration_method: str = Field(default="trapezoidal", description="Numerical integration method used")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current timestamp")
    nrel_api_available: bool = Field(..., description="NREL API availability")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
