"""FastAPI application for the LLM orchestrator."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from ..config import settings
from ..service import OrchestratorService
from ..models import QueryRequest, OrchestratorResponse


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Solar PV Multi-LLM Orchestrator",
        description="Intelligent routing between GPT-4o and Claude 3.5 for Solar PV queries",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>"
    )

    # Initialize orchestrator service
    orchestrator = OrchestratorService()

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Solar PV Multi-LLM Orchestrator",
            "version": "1.0.0",
            "status": "operational",
            "endpoints": {
                "query": "/api/v1/query",
                "health": "/api/v1/health",
                "docs": "/docs",
            },
        }

    @app.get("/api/v1/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint.

        Returns service health status and component availability.
        """
        try:
            health_status = await orchestrator.health_check()
            return JSONResponse(content=health_status, status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                content={"status": "unhealthy", "error": str(e)},
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    @app.post(
        "/api/v1/query",
        response_model=OrchestratorResponse,
        tags=["Query"],
        status_code=status.HTTP_200_OK,
    )
    async def process_query(request: QueryRequest):
        """
        Process a query through the multi-LLM orchestrator.

        The orchestrator will:
        1. Classify the query type
        2. Route to the most appropriate LLM(s)
        3. Generate response(s)
        4. Handle fallback if needed
        5. Synthesize final response

        Args:
            request: Query request with user input

        Returns:
            Orchestrator response with synthesized output

        Raises:
            HTTPException: If query processing fails
        """
        try:
            logger.info(f"Received query request: {request.query[:100]}...")

            # Validate request
            if not request.query or not request.query.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Query cannot be empty",
                )

            # Process query
            response = await orchestrator.process_query(request)

            logger.info(f"Query processed successfully (latency: {response.total_latency_ms:.2f}ms)")

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Query processing failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process query: {str(e)}",
            )

    @app.get("/api/v1/models", tags=["Models"])
    async def list_models():
        """
        List available LLM models and their status.

        Returns:
            Dictionary of available models and configuration
        """
        return {
            "models": {
                "gpt": {
                    "name": settings.gpt_model,
                    "provider": "OpenAI",
                    "available": bool(settings.openai_api_key),
                },
                "claude": {
                    "name": settings.claude_model,
                    "provider": "Anthropic",
                    "available": bool(settings.anthropic_api_key),
                },
            },
            "routing": {
                "default_llm": settings.default_llm,
                "enable_fallback": settings.enable_fallback,
                "enable_hybrid": settings.enable_hybrid_synthesis,
            },
        }

    @app.get("/api/v1/query-types", tags=["Query Types"])
    async def list_query_types():
        """
        List supported query types.

        Returns:
            Dictionary of query types and their descriptions
        """
        from ..models import QueryType

        return {
            "query_types": {
                QueryType.STANDARD_INTERPRETATION.value: {
                    "name": "Standard Interpretation",
                    "description": "General questions about solar PV systems",
                    "examples": [
                        "What is a solar inverter?",
                        "Explain how solar panels work",
                    ],
                },
                QueryType.CALCULATION.value: {
                    "name": "Calculation",
                    "description": "Numerical calculations and system sizing",
                    "examples": [
                        "Calculate energy yield for a 10kW system",
                        "Size inverter for 20 panels of 400W each",
                    ],
                },
                QueryType.IMAGE_ANALYSIS.value: {
                    "name": "Image Analysis",
                    "description": "Visual inspection and analysis",
                    "examples": [
                        "Analyze this thermal image of solar panels",
                        "Inspect this PV array layout",
                    ],
                },
                QueryType.TECHNICAL_EXPLANATION.value: {
                    "name": "Technical Explanation",
                    "description": "Detailed technical explanations",
                    "examples": [
                        "How does MPPT tracking work?",
                        "Explain the physics of the photovoltaic effect",
                    ],
                },
                QueryType.CODE_GENERATION.value: {
                    "name": "Code Generation",
                    "description": "Generate code for PV simulations and analysis",
                    "examples": [
                        "Write Python code to calculate shading losses",
                        "Generate a PV system simulation script",
                    ],
                },
            }
        }

    return app
