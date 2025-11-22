"""
Main FastAPI application.
Solar PV LLM AI - Backend API with RAG, LLM orchestration, and PV analytics.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger

from app.core.config import settings
from app.middleware.logging import setup_logging, LoggingMiddleware
from app.middleware.metrics import MetricsMiddleware

# Import routers
from app.api.endpoints import chat, pv_calculations, image_analysis, documents, health

# Setup logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"] if settings.CORS_ALLOW_METHODS == "*" else settings.CORS_ALLOW_METHODS.split(","),
    allow_headers=["*"] if settings.CORS_ALLOW_HEADERS == "*" else settings.CORS_ALLOW_HEADERS.split(","),
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(pv_calculations.router)
app.include_router(image_analysis.router)
app.include_router(documents.router)

logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
logger.info(f"Environment: {settings.ENVIRONMENT}")
logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("=" * 80)
    logger.info(f"{settings.APP_NAME} - Starting up")
    logger.info("=" * 80)
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 80)

    # Initialize services
    try:
        from app.services.rag_engine import rag_engine
        logger.info("✓ RAG Engine initialized")
    except Exception as e:
        logger.error(f"✗ RAG Engine initialization failed: {e}")

    try:
        from app.services.llm_orchestrator import llm_orchestrator
        logger.info("✓ LLM Orchestrator initialized")
    except Exception as e:
        logger.error(f"✗ LLM Orchestrator initialization failed: {e}")

    try:
        from app.services.image_analyzer import image_analyzer
        logger.info("✓ Image Analyzer initialized")
    except Exception as e:
        logger.error(f"✗ Image Analyzer initialization failed: {e}")

    try:
        from app.services.pv_calculator import pv_calculator
        logger.info("✓ PV Calculator initialized")
    except Exception as e:
        logger.error(f"✗ PV Calculator initialization failed: {e}")

    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("=" * 80)
    logger.info(f"{settings.APP_NAME} - Shutting down")
    logger.info("=" * 80)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
