"""Main entry point for the LLM orchestrator service."""

import uvicorn
from src.orchestrator.api import create_app
from src.orchestrator.config import settings

# Create FastAPI app
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
