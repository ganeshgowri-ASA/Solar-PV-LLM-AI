"""
Mock Service Bridge Module
Bridges mock API calls to the real api_client for Solar PV LLM system.

This module provides backward compatibility for pages that expect a mock API interface
while routing calls to the actual API client implementation.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add frontend to path for api_client import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'frontend'))

try:
    from api_client import get_client, ExpertiseLevel
except ImportError:
    # Fallback if api_client is not available
    get_client = None
    ExpertiseLevel = None

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class MockAPI:
    """
    Mock API bridge that maps mock service calls to the real API client.
    Provides consistent interface for dashboard, chat, search, and calculator pages.
    """

    def __init__(self):
        """Initialize MockAPI with real client if available"""
        self.client = get_client() if get_client else None
        self._expertise_level = ExpertiseLevel.INTERMEDIATE if ExpertiseLevel else None

    def chat_completion(self, query: str, include_sources: bool = True) -> dict:
        """
        Bridge chat_completion to real API.

        Args:
            query: User's question
            include_sources: Whether to include citation sources

        Returns:
            Dict with content and sources
        """
        try:
            if self.client and self._expertise_level:
                response = self.client.chat_query(query, self._expertise_level, None)
                if response.success:
                    data = response.data
                    return {
                        "content": data.get("response", "Sorry, I couldn't generate a response."),
                        "sources": self._format_citations(data.get("citations", [])) if include_sources else []
                    }
                else:
                    return {"content": f"Error: {response.error}", "sources": []}
            else:
                # Fallback mock response
                return self._get_fallback_response(query, include_sources)
        except Exception as e:
            return {"content": f"Error: {str(e)}", "sources": []}

    def _format_citations(self, citations: list) -> list:
        """
        Format citations for mock service interface.

        Args:
            citations: Raw citations from API

        Returns:
            Formatted citation list
        """
        formatted = []
        for cite in citations:
            formatted.append({
                "title": cite.get('source', 'Unknown'),
                "excerpt": cite.get('text', ''),
                "page": cite.get('page', 1),
                "section": cite.get('section', 'General'),
                "relevance_score": cite.get('score', 0.85)
            })
        return formatted

    def _get_fallback_response(self, query: str, include_sources: bool) -> dict:
        """Provide fallback response when client is unavailable"""
        return {
            "content": "Solar photovoltaic systems convert sunlight into electricity using "
                      "semiconductor materials. This technology is widely used for renewable "
                      "energy generation in residential, commercial, and utility-scale applications.",
            "sources": [
                {
                    "title": "Solar PV Fundamentals",
                    "excerpt": "Basic principles of photovoltaic energy conversion",
                    "page": 1,
                    "section": "Introduction",
                    "relevance_score": 0.90
                }
            ] if include_sources else []
        }

    def get_dashboard_metrics(self) -> dict:
        """
        Return dashboard metrics for system monitoring.

        Returns:
            Dict with system health, usage stats, knowledge base info, and recent activity
        """
        return {
            "system_health": {
                "status": "Healthy",
                "uptime_percentage": 99.7,
                "active_queries": random.randint(5, 25),
                "response_time_ms": random.randint(180, 280)
            },
            "usage_stats": {
                "total_queries": random.randint(8000, 12000),
                "successful_queries": random.randint(7500, 11500),
                "failed_queries": random.randint(50, 150),
                "avg_response_time": random.randint(200, 300)
            },
            "knowledge_base": {
                "total_documents": 1247,
                "indexed_standards": 89,
                "index_size_mb": 456,
                "last_updated": datetime.now().isoformat()
            },
            "recent_activity": [
                {
                    "type": "Chat Query",
                    "status": "success",
                    "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                    "duration_ms": random.randint(150, 350)
                } for i in range(10)
            ]
        }

    def get_time_series_data(self, days: int = 30):
        """
        Return time series data for charts.

        Args:
            days: Number of days of historical data

        Returns:
            DataFrame with date, queries, response_time, and success_rate columns
        """
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

        data = {
            "date": list(reversed(dates)),
            "queries": [random.randint(200, 500) for _ in range(days)],
            "response_time": [random.randint(180, 320) for _ in range(days)],
            "success_rate": [round(random.uniform(94, 99), 2) for _ in range(days)]
        }

        if HAS_PANDAS:
            return pd.DataFrame(data)
        else:
            # Return dict if pandas not available
            return data

    def get_hourly_distribution(self) -> dict:
        """
        Return hourly query distribution data.

        Returns:
            Dict with hours and query counts
        """
        return {
            "hours": list(range(24)),
            "queries": [
                random.randint(5, 15),   # 0:00
                random.randint(3, 10),   # 1:00
                random.randint(2, 8),    # 2:00
                random.randint(2, 6),    # 3:00
                random.randint(3, 8),    # 4:00
                random.randint(5, 15),   # 5:00
                random.randint(10, 25),  # 6:00
                random.randint(20, 40),  # 7:00
                random.randint(35, 60),  # 8:00
                random.randint(50, 80),  # 9:00
                random.randint(60, 90),  # 10:00
                random.randint(55, 85),  # 11:00
                random.randint(45, 70),  # 12:00
                random.randint(50, 75),  # 13:00
                random.randint(55, 80),  # 14:00
                random.randint(50, 75),  # 15:00
                random.randint(40, 65),  # 16:00
                random.randint(35, 55),  # 17:00
                random.randint(25, 45),  # 18:00
                random.randint(20, 35),  # 19:00
                random.randint(15, 30),  # 20:00
                random.randint(12, 25),  # 21:00
                random.randint(10, 20),  # 22:00
                random.randint(8, 18),   # 23:00
            ]
        }

    def search_standards(self, query: str, filters: dict = None) -> dict:
        """
        Search standards library.

        Args:
            query: Search query
            filters: Optional filters (standard_type, year_range, etc.)

        Returns:
            Dict with search results
        """
        try:
            if self.client:
                standard_types = filters.get("standard_types") if filters else None
                response = self.client.search_standards(query, standard_types)
                if response.success:
                    return response.data

            # Fallback mock standards
            return {
                "standards": [
                    {
                        "id": "IEC 61215-1",
                        "title": "Terrestrial PV Modules - Design Qualification Part 1",
                        "type": "IEC",
                        "description": "General requirements for crystalline silicon PV modules",
                        "year": 2021,
                        "relevance": 0.95
                    },
                    {
                        "id": "IEC 61730-1",
                        "title": "PV Module Safety Qualification Part 1",
                        "type": "IEC",
                        "description": "Requirements for construction of PV modules",
                        "year": 2016,
                        "relevance": 0.88
                    },
                    {
                        "id": "IEEE 1547-2018",
                        "title": "Interconnection and Interoperability of DER",
                        "type": "IEEE",
                        "description": "Standard for distributed energy resources interconnection",
                        "year": 2018,
                        "relevance": 0.82
                    }
                ],
                "total": 3
            }
        except Exception as e:
            return {"standards": [], "total": 0, "error": str(e)}

    def calculate_system(self, params: dict) -> dict:
        """
        Calculate solar system sizing.

        Args:
            params: Calculation parameters (consumption, location, panel_wattage, etc.)

        Returns:
            Dict with system sizing recommendations
        """
        try:
            if self.client:
                response = self.client.calculate_system_size(
                    annual_consumption_kwh=params.get("annual_consumption", 10000),
                    location_factor=params.get("location_factor", 1.0),
                    panel_wattage=params.get("panel_wattage", 400),
                    system_losses=params.get("system_losses", 0.14)
                )
                if response.success:
                    return response.data

            # Fallback calculation
            consumption = params.get("annual_consumption", 10000)
            panel_wattage = params.get("panel_wattage", 400)
            location_factor = params.get("location_factor", 1.0)

            # Simple calculation
            peak_sun_hours = 4.5 * location_factor
            system_size_kw = consumption / (peak_sun_hours * 365 * 0.86)
            num_panels = int((system_size_kw * 1000) / panel_wattage) + 1

            return {
                "recommended_size_kw": round(system_size_kw, 2),
                "actual_size_kw": round((num_panels * panel_wattage) / 1000, 2),
                "num_panels": num_panels,
                "panel_wattage": panel_wattage,
                "estimated_annual_production_kwh": round(consumption * 1.05, 0),
                "coverage_percentage": 105.0
            }
        except Exception as e:
            return {"error": str(e)}

    def analyze_image(self, image_data: bytes, analysis_type: str = "general") -> dict:
        """
        Analyze solar panel image (placeholder for Roboflow integration).

        Args:
            image_data: Image bytes
            analysis_type: Type of analysis (general, defect, thermal, el)

        Returns:
            Dict with analysis results
        """
        # Placeholder - actual implementation will use Roboflow
        return {
            "status": "pending_integration",
            "message": "Image analysis via Roboflow integration coming soon",
            "analysis_type": analysis_type,
            "placeholder_results": {
                "detected_panels": 0,
                "defects_found": [],
                "confidence": 0.0,
                "recommendations": [
                    "Roboflow VI/EL/IR analysis integration in progress"
                ]
            }
        }

    def get_category_breakdown(self) -> dict:
        """
        Return query category breakdown for analytics.

        Returns:
            Dict with category names and percentages
        """
        return {
            "categories": [
                {"name": "Installation", "percentage": 28, "count": 2800},
                {"name": "Efficiency", "percentage": 22, "count": 2200},
                {"name": "Standards", "percentage": 18, "count": 1800},
                {"name": "Troubleshooting", "percentage": 15, "count": 1500},
                {"name": "Design", "percentage": 12, "count": 1200},
                {"name": "Other", "percentage": 5, "count": 500}
            ]
        }

    def get_expertise_distribution(self) -> dict:
        """
        Return user expertise level distribution.

        Returns:
            Dict with expertise levels and counts
        """
        return {
            "levels": [
                {"level": "Beginner", "count": 3500, "percentage": 35},
                {"level": "Intermediate", "count": 4500, "percentage": 45},
                {"level": "Expert", "count": 2000, "percentage": 20}
            ]
        }


# Singleton instance for module-level access
mock_api = MockAPI()


# Convenience functions for direct import
def chat_completion(query: str, include_sources: bool = True) -> dict:
    """Wrapper for mock_api.chat_completion"""
    return mock_api.chat_completion(query, include_sources)


def get_dashboard_metrics() -> dict:
    """Wrapper for mock_api.get_dashboard_metrics"""
    return mock_api.get_dashboard_metrics()


def get_time_series_data(days: int = 30):
    """Wrapper for mock_api.get_time_series_data"""
    return mock_api.get_time_series_data(days)


def search_standards(query: str, filters: dict = None) -> dict:
    """Wrapper for mock_api.search_standards"""
    return mock_api.search_standards(query, filters)


def calculate_system(params: dict) -> dict:
    """Wrapper for mock_api.calculate_system"""
    return mock_api.calculate_system(params)


def analyze_image(image_data: bytes, analysis_type: str = "general") -> dict:
    """Wrapper for mock_api.analyze_image"""
    return mock_api.analyze_image(image_data, analysis_type)
