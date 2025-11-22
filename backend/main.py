"""
Solar PV LLM AI System - Main FastAPI Application

Provides REST API endpoints for PV calculators and AI-powered analysis.
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from loguru import logger
import sys

from backend.config.settings import settings
from backend.api.routes import calculators
from backend.models.schemas import HealthCheckResponse
from backend.services.nrel_client import nrel_client


# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="""
    Solar PV LLM AI System API for photovoltaic calculations and analysis.

    ## Features

    ### PV Calculators
    - **Energy Yield Calculator**: Annual and monthly energy production estimates using NREL PVWatts API
    - **Degradation Rate Calculator**: Statistical analysis of PV system performance degradation
    - **Spectral Mismatch Calculator**: IEC 60904-7 compliant spectral correction factors

    ### Key Capabilities
    - Uncertainty quantification with confidence intervals
    - Robust statistical methods with outlier detection
    - Standards-compliant calculations (IEC 60904-7)
    - Integration with NREL solar resource data
    - Modular API design for independent or combined use

    ## Getting Started

    1. Obtain an NREL API key from [https://developer.nrel.gov/signup/](https://developer.nrel.gov/signup/)
    2. Set your API key in the `.env` file or use `DEMO_KEY` for testing (rate limited)
    3. Explore the interactive API documentation at `/docs`
    4. Try the example calculations in the endpoint descriptions

    ## Support

    For issues and questions, visit the [GitHub repository](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI)
    """,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(calculators.router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info(f"Starting {settings.project_name} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API prefix: {settings.api_v1_prefix}")

    # Check NREL API availability
    nrel_available = nrel_client.check_api_availability()
    if nrel_available:
        logger.info("NREL API connection verified")
    else:
        logger.warning("NREL API connection failed - some features may be limited")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info("Shutting down application")
    nrel_client.close()


@app.get(
    "/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Root endpoint",
    tags=["General"]
)
async def root():
    """
    Root endpoint with API information.

    Returns:
        API information and links
    """
    return {
        "name": settings.project_name,
        "version": settings.version,
        "description": "Solar PV LLM AI System API",
        "docs": "/docs",
        "health": "/health",
        "api": settings.api_v1_prefix
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    tags=["General"]
)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Service health status and NREL API availability
    """
    nrel_available = nrel_client.check_api_availability()

    return HealthCheckResponse(
        status="healthy",
        version=settings.version,
        timestamp=datetime.utcnow(),
        nrel_api_available=nrel_available
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.

    Args:
        request: HTTP request
        exc: Exception instance

    Returns:
        JSON error response
    """
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.debug else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
