"""Anthropic Claude 3.5 client implementation."""

from typing import Optional, Dict, Any
from anthropic import AsyncAnthropic
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseLLMClient


class ClaudeClient(BaseLLMClient):
    """Client for Anthropic Claude 3.5 API."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        timeout: int = 60
    ):
        """Initialize Claude client."""
        super().__init__(api_key, model, timeout)
        self.client = AsyncAnthropic(api_key=api_key, timeout=timeout)
        logger.info(f"Initialized Claude client with model: {model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using Claude 3.5.

        Args:
            prompt: User prompt
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            system_prompt: Optional system prompt
            **kwargs: Additional Anthropic parameters

        Returns:
            Response dictionary with content and metadata
        """
        self._validate_params(max_tokens, temperature)

        try:
            logger.debug(f"Sending request to Claude 3.5")

            request_params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            }

            if system_prompt:
                request_params["system"] = system_prompt

            response = await self.client.messages.create(**request_params)

            # Extract text content from response
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            result = {
                "content": content,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "model": self.model,
                "stop_reason": response.stop_reason,
                "metadata": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            }

            logger.info(f"Claude 3.5 response received: {result['tokens_used']} tokens")
            return result

        except Exception as e:
            logger.error(f"Claude 3.5 generation failed: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_with_image(
        self,
        prompt: str,
        image_data: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response with image input using Claude 3.5 vision.

        Args:
            prompt: User prompt
            image_data: Base64 encoded image
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            **kwargs: Additional Anthropic parameters

        Returns:
            Response dictionary with content and metadata
        """
        self._validate_params(max_tokens, temperature)

        try:
            logger.debug("Sending image analysis request to Claude 3.5")

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
                **kwargs
            )

            # Extract text content from response
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            result = {
                "content": content,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "model": self.model,
                "stop_reason": response.stop_reason,
                "metadata": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "image_analysis": True
                }
            }

            logger.info(f"Claude 3.5 image analysis complete: {result['tokens_used']} tokens")
            return result

        except Exception as e:
            logger.error(f"Claude 3.5 image generation failed: {str(e)}")
            raise
