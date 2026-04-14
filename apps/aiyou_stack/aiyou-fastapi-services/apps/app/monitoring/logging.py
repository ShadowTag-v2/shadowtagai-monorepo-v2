"""Structured logging configuration."""

import logging
import sys

from pythonjsonlogger import jsonlogger

from app.config import settings


def setup_logging():
    """Configure structured JSON logging.

    Logs include:
    - Timestamp
    - Level
    - Message
    - Trace ID (if available)
    - Kernel name
    - Latency/metrics
    """
    logger = logging.getLogger()

    # Set log level from config
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers = []

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(trace_id)s %(kernel_name)s",
        rename_fields={
            "levelname": "level",
            "asctime": "timestamp",
        },
    )

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)
