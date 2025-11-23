"""LLM routing logic for intelligent model selection."""

from typing import List, Optional
from loguru import logger

from ..models import QueryType, LLMProvider, ClassificationResult


class LLMRouter:
    """
    Routes queries to the most appropriate LLM based on query type and characteristics.

    Routing Strategy:
    - GPT-4o: Better for calculations, code generation, structured outputs
    - Claude 3.5: Better for long-form explanations, nuanced analysis, technical depth
    - Hybrid: Complex queries requiring multiple perspectives
    """

    def __init__(
        self,
        default_llm: str = "auto",
        enable_hybrid: bool = True,
        classification_threshold: float = 0.7
    ):
        """
        Initialize the router.

        Args:
            default_llm: Default LLM selection ("auto", "gpt", "claude")
            enable_hybrid: Whether to enable hybrid responses
            classification_threshold: Confidence threshold for classification
        """
        self.default_llm = default_llm
        self.enable_hybrid = enable_hybrid
        self.classification_threshold = classification_threshold

        # Define LLM preferences for each query type
        self.routing_rules = {
            QueryType.CALCULATION: [LLMProvider.GPT, LLMProvider.CLAUDE],
            QueryType.IMAGE_ANALYSIS: [LLMProvider.GPT, LLMProvider.CLAUDE],
            QueryType.CODE_GENERATION: [LLMProvider.GPT, LLMProvider.CLAUDE],
            QueryType.TECHNICAL_EXPLANATION: [LLMProvider.CLAUDE, LLMProvider.GPT],
            QueryType.STANDARD_INTERPRETATION: [LLMProvider.CLAUDE, LLMProvider.GPT],
        }

        logger.info(
            f"Initialized LLM Router (default: {default_llm}, "
            f"hybrid: {enable_hybrid})"
        )

    def route(
        self,
        classification: ClassificationResult,
        preferred_llm: Optional[LLMProvider] = None
    ) -> List[LLMProvider]:
        """
        Determine which LLM(s) should handle the query.

        Args:
            classification: Query classification result
            preferred_llm: User's preferred LLM (overrides routing)

        Returns:
            List of LLM providers to use (in priority order)
        """
        # User preference takes precedence
        if preferred_llm and preferred_llm != LLMProvider.HYBRID:
            logger.info(f"Using user-preferred LLM: {preferred_llm.value}")
            return [preferred_llm]

        # Explicit hybrid request
        if preferred_llm == LLMProvider.HYBRID:
            logger.info("User requested hybrid response")
            return [LLMProvider.GPT, LLMProvider.CLAUDE]

        # Determine if hybrid is appropriate
        if self._should_use_hybrid(classification):
            logger.info(
                f"Using hybrid approach for {classification.query_type.value} "
                f"(confidence: {classification.confidence:.2f})"
            )
            return [LLMProvider.GPT, LLMProvider.CLAUDE]

        # Route based on query type
        providers = self._route_by_query_type(classification.query_type)

        logger.info(
            f"Routing {classification.query_type.value} to "
            f"{providers[0].value} (fallback: {providers[1].value if len(providers) > 1 else 'none'})"
        )

        return providers

    def _should_use_hybrid(self, classification: ClassificationResult) -> bool:
        """
        Determine if hybrid response is appropriate.

        Hybrid is used when:
        1. Hybrid mode is enabled
        2. Classification confidence is below threshold (ambiguous)
        3. Query type benefits from multiple perspectives
        """
        if not self.enable_hybrid:
            return False

        # Low confidence suggests ambiguous query
        if classification.confidence < self.classification_threshold:
            logger.debug(
                f"Low classification confidence ({classification.confidence:.2f}) "
                f"suggests hybrid approach"
            )
            return True

        # Certain query types benefit from hybrid
        hybrid_beneficial_types = [
            QueryType.TECHNICAL_EXPLANATION,
            QueryType.STANDARD_INTERPRETATION
        ]

        if classification.query_type in hybrid_beneficial_types:
            # Use hybrid for complex technical questions
            return classification.confidence < 0.85

        return False

    def _route_by_query_type(self, query_type: QueryType) -> List[LLMProvider]:
        """
        Route query based on its type.

        Returns list with primary LLM first, fallback second.
        """
        if query_type in self.routing_rules:
            return self.routing_rules[query_type]

        # Default routing
        logger.warning(
            f"No specific routing rule for {query_type.value}, "
            f"using default"
        )
        return [LLMProvider.CLAUDE, LLMProvider.GPT]

    def get_primary_llm(
        self,
        classification: ClassificationResult,
        preferred_llm: Optional[LLMProvider] = None
    ) -> LLMProvider:
        """
        Get the primary LLM for a query.

        Args:
            classification: Query classification result
            preferred_llm: User's preferred LLM

        Returns:
            Primary LLM provider
        """
        providers = self.route(classification, preferred_llm)
        return providers[0]

    def get_fallback_llm(
        self,
        primary_llm: LLMProvider,
        classification: ClassificationResult
    ) -> Optional[LLMProvider]:
        """
        Get fallback LLM if primary fails.

        Args:
            primary_llm: The primary LLM that failed
            classification: Query classification result

        Returns:
            Fallback LLM provider or None
        """
        providers = self._route_by_query_type(classification.query_type)

        # Return the other provider
        for provider in providers:
            if provider != primary_llm:
                logger.info(f"Fallback from {primary_llm.value} to {provider.value}")
                return provider

        # If no specific fallback, use the opposite
        fallback = (
            LLMProvider.CLAUDE if primary_llm == LLMProvider.GPT
            else LLMProvider.GPT
        )

        logger.info(f"Using default fallback: {fallback.value}")
        return fallback
