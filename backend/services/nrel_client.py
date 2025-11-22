"""
NREL API Client for PVWatts and solar resource data.
"""
import requests
from typing import Dict, Any, Optional
from loguru import logger

from backend.config.settings import settings
from backend.config.constants import (
    PVWATTS_V6_ENDPOINT,
    ERROR_NREL_API,
    ERROR_INVALID_COORDINATES
)


class NRELAPIError(Exception):
    """Custom exception for NREL API errors."""
    pass


class NRELClient:
    """Client for interacting with NREL APIs."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NREL API client.

        Args:
            api_key: NREL API key. If not provided, uses key from settings.
        """
        self.api_key = api_key or settings.nrel_api_key
        self.base_url = settings.nrel_api_base_url
        self.session = requests.Session()

    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Make a request to NREL API.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            method: HTTP method (GET or POST)

        Returns:
            JSON response from API

        Raises:
            NRELAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        params["api_key"] = self.api_key

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=30)
            else:
                response = self.session.post(url, json=params, timeout=30)

            response.raise_for_status()
            data = response.json()

            # Check for API errors in response
            if "errors" in data and data["errors"]:
                error_msg = data["errors"][0] if isinstance(data["errors"], list) else str(data["errors"])
                raise NRELAPIError(f"NREL API Error: {error_msg}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"NREL API request failed: {e}")
            raise NRELAPIError(f"{ERROR_NREL_API}: {str(e)}")
        except ValueError as e:
            logger.error(f"Failed to parse NREL API response: {e}")
            raise NRELAPIError(f"Invalid response from NREL API: {str(e)}")

    def get_pvwatts_data(
        self,
        latitude: float,
        longitude: float,
        system_capacity: float,
        module_type: int = 0,
        array_type: int = 0,
        tilt: float = 20,
        azimuth: float = 180,
        losses: float = 14.08,
        albedo: float = 0.2,
        dataset: str = "nsrdb"
    ) -> Dict[str, Any]:
        """
        Get PV performance data from PVWatts API.

        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            system_capacity: System capacity in kW (DC)
            module_type: Module type (0=Standard, 1=Premium, 2=Thin film)
            array_type: Array type (0=Fixed, 1=1-axis, etc.)
            tilt: Tilt angle in degrees (0-90)
            azimuth: Azimuth angle in degrees (0-360)
            losses: System losses in % (0-99)
            albedo: Ground reflectance (0-1)
            dataset: Weather dataset ('nsrdb' or 'tmy3')

        Returns:
            PVWatts API response data

        Raises:
            NRELAPIError: If API request fails
            ValueError: If parameters are invalid
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError(ERROR_INVALID_COORDINATES)

        params = {
            "lat": latitude,
            "lon": longitude,
            "system_capacity": system_capacity,
            "module_type": module_type,
            "array_type": array_type,
            "tilt": tilt,
            "azimuth": azimuth,
            "losses": losses,
            "albedo": albedo,
            "dataset": dataset
        }

        logger.info(f"Requesting PVWatts data for location ({latitude}, {longitude})")
        response = self._make_request(PVWATTS_V6_ENDPOINT, params)

        return response

    def check_api_availability(self) -> bool:
        """
        Check if NREL API is available.

        Returns:
            True if API is available, False otherwise
        """
        try:
            # Simple test request to verify API access
            params = {
                "lat": 40,
                "lon": -105,
                "system_capacity": 4,
                "module_type": 0,
                "array_type": 0,
                "tilt": 20,
                "azimuth": 180,
                "losses": 14.08
            }
            self._make_request(PVWATTS_V6_ENDPOINT, params)
            return True
        except Exception as e:
            logger.warning(f"NREL API availability check failed: {e}")
            return False

    def get_solar_resource_data(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get solar resource data for a location.

        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees

        Returns:
            Solar resource data

        Raises:
            NRELAPIError: If API request fails
        """
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError(ERROR_INVALID_COORDINATES)

        params = {
            "lat": latitude,
            "lon": longitude
        }

        logger.info(f"Requesting solar resource data for ({latitude}, {longitude})")
        response = self._make_request("/solar/solar_resource/v1.json", params)

        return response

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global NREL client instance
nrel_client = NRELClient()
