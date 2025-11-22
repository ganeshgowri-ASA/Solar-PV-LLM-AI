"""
Main FastAPI application for Solar PV LLM AI System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from backend.config import get_settings
from backend.database.connection import init_db, create_tables
from backend.utils.logger import setup_logging
from backend.api import query_routes, feedback_routes, admin_routes


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Solar PV LLM AI System")
    settings = get_settings()

    # Initialize database
    logger.info("Initializing database connection")
    init_db()

    # Create tables if they don't exist
    try:
        create_tables()
        logger.info("Database tables verified")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Solar PV LLM AI System")


# Create FastAPI app
app = FastAPI(
    title="Solar PV LLM AI System",
    description="Incremental learning system with user feedback and active retraining for Solar PV knowledge",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"status={response.status_code} duration={duration:.3f}s"
    )

    return response


# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health")
def health_check():
    """Basic health check endpoint"""
    from backend.database.connection import health_check as db_health

    db_healthy = db_health()

    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "Solar PV LLM AI System",
        "version": "1.0.0",
        "description": "Incremental learning system with user feedback and active retraining",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": {
                "queries": f"{settings.api_prefix}/{settings.api_version}/query",
                "feedback": f"{settings.api_prefix}/{settings.api_version}/feedback",
                "admin": f"{settings.api_prefix}/{settings.api_version}/admin"
            }
        }
    }


# Include routers
api_prefix = f"{settings.api_prefix}/{settings.api_version}"

app.include_router(query_routes.router, prefix=api_prefix)
app.include_router(feedback_routes.router, prefix=api_prefix)
app.include_router(admin_routes.router, prefix=api_prefix)

logger.info(f"API routes registered with prefix: {api_prefix}")


# Prometheus metrics endpoint (if enabled)
if settings.enable_prometheus:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response

    # Define metrics
    REQUEST_COUNT = Counter(
        'http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status']
    )

    REQUEST_DURATION = Histogram(
        'http_request_duration_seconds',
        'HTTP request duration',
        ['method', 'endpoint']
    )

    @app.get("/metrics")
    def metrics():
        """Prometheus metrics endpoint"""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    logger.info("Prometheus metrics enabled at /metrics")


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")

    uvicorn.run(
        "backend.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
