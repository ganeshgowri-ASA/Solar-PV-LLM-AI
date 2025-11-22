"""
Solar PV LLM AI - Main FastAPI Application
Includes LangSmith tracing, Prometheus metrics, and comprehensive monitoring
"""

import time
import os
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# LangSmith tracing
from langsmith import Client as LangSmithClient
from langchain.callbacks.tracers import LangChainTracer

# Logging
import structlog

# Local imports
from src.utils.metrics import MetricsCollector
from src.utils.langsmith_config import setup_langsmith
from src.models.solar_llm import SolarPVLLM

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Initialize metrics collector
metrics = MetricsCollector()

# Global LLM instance
llm_instance: Optional[SolarPVLLM] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global llm_instance

    # Startup
    logger.info("application_startup", message="Starting Solar PV LLM AI application")

    # Initialize LangSmith
    setup_langsmith()

    # Initialize LLM
    llm_instance = SolarPVLLM()

    logger.info("application_ready", message="Application is ready to serve requests")

    yield

    # Shutdown
    logger.info("application_shutdown", message="Shutting down application")


# Create FastAPI app
app = FastAPI(
    title="Solar PV LLM AI",
    description="AI-powered Solar PV system with RAG, citations, and monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for LLM queries"""
    query: str = Field(..., description="The user's question about Solar PV systems")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")
    include_citations: bool = Field(True, description="Whether to include citations in the response")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="LLM temperature parameter")


class QueryResponse(BaseModel):
    """Response model for LLM queries"""
    answer: str = Field(..., description="The AI-generated answer")
    citations: Optional[List[Dict[str, str]]] = Field(None, description="Source citations")
    confidence: float = Field(..., description="Confidence score (0-1)")
    latency_ms: float = Field(..., description="Query latency in milliseconds")
    trace_url: Optional[str] = Field(None, description="LangSmith trace URL")
    hallucination_score: float = Field(..., description="Estimated hallucination risk (0-1)")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime_seconds: float
    llm_status: str


# Middleware for request tracking
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Middleware to track all requests with metrics and logging"""
    start_time = time.time()

    # Increment request counter
    metrics.requests_total.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()

    # Log request
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client_host=request.client.host if request.client else "unknown"
    )

    try:
        response = await call_next(request)

        # Calculate latency
        latency = time.time() - start_time

        # Record latency
        metrics.request_latency.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(latency)

        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_seconds=latency
        )

        return response

    except Exception as e:
        # Increment error counter
        metrics.errors_total.labels(
            error_type=type(e).__name__,
            endpoint=request.url.path
        ).inc()

        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            error_type=type(e).__name__
        )

        raise


# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Solar PV LLM AI System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
        llm_status="ready" if llm_instance else "not_initialized"
    )


@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/query", response_model=QueryResponse)
async def query_llm(request: QueryRequest):
    """
    Query the LLM with a question about Solar PV systems
    Includes full tracing, metrics, and hallucination detection
    """
    start_time = time.time()

    if not llm_instance:
        raise HTTPException(status_code=503, detail="LLM not initialized")

    try:
        # Increment query counter
        metrics.llm_queries_total.inc()

        # Log query
        logger.info(
            "llm_query_started",
            query_length=len(request.query),
            include_citations=request.include_citations,
            temperature=request.temperature
        )

        # Execute query with LangSmith tracing
        result = await llm_instance.query(
            query=request.query,
            context=request.context,
            include_citations=request.include_citations,
            temperature=request.temperature
        )

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Record LLM latency
        metrics.llm_latency.observe(latency_ms / 1000)

        # Track hallucination score
        hallucination_score = result.get("hallucination_score", 0.0)
        metrics.hallucination_score.set(hallucination_score)

        # Increment hallucination counter if score is high
        if hallucination_score > 0.5:
            metrics.hallucinations_detected.inc()
            logger.warning(
                "high_hallucination_score",
                score=hallucination_score,
                query=request.query[:100]
            )

        # Track token usage
        if "token_usage" in result:
            metrics.llm_tokens_used.inc(result["token_usage"])

        # Log completion
        logger.info(
            "llm_query_completed",
            latency_ms=latency_ms,
            confidence=result.get("confidence", 0.0),
            hallucination_score=hallucination_score,
            has_citations=bool(result.get("citations"))
        )

        return QueryResponse(
            answer=result["answer"],
            citations=result.get("citations"),
            confidence=result.get("confidence", 0.0),
            latency_ms=latency_ms,
            trace_url=result.get("trace_url"),
            hallucination_score=hallucination_score
        )

    except Exception as e:
        # Increment error counter
        metrics.errors_total.labels(
            error_type=type(e).__name__,
            endpoint="/api/v1/query"
        ).inc()

        logger.error(
            "llm_query_failed",
            error=str(e),
            error_type=type(e).__name__,
            query=request.query[:100]
        )

        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/api/v1/feedback")
async def submit_feedback(
    trace_id: str,
    rating: int = Field(..., ge=1, le=5),
    comment: Optional[str] = None
):
    """Submit feedback for a specific query/response"""
    try:
        # Record feedback in LangSmith
        langsmith_client = LangSmithClient()
        langsmith_client.create_feedback(
            run_id=trace_id,
            key="user_rating",
            score=rating / 5.0,
            comment=comment
        )

        logger.info(
            "feedback_submitted",
            trace_id=trace_id,
            rating=rating,
            has_comment=bool(comment)
        )

        return {"status": "success", "message": "Feedback recorded"}

    except Exception as e:
        logger.error("feedback_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")


# Initialize start time
@app.on_event("startup")
async def set_start_time():
    """Set application start time"""
    app.state.start_time = time.time()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
