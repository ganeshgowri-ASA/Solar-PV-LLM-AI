"""
Solar-PV-LLM-AI Backend API
FastAPI application for Solar PV AI LLM system
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# Configuration
class Settings:
    APP_NAME: str = "Solar PV LLM AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    APP_ENV: str = os.getenv("APP_ENV", "production")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")


settings = Settings()

# Redis client (initialized on startup)
redis_client: redis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    global redis_client

    # Startup
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        print(f"✓ Connected to Redis at {settings.REDIS_URL}")
    except Exception as e:
        print(f"⚠ Redis connection failed: {e}")
        redis_client = None

    yield

    # Shutdown
    if redis_client:
        await redis_client.close()
        print("✓ Redis connection closed")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Solar PV system with LLM capabilities",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str


class HealthReadyResponse(HealthResponse):
    redis: str
    dependencies: dict[str, str]


class QueryRequest(BaseModel):
    query: str
    context: str | None = None
    max_tokens: int = 1024


class QueryResponse(BaseModel):
    response: str
    citations: list[dict[str, Any]] = []
    confidence: float
    processing_time_ms: float


# Health Check Endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.APP_VERSION,
        environment=settings.APP_ENV
    )


@app.get("/health/ready", response_model=HealthReadyResponse, tags=["Health"])
async def readiness_check():
    """Readiness check with dependency status."""
    redis_status = "disconnected"

    if redis_client:
        try:
            await redis_client.ping()
            redis_status = "connected"
        except Exception:
            redis_status = "error"

    return HealthReadyResponse(
        status="ready" if redis_status == "connected" else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        redis=redis_status,
        dependencies={
            "redis": redis_status,
            "database": "not_configured"
        }
    )


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "health": "/health"
    }


@app.post("/api/v1/query", response_model=QueryResponse, tags=["LLM"])
async def query_llm(request: QueryRequest):
    """
    Query the Solar PV LLM system.

    This endpoint processes natural language queries about solar PV systems
    and returns AI-generated responses with citations.
    """
    import time
    start_time = time.time()

    # TODO: Implement actual LLM query logic
    # This is a placeholder response
    response = QueryResponse(
        response=f"This is a placeholder response for: {request.query}",
        citations=[
            {
                "source": "Solar PV Handbook",
                "page": 42,
                "relevance": 0.95
            }
        ],
        confidence=0.85,
        processing_time_ms=(time.time() - start_time) * 1000
    )

    return response


@app.get("/api/v1/models", tags=["Models"])
async def list_models():
    """List available AI models."""
    return {
        "models": [
            {
                "id": "solar-pv-base",
                "name": "Solar PV Base Model",
                "version": "1.0.0",
                "status": "available"
            },
            {
                "id": "solar-pv-expert",
                "name": "Solar PV Expert Model",
                "version": "1.0.0",
                "status": "available"
            }
        ]
    }


@app.get("/metrics", tags=["Monitoring"])
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    # TODO: Implement actual Prometheus metrics
    return {
        "requests_total": 0,
        "requests_failed": 0,
        "request_latency_seconds": 0.0
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.DEBUG
    )
