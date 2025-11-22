"""OpenAI GPT-4o client implementation."""

from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseLLMClient


class GPTClient(BaseLLMClient):
    """Client for OpenAI GPT-4o API."""

    def __init__(self, api_key: str, model: str = "gpt-4o", timeout: int = 60):
        """Initialize GPT client."""
        super().__init__(api_key, model, timeout)
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        logger.info(f"Initialized GPT client with model: {model}")

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
        Generate a response using GPT-4o.

        Args:
            prompt: User prompt
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            system_prompt: Optional system prompt
            **kwargs: Additional OpenAI parameters

        Returns:
            Response dictionary with content and metadata
        """
        self._validate_params(max_tokens, temperature)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            logger.debug(f"Sending request to GPT-4o with {len(messages)} messages")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            result = {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": self.model,
                "finish_reason": response.choices[0].finish_reason,
                "metadata": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                }
            }

            logger.info(f"GPT-4o response received: {result['tokens_used']} tokens")
            return result

        except Exception as e:
            logger.error(f"GPT-4o generation failed: {str(e)}")
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
        Generate a response with image input using GPT-4o vision.

        Args:
            prompt: User prompt
            image_data: Base64 encoded image
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            **kwargs: Additional OpenAI parameters

        Returns:
            Response dictionary with content and metadata
        """
        self._validate_params(max_tokens, temperature)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ]

        try:
            logger.debug("Sending image analysis request to GPT-4o")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            result = {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": self.model,
                "finish_reason": response.choices[0].finish_reason,
                "metadata": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "image_analysis": True
                }
            }

            logger.info(f"GPT-4o image analysis complete: {result['tokens_used']} tokens")
            return result

        except Exception as e:
            logger.error(f"GPT-4o image generation failed: {str(e)}")
            raise
