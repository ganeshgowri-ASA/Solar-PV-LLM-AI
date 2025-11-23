"""Main application entry point for Solar PV LLM AI Vector Store API"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.config.settings import settings
from src.api.routes import router
from src.logging.logger import setup_logger
from src.utils.errors import SolarPVAIException

# Set up logging
logger = setup_logger(
    "solar_pv_llm_ai",
    level=settings.LOG_LEVEL,
    log_format=settings.LOG_FORMAT
)


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="""
    Solar PV LLM AI - Vector Store API

    This API provides vector store capabilities for Solar PV documentation and knowledge:
    - Document ingestion with automatic embedding generation
    - Similarity search with metadata filtering
    - Support for Solar PV specific filters (standards, clauses, test types)
    - Vector deletion and index statistics

    Powered by:
    - OpenAI text-embedding-3-large (1536 dimensions)
    - Pinecone vector database (cosine similarity)
    - FastAPI
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(SolarPVAIException)
async def solar_pv_exception_handler(request, exc: SolarPVAIException):
    """Handle application-specific exceptions"""
    logger.error(f"Application error: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(router)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Pinecone Index: {settings.PINECONE_INDEX_NAME}")
    logger.info(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    logger.info(f"Embedding Dimension: {settings.EMBEDDING_DIMENSION}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info(f"Shutting down {settings.API_TITLE}")


def main():
    """Main entry point"""
    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")

    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
