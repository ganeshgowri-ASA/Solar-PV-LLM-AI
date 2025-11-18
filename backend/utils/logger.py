"""
Logging configuration for the application
"""
import logging
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger

from backend.config import get_settings


def setup_logging(log_file: Optional[str] = None):
    """
    Configure application logging

    Args:
        log_file: Optional path to log file
    """
    settings = get_settings()

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level))

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))

    # Format based on configuration
    if settings.log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file or settings.log_file:
        file_path = log_file or settings.log_file
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(getattr(logging, settings.log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {file_path}")

    logger.info(f"Logging configured: level={settings.log_level}, format={settings.log_format}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
