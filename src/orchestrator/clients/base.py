"""Base class for LLM clients."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import time
from loguru import logger


class BaseLLMClient(ABC):
    """Abstract base class for LLM API clients."""

    def __init__(self, api_key: str, model: str, timeout: int = 60):
        """
        Initialize the LLM client.

        Args:
            api_key: API key for the LLM provider
            model: Model identifier
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary containing response content, tokens used, and metadata
        """
        pass

    @abstractmethod
    async def generate_with_image(
        self,
        prompt: str,
        image_data: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response with image input.

        Args:
            prompt: The user prompt
            image_data: Base64 encoded image data
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary containing response content, tokens used, and metadata
        """
        pass

    async def _execute_with_timing(self, coroutine):
        """Execute a coroutine and track timing."""
        start_time = time.time()
        try:
            result = await coroutine
            latency_ms = (time.time() - start_time) * 1000
            result["latency_ms"] = latency_ms
            return result
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"LLM request failed after {latency_ms:.2f}ms: {str(e)}")
            raise

    def _validate_params(self, max_tokens: int, temperature: float):
        """Validate common parameters."""
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0 <= temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
