# API Usage Guide

This guide provides detailed examples of how to use the Solar PV LLM AI System API calculators.

## Table of Contents

- [Getting Started](#getting-started)
- [Energy Yield Calculator](#energy-yield-calculator)
- [Degradation Rate Calculator](#degradation-rate-calculator)
- [Spectral Mismatch Calculator](#spectral-mismatch-calculator)
- [Error Handling](#error-handling)

## Getting Started

### Base URL

```
http://localhost:8000
```

### API Prefix

All calculator endpoints are prefixed with `/api/v1`

### Authentication

Currently no authentication required. NREL API key is configured server-side.

## Energy Yield Calculator

Calculate annual and monthly energy production for a PV system using NREL PVWatts API.

### Endpoint

```
POST /api/v1/calculators/energy-yield
```

### Request Example

```json
{
  "location": {
    "latitude": 40.0150,
    "longitude": -105.2705
  },
  "system": {
    "system_capacity": 4.0,
    "module_type": 0,
    "array_type": 0,
    "tilt": 20,
    "azimuth": 180,
    "losses": 14.08,
    "albedo": 0.2
  }
}
```

### Parameters

**Location:**
- `latitude`: -90 to 90 degrees
- `longitude`: -180 to 180 degrees

**System:**
- `system_capacity`: System capacity in kW (DC)
- `module_type`: 0=Standard, 1=Premium, 2=Thin film
- `array_type`: 0=Fixed, 1=1-axis, 2=1-axis backtracking, 3=2-axis, 4=Azimuth axis
- `tilt`: Tilt angle in degrees (0-90)
- `azimuth`: Azimuth angle in degrees (0-360, 180=South in N. hemisphere)
- `losses`: System losses in % (default: 14.08)
- `albedo`: Ground reflectance (default: 0.2)

### Response Example

```json
{
  "annual_energy_kwh": 6519.4,
  "monthly_energy": [
    {
      "month": 1,
      "energy_kwh": 443.2,
      "solar_radiation": 4.15,
      "capacity_factor": 0.148
    },
    ...
  ],
  "capacity_factor": 0.186,
  "specific_yield": 1629.85,
  "performance_ratio": 0.82,
  "uncertainty": {
    "standard_error": 716.13,
    "confidence_level": 0.95,
    "confidence_interval_lower": 5116.8,
    "confidence_interval_upper": 7922.0,
    "r_squared": 0.95,
    "relative_uncertainty": 10.99
  },
  "metadata": {
    "location": {
      "latitude": 40.0150,
      "longitude": -105.2705,
      "city": "Boulder",
      "state": "Colorado"
    },
    "data_source": "NREL PVWatts v6"
  }
}
```

### Python Example

```python
import requests

url = "http://localhost:8000/api/v1/calculators/energy-yield"

payload = {
    "location": {
        "latitude": 40.0150,
        "longitude": -105.2705
    },
    "system": {
        "system_capacity": 4.0,
        "module_type": 0,
        "array_type": 0,
        "tilt": 20,
        "azimuth": 180,
        "losses": 14.08,
        "albedo": 0.2
    }
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Annual Energy: {data['annual_energy_kwh']:.2f} kWh/year")
print(f"Capacity Factor: {data['capacity_factor']:.1%}")
print(f"Uncertainty (95% CI): ±{data['uncertainty']['relative_uncertainty']:.1f}%")
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/calculators/energy-yield" \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "latitude": 40.0150,
      "longitude": -105.2705
    },
    "system": {
      "system_capacity": 4.0,
      "module_type": 0,
      "array_type": 0,
      "tilt": 20,
      "azimuth": 180,
      "losses": 14.08,
      "albedo": 0.2
    }
  }'
```

## Degradation Rate Calculator

Analyze time series performance data to calculate annual degradation rate using robust statistical regression.

### Endpoint

```
POST /api/v1/calculators/degradation-rate
```

### Request Example

```json
{
  "data_points": [
    {
      "timestamp": "2020-01-01T00:00:00",
      "normalized_output": 1.0
    },
    {
      "timestamp": "2020-02-01T00:00:00",
      "normalized_output": 0.998
    },
    ...
  ],
  "system_capacity_kw": 4.0,
  "use_robust_regression": true
}
```

### Parameters

- `data_points`: Array of time series data (minimum 12 points)
  - `timestamp`: ISO 8601 datetime
  - `normalized_output`: Performance relative to initial (0-1.5)
- `system_capacity_kw`: System capacity in kW
- `installation_date`: (Optional) System installation date
- `use_robust_regression`: Use robust regression to handle outliers (default: true)

### Response Example

```json
{
  "degradation_rate_per_year": -0.0048,
  "degradation_rate_percent": -0.48,
  "expected_lifetime_years": 41.67,
  "uncertainty": {
    "standard_error": 0.0003,
    "confidence_level": 0.95,
    "confidence_interval_lower": -0.0054,
    "confidence_interval_upper": -0.0042,
    "r_squared": 0.94,
    "relative_uncertainty": 6.25
  },
  "data_quality_score": 0.88,
  "outliers_detected": 2,
  "analysis_period_years": 3.0,
  "projected_output_year_25": 0.88
}
```

### Python Example

```python
import requests
from datetime import datetime, timedelta

url = "http://localhost:8000/api/v1/calculators/degradation-rate"

# Generate 36 months of synthetic data
start_date = datetime(2020, 1, 1)
data_points = []

for month in range(36):
    timestamp = start_date + timedelta(days=30 * month)
    # Simulate -0.5%/year degradation
    normalized_output = 1.0 - (0.005 * month / 12)

    data_points.append({
        "timestamp": timestamp.isoformat(),
        "normalized_output": normalized_output
    })

payload = {
    "data_points": data_points,
    "system_capacity_kw": 4.0,
    "use_robust_regression": True
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Degradation Rate: {data['degradation_rate_percent']:.3f}%/year")
print(f"Expected Lifetime (to 80%): {data['expected_lifetime_years']:.1f} years")
print(f"Data Quality Score: {data['data_quality_score']:.2f}")
print(f"Output at Year 25: {data['projected_output_year_25']:.1%}")
```

## Spectral Mismatch Calculator

Calculate spectral mismatch correction factor according to IEC 60904-7 standard.

### Endpoint

```
POST /api/v1/calculators/spectral-mismatch
```

### Request Example

```json
{
  "wavelengths": [300, 310, 320, ..., 1190, 1200],
  "incident_spectrum": [0.1, 0.2, 0.3, ..., 0.8, 0.7],
  "reference_spectrum": [0.15, 0.25, 0.35, ..., 0.75, 0.65],
  "cell_spectral_response": [0.05, 0.1, 0.2, ..., 0.7, 0.6],
  "reference_cell_response": [0.05, 0.1, 0.2, ..., 0.7, 0.6]
}
```

### Parameters

- `wavelengths`: Array of wavelengths in nm (minimum 10 points, ascending order)
- `incident_spectrum`: Test spectral irradiance in W/m²/nm
- `reference_spectrum`: Reference spectral irradiance in W/m²/nm
- `cell_spectral_response`: Test cell spectral response in A/W
- `reference_cell_response`: (Optional) Reference cell spectral response in A/W

### Response Example

```json
{
  "mismatch_factor": 1.023,
  "corrected_irradiance": 1023.0,
  "uncorrected_irradiance": 1000.0,
  "correction_percentage": 2.3,
  "uncertainty": {
    "standard_error": 0.031,
    "confidence_level": 0.95,
    "confidence_interval_lower": 0.961,
    "confidence_interval_upper": 1.085,
    "r_squared": null,
    "relative_uncertainty": 3.03
  },
  "iec_compliant": true,
  "wavelength_range": [300, 1200],
  "integration_method": "trapezoidal"
}
```

### Python Example

```python
import requests
import numpy as np

url = "http://localhost:8000/api/v1/calculators/spectral-mismatch"

# Create sample spectral data
wavelengths = np.linspace(300, 1200, 100)

# Simplified AM1.5G spectrum
reference_spectrum = np.exp(-((wavelengths - 500) / 300) ** 2) * 1.5

# Test spectrum (cloudy sky - more blue)
incident_spectrum = np.exp(-((wavelengths - 450) / 250) ** 2) * 1.5

# Silicon cell response
cell_response = np.exp(-((wavelengths - 900) / 200) ** 2) * 0.8

payload = {
    "wavelengths": wavelengths.tolist(),
    "incident_spectrum": incident_spectrum.tolist(),
    "reference_spectrum": reference_spectrum.tolist(),
    "cell_spectral_response": cell_response.tolist()
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Mismatch Factor M: {data['mismatch_factor']:.4f}")
print(f"Correction: {data['correction_percentage']:+.2f}%")
print(f"IEC 60904-7 Compliant: {data['iec_compliant']}")
print(f"Corrected Irradiance: {data['corrected_irradiance']:.2f} W/m²")
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful calculation
- `400 Bad Request`: Invalid input parameters
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: External service (NREL API) unavailable

### Error Response Format

```json
{
  "error": "ValidationError",
  "message": "Insufficient data points for calculation",
  "details": {
    "minimum_required": 12,
    "provided": 8
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Python Error Handling Example

```python
import requests

url = "http://localhost:8000/api/v1/calculators/degradation-rate"

payload = {
    "data_points": [...],  # Your data
    "system_capacity_kw": 4.0
}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Raise exception for 4xx/5xx

    data = response.json()
    print(f"Success: {data}")

except requests.exceptions.HTTPError as e:
    error_data = e.response.json()
    print(f"Error: {error_data['message']}")

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

## Interactive Documentation

For interactive API documentation and testing, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces provide:
- Complete API schema
- Interactive request/response testing
- Example payloads
- Model schemas
- Authentication requirements
