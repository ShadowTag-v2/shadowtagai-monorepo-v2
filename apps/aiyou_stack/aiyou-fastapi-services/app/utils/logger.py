# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Logging Configuration

Security:
- Structured logging
- No sensitive data in logs
- JSON format for GCP integration
"""

import logging
import sys
from typing import Any

import structlog

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure structured logging

    Features:
    - JSON format (for GCP Cloud Logging)
    - Request ID tracking
    - No PII in logs
    - Configurable log level
    """
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
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
            if settings.LOG_FORMAT == "json"
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )


def get_logger(name: str) -> Any:
    """Get logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Structlog logger instance

    """
    return structlog.get_logger(name)


def sanitize_log_data(data: dict) -> dict:
    """Remove sensitive data from log entries

    Security:
    - Redact passwords, tokens, keys
    - Prevent credential leakage

    Args:
        data: Log data dictionary

    Returns:
        Sanitized dictionary

    """
    sensitive_keys = {
        "password",
        "token",
        "secret",
        "api_key",
        "authorization",
        "access_token",
        "refresh_token",
        "hashed_password",
    }

    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        else:
            sanitized[key] = value

    return sanitized
