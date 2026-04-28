# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Logging configuration for the pipeline"""

from pathlib import Path

import structlog

from ..config import LOGGING_CONFIG


def setup_logging():
    """Configure structured logging"""
    # Ensure log directory exists
    log_file = Path(LOGGING_CONFIG["file"])
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
            if not LOGGING_CONFIG.get("console", True)
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Get root logger
    logger = structlog.get_logger(__name__)
    logger.info("logging_configured", log_file=str(log_file))

    return logger
