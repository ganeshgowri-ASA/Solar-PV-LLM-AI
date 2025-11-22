"""
Solar PV LLM AI - FastAPI Backend
Main application entry point.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .routers import chat_router, search_router, calculator_router, image_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Solar PV LLM AI Backend...")
    logger.info("All services initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down Solar PV LLM AI Backend...")


# Create FastAPI application
app = FastAPI(
    title="Solar PV LLM AI",
    description="""
    AI-powered Solar PV Assistant API

    ## Features
    - **Chat**: Ask questions about solar PV systems with AI-powered responses
    - **Search**: Search solar PV standards and regulations
    - **Calculator**: Perform solar PV calculations (sizing, ROI, etc.)
    - **Image Analysis**: Analyze solar panel images for issues

    ## Authentication
    Currently open for development. Production will require API keys.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit default
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(search_router)
app.include_router(calculator_router)
app.include_router(image_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Solar PV LLM AI",
        "version": "1.0.0",
        "description": "AI-powered Solar PV Assistant",
        "documentation": "/docs",
        "endpoints": {
            "chat": "/chat/query",
            "chat_stream": "/chat/query/stream",
            "chat_websocket": "/chat/ws/{conversation_id}",
            "search": "/search/standards",
            "calculator": "/calculate",
            "image_analysis": "/analyze/image"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Overall system health check."""
    return {
        "status": "healthy",
        "services": {
            "chat": "operational",
            "search": "operational",
            "calculator": "operational",
            "image_analysis": "operational"
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )


# For running directly with: python -m backend.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
