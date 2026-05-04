# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Internal Logging — Batch 6 port from Claude Code v2.1.91.

Structured internal logging with severity levels and PII guards.
Provides a safe logging interface that strips sensitive data.

Ported from: external_repos/claude_code_services/internalLogging.ts
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# PII patterns to redact
_PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.ASCII)),
    ("ipv4", re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", re.ASCII)),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", re.ASCII)),
    ("path_home", re.compile(r"/(?:Users|home)/[a-zA-Z0-9._-]+", re.ASCII)),
]


def redact_pii(text: str) -> str:
    """Strip PII from a log message.

    Args:
        text: Raw log message.

    Returns:
        Message with PII patterns redacted.
    """
    result = text
    for name, pattern in _PII_PATTERNS:
        result = pattern.sub(f"[REDACTED:{name}]", result)
    return result


def log_for_diagnostics(
    level: str,
    event: str,
    data: dict[str, Any] | None = None,
    *,
    strip_pii: bool = True,
) -> None:
    """Log a structured diagnostic event.

    This mirrors CC's logForDiagnosticsNoPII function, providing
    a structured logging interface with PII redaction.

    Args:
        level: Log level ("info", "warn", "error", "debug").
        event: Event identifier (e.g., "settings_sync_upload_success").
        data: Optional structured data to include.
        strip_pii: Whether to redact PII from the event string.
    """
    log_fn = getattr(logger, level, logger.info)
    event_str = redact_pii(event) if strip_pii else event

    if data:
        safe_data = {k: redact_pii(str(v)) if strip_pii else v for k, v in data.items()}
        log_fn("%s %s", event_str, safe_data)
    else:
        log_fn("%s", event_str)


def log_for_debugging(message: str, *, level: str = "debug") -> None:
    """Log a debug message (PII-safe by default).

    Args:
        message: Debug message to log.
        level: Log level override.
    """
    log_for_diagnostics(level, message, strip_pii=True)
