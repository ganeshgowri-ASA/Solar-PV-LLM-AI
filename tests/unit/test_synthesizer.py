"""Tests for the response synthesizer."""

import pytest
from src.orchestrator.synthesizer import ResponseSynthesizer
from src.orchestrator.models import LLMResponse, LLMProvider


class TestResponseSynthesizer:
    """Test suite for ResponseSynthesizer."""

    @pytest.fixture
    def synthesizer(self):
        """Create synthesizer instance."""
        return ResponseSynthesizer(enable_hybrid=True)

    def test_synthesize_single_response(
        self, synthesizer, sample_llm_response_gpt
    ):
        """Test synthesizing a single response."""
        result = synthesizer.synthesize([sample_llm_response_gpt], is_hybrid=False)

        assert result == sample_llm_response_gpt.content

    def test_synthesize_hybrid_response(
        self, synthesizer, sample_llm_response_gpt, sample_llm_response_claude
    ):
        """Test synthesizing hybrid response."""
        responses = [sample_llm_response_gpt, sample_llm_response_claude]
        result = synthesizer.synthesize(responses, is_hybrid=True)

        # Should include content from both
        assert "GPT-4o" in result or "Claude" in result
        assert len(result) > len(sample_llm_response_gpt.content)

    def test_synthesize_empty_responses(self, synthesizer):
        """Test that empty response list raises error."""
        with pytest.raises(ValueError, match="No responses to synthesize"):
            synthesizer.synthesize([], is_hybrid=False)

    def test_is_response_valid(self, synthesizer):
        """Test response validation."""
        valid_response = LLMResponse(
            provider=LLMProvider.GPT,
            content="This is a good response with sufficient content.",
            model="gpt-4o",
            tokens_used=100,
        )

        assert synthesizer.is_response_valid(valid_response) is True

    def test_is_response_invalid_empty(self, synthesizer):
        """Test that empty responses are invalid."""
        empty_response = LLMResponse(
            provider=LLMProvider.GPT,
            content="",
            model="gpt-4o",
            tokens_used=0,
        )

        assert synthesizer.is_response_valid(empty_response) is False

    def test_is_response_invalid_too_short(self, synthesizer):
        """Test that very short responses are invalid."""
        short_response = LLMResponse(
            provider=LLMProvider.GPT,
            content="Error",
            model="gpt-4o",
            tokens_used=5,
        )

        assert synthesizer.is_response_valid(short_response) is False

    def test_select_best_response(
        self, synthesizer, sample_llm_response_gpt, sample_llm_response_claude
    ):
        """Test selecting best response from multiple."""
        # Make Claude response longer
        sample_llm_response_claude.content = (
            "This is a much longer and more comprehensive response "
            "from Claude that provides detailed information about "
            "solar panels and their operation."
        )

        responses = [sample_llm_response_gpt, sample_llm_response_claude]
        result = synthesizer._select_best_response(responses)

        # Should select the longer (more comprehensive) response
        assert result == sample_llm_response_claude.content

    def test_select_for_fallback(
        self, synthesizer, sample_llm_response_gpt, sample_llm_response_claude
    ):
        """Test selecting response for fallback."""
        responses = [sample_llm_response_gpt, sample_llm_response_claude]

        result = synthesizer.select_for_fallback(
            responses, failed_provider=LLMProvider.GPT
        )

        # Should exclude GPT and return Claude
        assert result == sample_llm_response_claude.content

    def test_select_for_fallback_no_valid_responses(self, synthesizer):
        """Test fallback with no valid responses."""
        empty_response = LLMResponse(
            provider=LLMProvider.CLAUDE,
            content="",
            model="claude-3-5-sonnet-20241022",
            tokens_used=0,
        )

        result = synthesizer.select_for_fallback(
            [empty_response], failed_provider=LLMProvider.GPT
        )

        assert result is None
