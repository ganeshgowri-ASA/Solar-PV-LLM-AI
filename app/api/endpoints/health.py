"""
Health check and metrics endpoints.
"""
import time
from datetime import datetime
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from loguru import logger

from app.models.schemas import HealthStatus, MetricsResponse
from app.core.config import settings

router = APIRouter(tags=["Health & Metrics"])

# Track service start time
SERVICE_START_TIME = time.time()


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint.

    Returns the health status of the API and its dependencies.

    **Checks:**
    - API service status
    - Vector database connectivity
    - LLM service availability

    **Returns:**
    - status: healthy, degraded, or unhealthy
    - timestamp: Current timestamp
    - version: API version
    - uptime_seconds: Service uptime
    - services: Individual service statuses
    """
    try:
        # Check individual services
        services = {}

        # Check vector database
        try:
            from app.services.rag_engine import rag_engine
            stats = rag_engine.get_collection_stats()
            services["vector_db"] = "healthy" if stats.get("status") == "healthy" else "degraded"
        except Exception as e:
            logger.error(f"Vector DB health check failed: {e}")
            services["vector_db"] = "unhealthy"

        # Check LLM service
        try:
            from app.services.llm_orchestrator import llm_orchestrator
            if llm_orchestrator.openai_client or llm_orchestrator.anthropic_client:
                services["llm"] = "healthy"
            else:
                services["llm"] = "degraded"
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            services["llm"] = "unhealthy"

        # Image analyzer
        try:
            from app.services.image_analyzer import image_analyzer
            services["image_analyzer"] = "healthy"
        except Exception as e:
            logger.error(f"Image analyzer health check failed: {e}")
            services["image_analyzer"] = "unhealthy"

        # PV calculator
        try:
            from app.services.pv_calculator import pv_calculator
            services["pv_calculator"] = "healthy"
        except Exception as e:
            logger.error(f"PV calculator health check failed: {e}")
            services["pv_calculator"] = "unhealthy"

        # Determine overall status
        if all(status == "healthy" for status in services.values()):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in services.values()):
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        # Calculate uptime
        uptime = time.time() - SERVICE_START_TIME

        health = HealthStatus(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION,
            uptime_seconds=round(uptime, 2),
            services=services
        )

        return health

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION,
            uptime_seconds=0,
            services={"error": str(e)}
        )


@router.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus format for monitoring.

    **Metrics include:**
    - HTTP request counts
    - Request duration histograms
    - Active request gauge
    - Custom application metrics

    **Usage:**
    Configure Prometheus to scrape this endpoint:
    ```yaml
    scrape_configs:
      - job_name: 'solar-pv-api'
        static_configs:
          - targets: ['localhost:8000']
        metrics_path: '/metrics'
    ```
    """
    try:
        metrics = generate_latest()
        return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return Response(content=f"# Error generating metrics: {e}", status_code=500)


@router.get("/")
async def root():
    """
    Root endpoint with API information.

    **Returns:**
    - API name, version, and description
    - Links to documentation
    - Available endpoints
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "documentation": "/docs",
        "openapi_spec": "/openapi.json",
        "health": "/health",
        "metrics": "/metrics",
        "endpoints": {
            "chat": "/chat",
            "pv_calculations": "/pv",
            "image_analysis": "/image-analysis",
            "documents": "/documents"
        }
    }


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint.

    **Returns:**
    - pong: timestamp
    """
    return {
        "pong": datetime.utcnow().isoformat(),
        "status": "ok"
    }
