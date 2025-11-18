"""Tests for the LLM router."""

import pytest
from src.orchestrator.router import LLMRouter
from src.orchestrator.models import QueryType, LLMProvider, ClassificationResult


class TestLLMRouter:
    """Test suite for LLMRouter."""

    @pytest.fixture
    def router(self):
        """Create router instance."""
        return LLMRouter(
            default_llm="auto",
            enable_hybrid=True,
            classification_threshold=0.7,
        )

    @pytest.fixture
    def high_confidence_calculation(self):
        """High confidence calculation classification."""
        return ClassificationResult(
            query_type=QueryType.CALCULATION,
            confidence=0.9,
            reasoning="Strong calculation indicators",
        )

    @pytest.fixture
    def low_confidence_classification(self):
        """Low confidence classification."""
        return ClassificationResult(
            query_type=QueryType.STANDARD_INTERPRETATION,
            confidence=0.5,
            reasoning="Ambiguous query",
        )

    def test_route_with_user_preference(self, router, high_confidence_calculation):
        """Test routing with explicit user preference."""
        result = router.route(
            high_confidence_calculation, preferred_llm=LLMProvider.CLAUDE
        )

        assert len(result) == 1
        assert result[0] == LLMProvider.CLAUDE

    def test_route_hybrid_request(self, router, high_confidence_calculation):
        """Test routing with hybrid request."""
        result = router.route(
            high_confidence_calculation, preferred_llm=LLMProvider.HYBRID
        )

        assert len(result) == 2
        assert LLMProvider.GPT in result
        assert LLMProvider.CLAUDE in result

    def test_route_calculation_query(self, router, high_confidence_calculation):
        """Test routing for calculation queries."""
        result = router.route(high_confidence_calculation)

        # Should prefer GPT for calculations
        assert result[0] == LLMProvider.GPT
        assert len(result) >= 1

    def test_route_technical_explanation(self, router):
        """Test routing for technical explanations."""
        classification = ClassificationResult(
            query_type=QueryType.TECHNICAL_EXPLANATION,
            confidence=0.85,
            reasoning="Technical explanation detected",
        )

        result = router.route(classification)

        # Should prefer Claude for explanations
        assert result[0] == LLMProvider.CLAUDE

    def test_hybrid_on_low_confidence(self, router, low_confidence_classification):
        """Test that low confidence triggers hybrid."""
        result = router.route(low_confidence_classification)

        # Low confidence should trigger hybrid
        assert len(result) == 2

    def test_get_primary_llm(self, router, high_confidence_calculation):
        """Test getting primary LLM."""
        primary = router.get_primary_llm(high_confidence_calculation)

        assert primary in [LLMProvider.GPT, LLMProvider.CLAUDE]

    def test_get_fallback_llm(self, router, high_confidence_calculation):
        """Test getting fallback LLM."""
        fallback = router.get_fallback_llm(
            LLMProvider.GPT, high_confidence_calculation
        )

        assert fallback == LLMProvider.CLAUDE

        fallback = router.get_fallback_llm(
            LLMProvider.CLAUDE, high_confidence_calculation
        )

        assert fallback == LLMProvider.GPT

    def test_router_without_hybrid(self):
        """Test router with hybrid disabled."""
        router = LLMRouter(enable_hybrid=False)

        classification = ClassificationResult(
            query_type=QueryType.STANDARD_INTERPRETATION,
            confidence=0.5,
            reasoning="Low confidence",
        )

        result = router.route(classification)

        # Should not use hybrid even with low confidence
        assert len(result) <= 2  # Primary + fallback
