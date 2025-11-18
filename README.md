# Solar PV LLM AI System

> **Photovoltaic domain calculators with NREL API integration, uncertainty quantification, and standards-compliant calculations**

A comprehensive REST API system for solar photovoltaic calculations, featuring energy yield estimation, degradation analysis, and spectral mismatch correction. Built with FastAPI and integrated with NREL solar resource data.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

### 🌞 PV Domain Calculators

1. **Energy Yield Calculator**
   - Wraps NREL PVWatts v6 API for annual and monthly energy production estimates
   - Location-based solar resource data (TMY weather files)
   - System performance metrics: capacity factor, specific yield, performance ratio
   - Comprehensive uncertainty quantification with 95% confidence intervals

2. **Degradation Rate Calculator**
   - Statistical linear regression analysis of PV system performance over time
   - Robust regression with automatic outlier detection (Huber regression)
   - Calculates annual degradation rate with confidence intervals
   - Projects system lifetime and performance at year 25
   - Data quality scoring

3. **Spectral Mismatch Correction Calculator**
   - IEC 60904-7 compliant spectral mismatch factor calculation
   - Corrects for differences between test and reference spectral conditions
   - Supports custom spectral irradiance and cell response data
   - Trapezoidal integration for accurate spectral calculations
   - IEC compliance verification

### 🎯 Key Capabilities

- **Standards Compliant**: IEC 60904-7 for spectral mismatch calculations
- **Uncertainty Quantification**: All calculators include statistical uncertainty analysis
- **Robust Methods**: Outlier detection and handling in degradation analysis
- **NREL Integration**: Direct integration with NREL solar resource APIs
- **Modular Design**: Each calculator can be used independently or combined
- **Interactive Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Comprehensive Testing**: Unit and integration tests with >90% coverage

## Quick Start

### Prerequisites

- Python 3.10 or higher
- NREL API key (free from [https://developer.nrel.gov/signup/](https://developer.nrel.gov/signup/))

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

2. **Create and activate virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp .env.example .env
# Edit .env and add your NREL API key
```

5. **Run the server**

```bash
python backend/main.py
```

The API will be available at `http://localhost:8000`

### Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Interactive documentation
open http://localhost:8000/docs
```

## API Usage

### Energy Yield Calculation

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/calculators/energy-yield",
    json={
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
            "losses": 14.08
        }
    }
)

data = response.json()
print(f"Annual Energy: {data['annual_energy_kwh']:.2f} kWh/year")
print(f"Capacity Factor: {data['capacity_factor']:.1%}")
```

### Degradation Rate Analysis

```python
from datetime import datetime, timedelta
import requests

# Generate sample data
start_date = datetime(2020, 1, 1)
data_points = [
    {
        "timestamp": (start_date + timedelta(days=30*i)).isoformat(),
        "normalized_output": 1.0 - (0.005 * i / 12)  # -0.5%/year degradation
    }
    for i in range(36)  # 3 years of monthly data
]

response = requests.post(
    "http://localhost:8000/api/v1/calculators/degradation-rate",
    json={
        "data_points": data_points,
        "system_capacity_kw": 4.0,
        "use_robust_regression": True
    }
)

data = response.json()
print(f"Degradation: {data['degradation_rate_percent']:.3f}%/year")
print(f"Lifetime (to 80%): {data['expected_lifetime_years']:.1f} years")
```

### Spectral Mismatch Correction

```python
import numpy as np
import requests

# Create sample spectral data
wavelengths = np.linspace(300, 1200, 100)
reference_spectrum = np.exp(-((wavelengths - 500) / 300) ** 2) * 1.5
incident_spectrum = np.exp(-((wavelengths - 450) / 250) ** 2) * 1.5
cell_response = np.exp(-((wavelengths - 900) / 200) ** 2) * 0.8

response = requests.post(
    "http://localhost:8000/api/v1/calculators/spectral-mismatch",
    json={
        "wavelengths": wavelengths.tolist(),
        "incident_spectrum": incident_spectrum.tolist(),
        "reference_spectrum": reference_spectrum.tolist(),
        "cell_spectral_response": cell_response.tolist()
    }
)

data = response.json()
print(f"Mismatch Factor: {data['mismatch_factor']:.4f}")
print(f"Correction: {data['correction_percentage']:+.2f}%")
```

For more examples, see [API Usage Guide](docs/API_USAGE.md)

## Documentation

- **[API Usage Guide](docs/API_USAGE.md)**: Detailed API usage with examples
- **[Interactive Docs](http://localhost:8000/docs)**: Swagger UI (after starting server)
- **[ReDoc](http://localhost:8000/redoc)**: Alternative API documentation

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/test_energy_yield.py

# Run integration tests only
pytest tests/integration/
```

## Project Structure

```
Solar-PV-LLM-AI/
├── backend/
│   ├── api/
│   │   └── routes/
│   │       └── calculators.py      # API endpoints
│   ├── calculators/
│   │   ├── energy_yield.py         # Energy Yield Calculator
│   │   ├── degradation_rate.py     # Degradation Rate Calculator
│   │   └── spectral_mismatch.py    # Spectral Mismatch Calculator
│   ├── config/
│   │   ├── settings.py             # App configuration
│   │   └── constants.py            # PV constants
│   ├── models/
│   │   └── schemas.py              # Pydantic models
│   ├── services/
│   │   └── nrel_client.py          # NREL API client
│   └── main.py                     # FastAPI application
├── tests/
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   └── conftest.py                 # Pytest fixtures
├── docs/
│   └── API_USAGE.md               # API documentation
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md
```

## Technology Stack

- **Framework**: FastAPI 0.109
- **PV Libraries**: pvlib-python, NREL-PySAM
- **Scientific Computing**: NumPy, SciPy, pandas, scikit-learn
- **Statistics**: statsmodels
- **Testing**: pytest, pytest-cov
- **API Client**: requests, httpx
- **Logging**: loguru
- **Validation**: Pydantic

## NREL API Integration

This system integrates with NREL (National Renewable Energy Laboratory) APIs:

- **PVWatts v6**: Energy production estimates from weather data
- **Solar Resource Data**: TMY (Typical Meteorological Year) datasets

### Getting an API Key

1. Visit [https://developer.nrel.gov/signup/](https://developer.nrel.gov/signup/)
2. Sign up for a free account
3. Obtain your API key
4. Add to `.env` file: `NREL_API_KEY=your_key_here`

**Note**: You can use `DEMO_KEY` for testing, but it has rate limits.

## Calculators Overview

### Energy Yield Calculator

**Purpose**: Estimate annual and monthly energy production for a PV system

**Key Features**:
- Location-based TMY weather data via NREL PVWatts
- Monthly and annual energy production (kWh)
- Capacity factor, specific yield, performance ratio
- Uncertainty quantification (typically ±10-15%)
- 95% confidence intervals

**Typical Use Cases**:
- System design and sizing
- Financial analysis and ROI calculations
- Site assessment
- Performance verification

### Degradation Rate Calculator

**Purpose**: Calculate annual degradation rate from time series performance data

**Key Features**:
- Robust linear regression (Huber regressor)
- Automatic outlier detection and exclusion
- Statistical uncertainty analysis
- Expected lifetime to 80% capacity
- Data quality scoring
- Projection to year 25

**Typical Use Cases**:
- Long-term performance monitoring
- Warranty compliance verification
- Asset valuation
- O&M planning

### Spectral Mismatch Calculator

**Purpose**: Calculate spectral mismatch correction factor per IEC 60904-7

**Key Features**:
- IEC 60904-7 compliant calculation
- Supports custom spectral data
- Trapezoidal integration
- Uncertainty quantification
- Compliance verification

**Typical Use Cases**:
- Laboratory PV device testing
- Calibration of reference cells
- Research and development
- Standards compliance

## Uncertainty Quantification

All calculators provide comprehensive uncertainty metrics:

- **Standard Error**: Absolute uncertainty in estimate
- **Confidence Intervals**: 95% confidence bounds
- **R-squared**: Goodness of fit (where applicable)
- **Relative Uncertainty**: Percentage uncertainty

Example uncertainty response:
```json
{
  "standard_error": 716.13,
  "confidence_level": 0.95,
  "confidence_interval_lower": 5116.8,
  "confidence_interval_upper": 7922.0,
  "r_squared": 0.95,
  "relative_uncertainty": 10.99
}
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Roadmap

- [ ] Additional PV calculators (shading analysis, thermal modeling)
- [ ] LLM integration for natural language queries
- [ ] RAG (Retrieval-Augmented Generation) for PV knowledge base
- [ ] Real-time monitoring integration
- [ ] Enhanced visualization and reporting
- [ ] Multi-language support
- [ ] Docker containerization
- [ ] Cloud deployment guides (AWS, Azure, GCP)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NREL** for providing comprehensive solar resource APIs
- **pvlib-python** community for excellent PV modeling tools
- **FastAPI** for the modern, fast web framework
- IEC standards committee for spectral mismatch calculation standards

## Support

- **Issues**: [GitHub Issues](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues)
- **Documentation**: [API Usage Guide](docs/API_USAGE.md)
- **NREL API Docs**: [https://developer.nrel.gov/docs/](https://developer.nrel.gov/docs/)

## Citation

If you use this software in your research, please cite:

```bibtex
@software{solar_pv_llm_ai,
  title = {Solar PV LLM AI System},
  author = {Ganesh Gowri},
  year = {2024},
  url = {https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI}
}
```

---

**Built with ☀️ for the solar energy community**
