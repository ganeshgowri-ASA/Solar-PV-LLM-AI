"""
API Client for Solar PV LLM AI Backend
Handles all HTTP requests with error handling, retries, and WebSocket support.
"""

import os
import json
import time
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any, List, Generator, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import queue

# Try to import websocket for streaming
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


class ExpertiseLevel(str, Enum):
    """User expertise level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class CalculationType(str, Enum):
    """Types of solar PV calculations."""
    SYSTEM_SIZE = "system_size"
    ENERGY_OUTPUT = "energy_output"
    ROI = "roi"
    PAYBACK_PERIOD = "payback_period"
    PANEL_COUNT = "panel_count"
    INVERTER_SIZE = "inverter_size"
    BATTERY_SIZE = "battery_size"


@dataclass
class APIResponse:
    """Wrapper for API responses."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


class SolarPVAPIClient:
    """
    Client for interacting with Solar PV LLM AI Backend.

    Features:
    - Automatic retries with exponential backoff
    - Connection pooling
    - Error handling
    - WebSocket support for streaming
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5
    ):
        """
        Initialize API client.

        Args:
            base_url: Backend API URL (default: from env or localhost:8000)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff factor
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.timeout = timeout

        # Configure session with retries
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters

        Returns:
            APIResponse with success status and data/error
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )

            # Check for HTTP errors
            response.raise_for_status()

            return APIResponse(
                success=True,
                data=response.json(),
                status_code=response.status_code
            )

        except requests.exceptions.Timeout:
            return APIResponse(
                success=False,
                error="Request timed out. Please try again.",
                status_code=408
            )
        except requests.exceptions.ConnectionError:
            return APIResponse(
                success=False,
                error="Cannot connect to server. Please check if the backend is running.",
                status_code=503
            )
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                error_msg = error_data.get("message", error_data.get("detail", str(e)))
            except:
                pass
            return APIResponse(
                success=False,
                error=error_msg,
                status_code=e.response.status_code if e.response else 500
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                status_code=500
            )

    # ============ Health Check ============

    def health_check(self) -> APIResponse:
        """Check if backend is healthy."""
        return self._make_request("GET", "/health")

    def is_healthy(self) -> bool:
        """Quick check if backend is available."""
        response = self.health_check()
        return response.success and response.data.get("status") == "healthy"

    # ============ Chat Endpoints ============

    def chat_query(
        self,
        query: str,
        expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        conversation_id: Optional[str] = None,
        include_citations: bool = True
    ) -> APIResponse:
        """
        Send a chat query to the AI assistant.

        Args:
            query: User's question
            expertise_level: User's expertise level
            conversation_id: Existing conversation ID
            include_citations: Include source citations

        Returns:
            APIResponse with AI response
        """
        data = {
            "query": query,
            "expertise_level": expertise_level.value if isinstance(expertise_level, ExpertiseLevel) else expertise_level,
            "conversation_id": conversation_id,
            "include_citations": include_citations,
            "stream": False
        }

        return self._make_request("POST", "/chat/query", data=data)

    def chat_stream(
        self,
        query: str,
        expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        conversation_id: Optional[str] = None,
        on_token: Optional[Callable[[str], None]] = None
    ) -> Generator[str, None, None]:
        """
        Stream chat response token by token.

        Args:
            query: User's question
            expertise_level: User's expertise level
            conversation_id: Existing conversation ID
            on_token: Callback for each token

        Yields:
            Response tokens
        """
        url = f"{self.base_url}/chat/query/stream"

        data = {
            "query": query,
            "expertise_level": expertise_level.value if isinstance(expertise_level, ExpertiseLevel) else expertise_level,
            "conversation_id": conversation_id,
            "include_citations": False,
            "stream": True
        }

        try:
            response = self.session.post(
                url,
                json=data,
                stream=True,
                timeout=60
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            token_data = json.loads(data_str)
                            if "token" in token_data:
                                token = token_data["token"]
                                if on_token:
                                    on_token(token)
                                yield token
                            elif "error" in token_data:
                                yield f"\n\nError: {token_data['error']}"
                                break
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            yield f"\n\nStreaming error: {str(e)}"

    # ============ WebSocket Chat ============

    def create_websocket_chat(
        self,
        conversation_id: str,
        on_message: Callable[[Dict[str, Any]], None],
        on_error: Optional[Callable[[str], None]] = None,
        on_close: Optional[Callable[[], None]] = None
    ) -> Optional['WebSocketChat']:
        """
        Create a WebSocket connection for real-time chat.

        Args:
            conversation_id: Unique conversation ID
            on_message: Callback for received messages
            on_error: Callback for errors
            on_close: Callback when connection closes

        Returns:
            WebSocketChat instance or None if WebSocket not available
        """
        if not WEBSOCKET_AVAILABLE:
            return None

        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/chat/ws/{conversation_id}"

        return WebSocketChat(
            url=ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

    # ============ Search Endpoints ============

    def search_standards(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        max_results: int = 10,
        include_summaries: bool = True
    ) -> APIResponse:
        """
        Search solar PV standards database.

        Args:
            query: Search query
            categories: Filter by categories
            max_results: Maximum results to return
            include_summaries: Include document summaries

        Returns:
            APIResponse with search results
        """
        data = {
            "query": query,
            "categories": categories,
            "max_results": max_results,
            "include_summaries": include_summaries
        }

        return self._make_request("POST", "/search/standards", data=data)

    def get_categories(self) -> APIResponse:
        """Get available standard categories."""
        return self._make_request("GET", "/search/categories")

    # ============ Calculator Endpoints ============

    def calculate(
        self,
        calculation_type: CalculationType,
        parameters: Dict[str, Any],
        location: Optional[str] = None,
        include_explanation: bool = True
    ) -> APIResponse:
        """
        Perform a solar PV calculation.

        Args:
            calculation_type: Type of calculation
            parameters: Calculation parameters
            location: Optional location for solar data
            include_explanation: Include explanation

        Returns:
            APIResponse with calculation results
        """
        data = {
            "calculation_type": calculation_type.value if isinstance(calculation_type, CalculationType) else calculation_type,
            "parameters": parameters,
            "location": location,
            "include_explanation": include_explanation
        }

        return self._make_request("POST", "/calculate", data=data)

    def get_calculation_types(self) -> APIResponse:
        """Get available calculation types."""
        return self._make_request("GET", "/calculate/types")

    # ============ Image Analysis Endpoints ============

    def analyze_image(
        self,
        image_data: bytes,
        analysis_type: str = "general",
        include_recommendations: bool = True
    ) -> APIResponse:
        """
        Analyze a solar PV image.

        Args:
            image_data: Raw image bytes
            analysis_type: Type of analysis
            include_recommendations: Include recommendations

        Returns:
            APIResponse with analysis results
        """
        # Encode image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        data = {
            "image_base64": image_base64,
            "analysis_type": analysis_type,
            "include_recommendations": include_recommendations
        }

        return self._make_request("POST", "/analyze/image", data=data)

    def analyze_image_file(
        self,
        file_path: str,
        analysis_type: str = "general",
        include_recommendations: bool = True
    ) -> APIResponse:
        """
        Analyze a solar PV image from file path.

        Args:
            file_path: Path to image file
            analysis_type: Type of analysis
            include_recommendations: Include recommendations

        Returns:
            APIResponse with analysis results
        """
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
            return self.analyze_image(image_data, analysis_type, include_recommendations)
        except FileNotFoundError:
            return APIResponse(
                success=False,
                error=f"File not found: {file_path}",
                status_code=404
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Error reading file: {str(e)}",
                status_code=500
            )

    def get_analysis_types(self) -> APIResponse:
        """Get available image analysis types."""
        return self._make_request("GET", "/analyze/types")


class WebSocketChat:
    """WebSocket client for real-time chat streaming."""

    def __init__(
        self,
        url: str,
        on_message: Callable[[Dict[str, Any]], None],
        on_error: Optional[Callable[[str], None]] = None,
        on_close: Optional[Callable[[], None]] = None
    ):
        """
        Initialize WebSocket chat client.

        Args:
            url: WebSocket URL
            on_message: Callback for received messages
            on_error: Callback for errors
            on_close: Callback when connection closes
        """
        self.url = url
        self.on_message = on_message
        self.on_error = on_error or (lambda e: None)
        self.on_close = on_close or (lambda: None)

        self.ws: Optional[websocket.WebSocketApp] = None
        self.thread: Optional[threading.Thread] = None
        self.connected = False
        self.message_queue: queue.Queue = queue.Queue()

    def connect(self):
        """Establish WebSocket connection."""
        if not WEBSOCKET_AVAILABLE:
            self.on_error("WebSocket library not installed")
            return

        def on_message(ws, message):
            try:
                data = json.loads(message)
                self.on_message(data)
            except json.JSONDecodeError:
                self.on_error(f"Invalid message format: {message}")

        def on_error(ws, error):
            self.on_error(str(error))

        def on_close(ws, close_status_code, close_msg):
            self.connected = False
            self.on_close()

        def on_open(ws):
            self.connected = True

        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()

        # Wait for connection
        timeout = 5
        start = time.time()
        while not self.connected and time.time() - start < timeout:
            time.sleep(0.1)

        if not self.connected:
            self.on_error("Connection timeout")

    def send_query(
        self,
        query: str,
        expertise_level: str = "intermediate"
    ):
        """
        Send a query through WebSocket.

        Args:
            query: User's question
            expertise_level: User's expertise level
        """
        if not self.connected or not self.ws:
            self.on_error("Not connected")
            return

        message = {
            "query": query,
            "expertise_level": expertise_level
        }

        try:
            self.ws.send(json.dumps(message))
        except Exception as e:
            self.on_error(f"Send error: {str(e)}")

    def close(self):
        """Close WebSocket connection."""
        if self.ws:
            self.ws.close()
            self.connected = False


# Convenience function to create client
def create_client(
    base_url: Optional[str] = None,
    timeout: int = 30
) -> SolarPVAPIClient:
    """
    Create and return an API client instance.

    Args:
        base_url: Backend API URL
        timeout: Request timeout

    Returns:
        Configured SolarPVAPIClient
    """
    return SolarPVAPIClient(base_url=base_url, timeout=timeout)


# Default client instance
_default_client: Optional[SolarPVAPIClient] = None


def get_client() -> SolarPVAPIClient:
    """Get or create default API client instance."""
    global _default_client
    if _default_client is None:
        _default_client = create_client()
    return _default_client
