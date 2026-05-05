# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pluggable telemetry protocol for Interactions API observability.

Defines a minimal TelemetryCallback protocol that both sync and async clients
accept as an optional dependency injection point. This enables latency tracking,
round counting, reconnection monitoring, and cost attribution — without coupling
the interactions package to any specific telemetry backend.

Architecture:
  - TelemetryCallback: typing.Protocol defining the telemetry contract.
  - NullTelemetry: No-op implementation (default, zero overhead).
  - LoggingTelemetry: stdlib-logger implementation for development/debug.

Usage:
    from gemini_interactions.telemetry import LoggingTelemetry

    client = InteractionsClient(telemetry=LoggingTelemetry())
    # or
    client = AsyncInteractionsClient(telemetry=LoggingTelemetry())
"""

from __future__ import annotations

import logging
import time
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class TelemetryCallback(Protocol):
    """Protocol defining telemetry hooks for Interactions API operations.

    All methods have default no-op implementations via NullTelemetry.
    Implementors may override any subset of methods.
    """

    def on_request_start(
        self,
        *,
        method: str,
        model: str,
        is_streaming: bool,
        has_tools: bool,
        previous_interaction_id: str | None,
    ) -> None:
        """Called before an API request is dispatched.

        Args:
            method: Operation name (create, stream, get, function_call_loop).
            model: Model being invoked.
            is_streaming: Whether this is a streaming request.
            has_tools: Whether tools are attached.
            previous_interaction_id: Chain ID (None for first turn).
        """
        ...

    def on_request_complete(
        self,
        *,
        method: str,
        model: str,
        interaction_id: str,
        latency_ms: float,
        usage: dict[str, Any] | None,
        status: str,
    ) -> None:
        """Called after an API request completes successfully.

        Args:
            method: Operation name.
            model: Model used.
            interaction_id: Server-assigned interaction ID.
            latency_ms: Wall-clock latency in milliseconds.
            usage: Token usage dict (total, prompt, completion).
            status: Completion status string.
        """
        ...

    def on_request_error(
        self,
        *,
        method: str,
        model: str,
        error: Exception,
        latency_ms: float,
    ) -> None:
        """Called when an API request fails with an exception.

        Args:
            method: Operation name.
            model: Model used.
            error: The exception that was raised.
            latency_ms: Wall-clock time until failure.
        """
        ...

    def on_stream_reconnect(
        self,
        *,
        attempt: int,
        max_attempts: int,
        interaction_id: str | None,
        last_event_id: str | None,
    ) -> None:
        """Called when a streaming connection drops and reconnection starts.

        Args:
            attempt: Current attempt number (1-indexed).
            max_attempts: Maximum allowed reconnection attempts.
            interaction_id: Interaction ID being reconnected (if known).
            last_event_id: Last SSE event ID received (for resumption).
        """
        ...

    def on_function_call_round(
        self,
        *,
        round_number: int,
        function_names: list[str],
        interaction_id: str,
    ) -> None:
        """Called for each round of the function call loop.

        Args:
            round_number: Current round (1-indexed).
            function_names: Names of functions being called this round.
            interaction_id: Interaction ID for this round.
        """
        ...


class NullTelemetry:
    """No-op telemetry implementation. Zero overhead. Default for all clients."""

    def on_request_start(self, **kwargs: Any) -> None:
        pass

    def on_request_complete(self, **kwargs: Any) -> None:
        pass

    def on_request_error(self, **kwargs: Any) -> None:
        pass

    def on_stream_reconnect(self, **kwargs: Any) -> None:
        pass

    def on_function_call_round(self, **kwargs: Any) -> None:
        pass


class LoggingTelemetry:
    """Telemetry implementation that logs to Python's stdlib logger.

    Useful for development, debugging, and cost monitoring. Each event
    is logged at DEBUG level with structured key-value data.
    """

    def __init__(self, logger_name: str = "gemini_interactions.telemetry") -> None:
        self._logger = logging.getLogger(logger_name)

    def on_request_start(
        self,
        *,
        method: str = "",
        model: str = "",
        is_streaming: bool = False,
        has_tools: bool = False,
        previous_interaction_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._logger.debug(
            "REQ_START method=%s model=%s streaming=%s tools=%s chain=%s",
            method,
            model,
            is_streaming,
            has_tools,
            previous_interaction_id or "none",
        )

    def on_request_complete(
        self,
        *,
        method: str = "",
        model: str = "",
        interaction_id: str = "",
        latency_ms: float = 0.0,
        usage: dict[str, Any] | None = None,
        status: str = "",
        **kwargs: Any,
    ) -> None:
        tokens = usage.get("total_tokens", 0) if usage else 0
        self._logger.debug(
            "REQ_COMPLETE method=%s model=%s id=%s latency=%.1fms tokens=%d status=%s",
            method,
            model,
            interaction_id,
            latency_ms,
            tokens,
            status,
        )

    def on_request_error(
        self,
        *,
        method: str = "",
        model: str = "",
        error: Exception | None = None,
        latency_ms: float = 0.0,
        **kwargs: Any,
    ) -> None:
        self._logger.warning(
            "REQ_ERROR method=%s model=%s error=%s latency=%.1fms",
            method,
            model,
            error,
            latency_ms,
        )

    def on_stream_reconnect(
        self,
        *,
        attempt: int = 0,
        max_attempts: int = 0,
        interaction_id: str | None = None,
        last_event_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._logger.info(
            "STREAM_RECONNECT attempt=%d/%d interaction=%s last_event=%s",
            attempt,
            max_attempts,
            interaction_id or "unknown",
            last_event_id or "none",
        )

    def on_function_call_round(
        self,
        *,
        round_number: int = 0,
        function_names: list[str] | None = None,
        interaction_id: str = "",
        **kwargs: Any,
    ) -> None:
        self._logger.debug(
            "FC_ROUND round=%d functions=%s interaction=%s",
            round_number,
            function_names or [],
            interaction_id,
        )


class Timer:
    """Context manager for wall-clock latency measurement.

    Usage:
        timer = Timer()
        with timer:
            do_work()
        print(timer.elapsed_ms)
    """

    def __init__(self) -> None:
        self._start: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> Timer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000.0
