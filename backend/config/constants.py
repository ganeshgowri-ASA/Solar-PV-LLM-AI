"""
Constants for PV calculations and system parameters.
"""

# Physical Constants
BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
ELEMENTARY_CHARGE = 1.602176634e-19  # C
PLANCK_CONSTANT = 6.62607015e-34  # J⋅s
SPEED_OF_LIGHT = 299792458  # m/s
STANDARD_TEST_CONDITIONS_IRRADIANCE = 1000  # W/m²
STANDARD_TEST_CONDITIONS_TEMPERATURE = 25  # °C
AIR_MASS_STANDARD = 1.5  # AM1.5

# PV System Defaults
DEFAULT_ALBEDO = 0.2  # Ground reflectance
DEFAULT_TILT_LATITUDE = True  # Use latitude as tilt angle if not specified
DEFAULT_AZIMUTH_NORTHERN = 180  # South-facing for Northern hemisphere
DEFAULT_AZIMUTH_SOUTHERN = 0  # North-facing for Southern hemisphere

# Degradation Defaults
TYPICAL_DEGRADATION_RATE = 0.005  # 0.5% per year (typical crystalline silicon)
MIN_DEGRADATION_RATE = 0.003  # 0.3% per year
MAX_DEGRADATION_RATE = 0.015  # 1.5% per year

# Confidence Intervals
CONFIDENCE_LEVEL_95 = 0.95
CONFIDENCE_LEVEL_90 = 0.90
CONFIDENCE_LEVEL_68 = 0.68

# API Endpoints
PVWATTS_V6_ENDPOINT = "/pvwatts/v6.json"
PVWATTS_V8_ENDPOINT = "/pvwatts/v8.json"
SOLAR_RESOURCE_ENDPOINT = "/solar/solar_resource/v1.json"

# System Losses (%)
DEFAULT_SYSTEM_LOSSES = 14.08  # PVWatts default total system losses

# Module Temperature Model Parameters
SAPM_OPEN_RACK_GLASS_GLASS = {
    'a': -3.47,
    'b': -0.0594,
    'deltaT': 3
}

SAPM_CLOSE_MOUNT_GLASS_GLASS = {
    'a': -2.98,
    'b': -0.0471,
    'deltaT': 1
}

SAPM_INSULATED_BACK_GLASS_POLYMER = {
    'a': -2.81,
    'b': -0.0455,
    'deltaT': 0
}

# Spectral Mismatch Reference Conditions (IEC 60904-7)
IEC_60904_7_REFERENCE_SPECTRUM = "AM1.5G"
IEC_60904_7_REFERENCE_IRRADIANCE = 1000  # W/m²
IEC_60904_7_WAVELENGTH_RANGE = (280, 4000)  # nm

# Error Messages
ERROR_INVALID_COORDINATES = "Invalid coordinates: latitude must be between -90 and 90, longitude between -180 and 180"
ERROR_INVALID_SYSTEM_CAPACITY = "Invalid system capacity: must be greater than 0"
ERROR_INVALID_TILT = "Invalid tilt angle: must be between 0 and 90 degrees"
ERROR_INVALID_AZIMUTH = "Invalid azimuth: must be between 0 and 360 degrees"
ERROR_INSUFFICIENT_DATA = "Insufficient data points for calculation"
ERROR_NREL_API = "Error communicating with NREL API"

# Data Quality Thresholds
MIN_DATA_POINTS_DEGRADATION = 12  # Minimum monthly data points for degradation analysis
MIN_R_SQUARED_DEGRADATION = 0.5  # Minimum R² for acceptable degradation fit
MAX_UNCERTAINTY_THRESHOLD = 0.3  # Maximum acceptable relative uncertainty (30%)
