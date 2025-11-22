"""
Logging Configuration
Structured JSON logging for production environments
"""

import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging():
    """Configure application-wide logging"""

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Set levels for external libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    return logger
