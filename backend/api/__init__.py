"""
Solar PV LLM AI - API Module
Contains mock_service bridge and API endpoints.
"""

from .mock_service import (
    MockAPI,
    mock_api,
    chat_completion,
    get_dashboard_metrics,
    get_time_series_data,
    search_standards,
    calculate_system,
    analyze_image,
)

__all__ = [
    "MockAPI",
    "mock_api",
    "chat_completion",
    "get_dashboard_metrics",
    "get_time_series_data",
    "search_standards",
    "calculate_system",
    "analyze_image",
]
