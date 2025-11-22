"""
Solar PV LLM AI - Main Application Entry Point
FastAPI application with comprehensive middleware, routing, and lifecycle management
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from prometheus_client import make_asgi_app
import logging
import time
from typing import AsyncGenerator

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.database import engine, Base
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.api.v1.router import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting Solar PV LLM AI application...")

    # Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

    # Initialize ML models (lazy loading recommended for production)
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Solar PV LLM AI application...")
    await engine.dispose()
    logger.info("Application shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered Solar PV analysis with incremental training, RAG, and citation tracking",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/api/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# =============================================================================
# Middleware Configuration
# =============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom Middleware
app.add_middleware(RequestIDMiddleware)

if settings.ENABLE_RATE_LIMITING:
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=settings.RATE_LIMIT_PER_MINUTE,
        window_seconds=60,
    )


# =============================================================================
# Request/Response Middleware
# =============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and add processing time header"""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else "unknown"

    start_time = time.time()
    logger.info(f"Request started: {request.method} {request.url.path} [ID: {request_id}]")

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"[ID: {request_id}] [Status: {response.status_code}] "
        f"[Duration: {process_time:.3f}s]"
    )

    return response


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


# =============================================================================
# Routes
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    # TODO: Add database connection check, Redis check, etc.
    return {
        "status": "healthy",
        "timestamp": time.time(),
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # TODO: Check if all dependencies are ready
    return {
        "status": "ready",
        "timestamp": time.time(),
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        workers=settings.API_WORKERS if not settings.API_RELOAD else 1,
        log_level=settings.LOG_LEVEL.lower(),
    )
