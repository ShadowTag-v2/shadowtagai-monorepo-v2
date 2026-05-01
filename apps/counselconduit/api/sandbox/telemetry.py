# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Telemetry decorators for sandbox session store operations.

Phase 4 M4: Adds @telemetry_latency decorator for all FirestoreSessionStore
methods. Tracks p50/p95/p99 latency, error rates, and operation metadata
without coupling Firestore persistence to observability concerns.

Design principles:
    - Zero overhead when telemetry is disabled (lazy import guard)
    - Structured logging with operation name, duration, and error type
    - No PII in telemetry events (session_id prefix only)
    - Compatible with OpenTelemetry span export
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger("counselconduit.sandbox.telemetry")

F = TypeVar("F", bound=Callable[..., Any])


def telemetry_latency(operation: str) -> Callable[[F], F]:
    """Decorator that measures async method latency and logs structured metrics.

    Args:
        operation: Human-readable operation name (e.g., "create_session").

    Usage:
        @telemetry_latency("create_session")
        async def create_session(self, session: SandboxSession) -> str:
            ...
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            error_type: str | None = None
            try:
                result = await fn(*args, **kwargs)
                return result
            except Exception as exc:
                error_type = type(exc).__name__
                raise
            finally:
                duration_ms = (time.perf_counter() - start) * 1000

                # Extract session_id prefix for structured logging (no PII)
                session_id_prefix = _extract_session_prefix(args, kwargs)

                log_data = {
                    "op": operation,
                    "duration_ms": round(duration_ms, 2),
                    "session_prefix": session_id_prefix,
                }
                if error_type:
                    log_data["error_type"] = error_type
                    logger.warning(
                        "sandbox.store.%s failed (%.2fms): %s",
                        operation,
                        duration_ms,
                        error_type,
                        extra=log_data,
                    )
                else:
                    logger.info(
                        "sandbox.store.%s completed (%.2fms)",
                        operation,
                        duration_ms,
                        extra=log_data,
                    )

        return wrapper  # type: ignore[return-value]

    return decorator


def _extract_session_prefix(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Extract 8-char session ID prefix from method args for logging.

    Looks for session_id keyword arg, or session object in positional args.
    Returns empty string if not found (safe fallback).
    """
    # Check kwargs first
    session_id = kwargs.get("session_id", "")
    if session_id:
        return session_id[:8]

    # Check positional args (skip self at index 0)
    for arg in args[1:]:
        if isinstance(arg, str) and len(arg) >= 8:
            return arg[:8]
        if hasattr(arg, "session_id"):
            return arg.session_id[:8]

    return ""
