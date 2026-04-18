"""Structured logging configuration with JSON formatting and correlation IDs.
Provides context-aware logging with automatic request tracking.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

import structlog
from pythonjsonlogger import jsonlogger

from app.config import settings


class CorrelationIdProcessor:
    """Add correlation ID to log records for request tracking."""

    def __init__(self):
        self._correlation_id: str | None = None

    def set_correlation_id(self, correlation_id: str):
        """Set the correlation ID for the current context."""
        self._correlation_id = correlation_id

    def clear_correlation_id(self):
        """Clear the correlation ID."""
        self._correlation_id = None

    def __call__(self, logger, method_name, event_dict):
        """Add correlation ID to event dict if present."""
        if self._correlation_id:
            event_dict["correlation_id"] = self._correlation_id
        return event_dict


# Global correlation ID processor
correlation_processor = CorrelationIdProcessor()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context fields."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ):
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["service"] = settings.app_name
        log_record["environment"] = settings.environment

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_record.update(record.extra_fields)


def setup_logging() -> None:
    """Configure structured logging for the application.
    Sets up both console and file handlers with JSON formatting.
    """
    # Create logs directory if it doesn't exist
    log_file_path = Path(settings.log_file_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    if settings.log_format.lower() == "json":
        # JSON formatter for structured logging
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(logger)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Standard text formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.log_file_path,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            correlation_processor,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "extra_fields": {
                "log_level": settings.log_level,
                "log_format": settings.log_format,
                "log_file": str(settings.log_file_path),
            },
        },
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured structlog logger instance

    """
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding temporary logging context."""

    def __init__(self, **kwargs):
        self.context = kwargs
        self._logger = None

    def __enter__(self):
        self._logger = structlog.get_logger()
        self._logger = self._logger.bind(**self.context)
        return self._logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Context is automatically cleared when the logger is garbage collected
        pass


def log_with_context(**context_kwargs):
    """Decorator to add context to all logs within a function.

    Usage:
        @log_with_context(user_id="123", operation="payment")
        def process_payment():
            logger.info("Processing payment")
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with LogContext(**context_kwargs):
                return func(*args, **kwargs)

        return wrapper

    return decorator
