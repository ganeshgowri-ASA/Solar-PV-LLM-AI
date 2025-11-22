#!/usr/bin/env python
"""
Application runner script.
Starts the FastAPI application with uvicorn.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Run the FastAPI application."""
    import uvicorn
    from app.core.config import settings

    print("=" * 80)
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 80)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Server: http://{settings.HOST}:{settings.PORT}")
    print(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"Health Check: http://{settings.HOST}:{settings.PORT}/health")
    print("=" * 80)

    # Create required directories
    directories = [
        Path(settings.CHROMA_PERSIST_DIRECTORY),
        Path(settings.IMAGE_UPLOAD_DIR),
        Path(settings.DOCUMENT_UPLOAD_DIR),
        Path(settings.LOG_FILE).parent,
        Path("data"),
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ready: {directory}")

    print("=" * 80)
    print("Starting server...")
    print()

    # Run uvicorn server
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError starting application: {e}", file=sys.stderr)
        sys.exit(1)
