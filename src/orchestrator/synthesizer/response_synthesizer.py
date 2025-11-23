"""Response synthesis for combining and selecting LLM outputs."""

from typing import List, Optional
from loguru import logger

from ..models import LLMResponse, LLMProvider


class ResponseSynthesizer:
    """
    Synthesizes responses from multiple LLMs.

    Handles:
    - Fallback selection when primary LLM fails
    - Hybrid response synthesis from multiple LLMs
    - Response quality assessment
    """

    def __init__(self, enable_hybrid: bool = True):
        """
        Initialize the response synthesizer.

        Args:
            enable_hybrid: Whether hybrid synthesis is enabled
        """
        self.enable_hybrid = enable_hybrid
        logger.info(f"Initialized Response Synthesizer (hybrid: {enable_hybrid})")

    def synthesize(
        self,
        responses: List[LLMResponse],
        is_hybrid: bool = False
    ) -> str:
        """
        Synthesize final response from LLM outputs.

        Args:
            responses: List of LLM responses
            is_hybrid: Whether to create a hybrid response

        Returns:
            Final synthesized response text
        """
        if not responses:
            raise ValueError("No responses to synthesize")

        # Single response - return as is
        if len(responses) == 1:
            logger.debug("Single response, no synthesis needed")
            return responses[0].content

        # Hybrid synthesis
        if is_hybrid and self.enable_hybrid:
            return self._create_hybrid_response(responses)

        # Fallback - select best response
        return self._select_best_response(responses)

    def _create_hybrid_response(self, responses: List[LLMResponse]) -> str:
        """
        Create a hybrid response combining insights from multiple LLMs.

        Strategy:
        1. Present both perspectives with clear attribution
        2. Highlight complementary insights
        3. Note areas of agreement and divergence
        """
        logger.info(f"Creating hybrid response from {len(responses)} LLMs")

        if len(responses) < 2:
            return responses[0].content

        # Sort responses by provider for consistency
        sorted_responses = sorted(responses, key=lambda x: x.provider.value)

        # Build hybrid response
        hybrid_parts = [
            "# Comprehensive Analysis (Multi-LLM Synthesis)\n",
            "\nThis response synthesizes insights from multiple AI models "
            "to provide a comprehensive perspective.\n"
        ]

        # Add each LLM's response
        for i, response in enumerate(sorted_responses, 1):
            provider_name = self._get_provider_display_name(response.provider)
            hybrid_parts.append(f"\n## Perspective {i}: {provider_name}\n")
            hybrid_parts.append(response.content)
            hybrid_parts.append("\n")

        # Add synthesis note
        hybrid_parts.append(
            "\n---\n"
            "*Note: This hybrid response combines insights from multiple AI models. "
            "Consider reviewing both perspectives for a complete understanding.*\n"
        )

        synthesized = "".join(hybrid_parts)

        logger.info(
            f"Hybrid response created: {len(synthesized)} characters from "
            f"{len(responses)} sources"
        )

        return synthesized

    def _select_best_response(self, responses: List[LLMResponse]) -> str:
        """
        Select the best response from multiple options.

        Selection criteria:
        1. Response completeness (length)
        2. Provider priority (if configured)
        3. First non-empty response
        """
        logger.info(f"Selecting best response from {len(responses)} options")

        # Filter out empty responses
        valid_responses = [r for r in responses if r.content.strip()]

        if not valid_responses:
            logger.warning("No valid responses found")
            return "I apologize, but I was unable to generate a response. Please try again."

        # Select based on content length (more comprehensive response)
        best_response = max(valid_responses, key=lambda r: len(r.content))

        logger.info(
            f"Selected {best_response.provider.value} response "
            f"({len(best_response.content)} characters)"
        )

        return best_response.content

    def _get_provider_display_name(self, provider: LLMProvider) -> str:
        """Get display name for a provider."""
        names = {
            LLMProvider.GPT: "GPT-4o",
            LLMProvider.CLAUDE: "Claude 3.5 Sonnet",
        }
        return names.get(provider, provider.value)

    def is_response_valid(self, response: LLMResponse) -> bool:
        """
        Check if a response is valid and complete.

        Args:
            response: LLM response to validate

        Returns:
            True if response is valid
        """
        # Basic validation
        if not response.content or not response.content.strip():
            logger.warning(f"Empty response from {response.provider.value}")
            return False

        # Check for error indicators
        error_indicators = [
            "error",
            "unable to",
            "cannot process",
            "failed to",
        ]

        content_lower = response.content.lower()
        if any(indicator in content_lower for indicator in error_indicators):
            # Check if it's actually an error message
            if len(response.content) < 200:  # Short error message
                logger.warning(
                    f"Possible error response from {response.provider.value}"
                )
                return False

        # Minimum length check (avoid truncated responses)
        if len(response.content.strip()) < 50:
            logger.warning(
                f"Response too short from {response.provider.value} "
                f"({len(response.content)} chars)"
            )
            return False

        return True

    def select_for_fallback(
        self,
        responses: List[LLMResponse],
        failed_provider: Optional[LLMProvider] = None
    ) -> Optional[str]:
        """
        Select response for fallback scenario.

        Args:
            responses: Available responses
            failed_provider: Provider that failed (to exclude)

        Returns:
            Selected response content or None
        """
        # Filter valid responses, excluding failed provider
        valid_responses = [
            r for r in responses
            if self.is_response_valid(r) and r.provider != failed_provider
        ]

        if not valid_responses:
            logger.error("No valid responses available for fallback")
            return None

        # Return the best valid response
        best = max(valid_responses, key=lambda r: len(r.content))
        logger.info(f"Selected {best.provider.value} for fallback")
        return best.content
