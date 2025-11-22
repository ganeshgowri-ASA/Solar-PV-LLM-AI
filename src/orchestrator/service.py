"""Main orchestrator service coordinating all components."""

import time
from typing import Optional, List
from loguru import logger

from .config import settings
from .models import (
    QueryRequest,
    QueryType,
    LLMProvider,
    LLMResponse,
    OrchestratorResponse,
    ClassificationResult,
)
from .clients import GPTClient, ClaudeClient
from .classifier import SemanticClassifier
from .router import LLMRouter
from .synthesizer import ResponseSynthesizer
from .prompts import get_prompt_template


class OrchestratorService:
    """
    Main orchestrator service for multi-LLM query handling.

    Coordinates:
    - Query classification
    - LLM routing
    - Response generation
    - Fallback handling
    - Response synthesis
    """

    def __init__(self):
        """Initialize the orchestrator service."""
        logger.info("Initializing Orchestrator Service")

        # Initialize components
        self.classifier = SemanticClassifier()
        self.router = LLMRouter(
            default_llm=settings.default_llm,
            enable_hybrid=settings.enable_hybrid_synthesis,
            classification_threshold=settings.classification_threshold,
        )
        self.synthesizer = ResponseSynthesizer(
            enable_hybrid=settings.enable_hybrid_synthesis
        )

        # Initialize LLM clients
        self.gpt_client: Optional[GPTClient] = None
        self.claude_client: Optional[ClaudeClient] = None

        self._initialize_clients()

        logger.info("Orchestrator Service initialized successfully")

    def _initialize_clients(self):
        """Initialize LLM clients if API keys are available."""
        if settings.openai_api_key:
            try:
                self.gpt_client = GPTClient(
                    api_key=settings.openai_api_key,
                    model=settings.gpt_model,
                    timeout=settings.llm_timeout,
                )
                logger.info("GPT client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize GPT client: {e}")

        if settings.anthropic_api_key:
            try:
                self.claude_client = ClaudeClient(
                    api_key=settings.anthropic_api_key,
                    model=settings.claude_model,
                    timeout=settings.llm_timeout,
                )
                logger.info("Claude client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")

        if not self.gpt_client and not self.claude_client:
            logger.warning("No LLM clients initialized - API keys may be missing")

    async def process_query(self, request: QueryRequest) -> OrchestratorResponse:
        """
        Process a query through the orchestrator.

        Args:
            request: Query request with user input

        Returns:
            Orchestrator response with synthesized output

        Raises:
            ValueError: If no LLM clients are available
        """
        start_time = time.time()

        logger.info(f"Processing query: {request.query[:100]}...")

        # Step 1: Classify query
        classification = self._classify_query(request)

        # Step 2: Route to appropriate LLM(s)
        providers = self.router.route(classification, request.preferred_llm)

        # Step 3: Generate responses
        responses = await self._generate_responses(
            request, classification, providers
        )

        # Step 4: Handle fallback if needed
        if not responses and settings.enable_fallback:
            responses = await self._handle_fallback(request, classification, providers)

        # Step 5: Synthesize final response
        is_hybrid = len(providers) > 1 and len(responses) > 1
        final_response = self.synthesizer.synthesize(responses, is_hybrid)

        # Calculate total latency
        total_latency = (time.time() - start_time) * 1000

        # Build orchestrator response
        result = OrchestratorResponse(
            response=final_response,
            primary_llm=providers[0] if providers else LLMProvider.CLAUDE,
            query_type=classification.query_type,
            classification_confidence=classification.confidence,
            responses=responses,
            is_hybrid=is_hybrid,
            fallback_used=len(responses) > len(providers),
            total_latency_ms=total_latency,
            metadata={
                "classification_reasoning": classification.reasoning,
                "providers_used": [p.value for p in providers],
            },
        )

        logger.info(
            f"Query processed successfully in {total_latency:.2f}ms "
            f"(type: {classification.query_type.value}, "
            f"providers: {len(responses)})"
        )

        return result

    def _classify_query(self, request: QueryRequest) -> ClassificationResult:
        """Classify the query type."""
        # Use explicit type if provided
        if request.query_type:
            logger.info(f"Using explicit query type: {request.query_type.value}")
            return ClassificationResult(
                query_type=request.query_type,
                confidence=1.0,
                reasoning="Explicitly specified by user",
            )

        # Classify based on query content
        return self.classifier.classify(
            request.query, image_data=bool(request.image_data)
        )

    async def _generate_responses(
        self,
        request: QueryRequest,
        classification: ClassificationResult,
        providers: List[LLMProvider],
    ) -> List[LLMResponse]:
        """Generate responses from specified providers."""
        responses = []

        for provider in providers:
            try:
                response = await self._generate_single_response(
                    request, classification, provider
                )
                if response and self.synthesizer.is_response_valid(response):
                    responses.append(response)
                else:
                    logger.warning(f"Invalid response from {provider.value}")
            except Exception as e:
                logger.error(f"Error generating response from {provider.value}: {e}")
                continue

        return responses

    async def _generate_single_response(
        self,
        request: QueryRequest,
        classification: ClassificationResult,
        provider: LLMProvider,
    ) -> Optional[LLMResponse]:
        """Generate a single response from a specific provider."""
        start_time = time.time()

        # Get appropriate client
        client = self._get_client(provider)
        if not client:
            logger.error(f"No client available for {provider.value}")
            return None

        # Get prompt template
        template = get_prompt_template(classification.query_type)

        # Format prompt
        user_prompt = template.format_user_prompt(
            query=request.query, **request.context
        )

        try:
            # Generate response (with or without image)
            if request.image_data:
                result = await client.generate_with_image(
                    prompt=user_prompt,
                    image_data=request.image_data,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                )
            else:
                result = await client.generate(
                    prompt=user_prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system_prompt=template.system_prompt,
                )

            latency = (time.time() - start_time) * 1000

            return LLMResponse(
                provider=provider,
                content=result["content"],
                model=result["model"],
                tokens_used=result.get("tokens_used"),
                latency_ms=latency,
                metadata=result.get("metadata"),
            )

        except Exception as e:
            logger.error(f"Failed to generate response from {provider.value}: {e}")
            return None

    async def _handle_fallback(
        self,
        request: QueryRequest,
        classification: ClassificationResult,
        providers: List[LLMProvider],
    ) -> List[LLMResponse]:
        """Handle fallback when primary provider(s) fail."""
        logger.info("Attempting fallback response generation")

        # Get fallback provider
        primary = providers[0] if providers else None
        fallback_provider = self.router.get_fallback_llm(primary, classification)

        if not fallback_provider or fallback_provider in providers:
            logger.warning("No suitable fallback provider available")
            return []

        # Try generating from fallback
        try:
            response = await self._generate_single_response(
                request, classification, fallback_provider
            )

            if response and self.synthesizer.is_response_valid(response):
                logger.info(f"Fallback successful with {fallback_provider.value}")
                return [response]
        except Exception as e:
            logger.error(f"Fallback also failed: {e}")

        return []

    def _get_client(self, provider: LLMProvider):
        """Get the appropriate client for a provider."""
        if provider == LLMProvider.GPT:
            return self.gpt_client
        elif provider == LLMProvider.CLAUDE:
            return self.claude_client
        else:
            logger.error(f"Unknown provider: {provider}")
            return None

    async def health_check(self) -> dict:
        """
        Check health status of the orchestrator service.

        Returns:
            Health status dictionary
        """
        return {
            "status": "healthy",
            "components": {
                "classifier": "operational",
                "router": "operational",
                "synthesizer": "operational",
                "gpt_client": "available" if self.gpt_client else "unavailable",
                "claude_client": "available" if self.claude_client else "unavailable",
            },
            "config": {
                "default_llm": settings.default_llm,
                "enable_fallback": settings.enable_fallback,
                "enable_hybrid": settings.enable_hybrid_synthesis,
            },
        }
