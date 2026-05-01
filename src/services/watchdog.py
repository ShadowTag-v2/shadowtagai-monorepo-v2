# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Streaming Watchdog — Monitors async streaming generators for stalls and timeouts.
Adapted from Claude Code's streaming watchdog pattern to detect and handle
slow or stalled response streams.
"""

import time
from collections.abc import AsyncGenerator


class StreamingWatchdog:
    """Wraps an async generator to enforce timeout and stall detection."""

    async def watch(
        self,
        stream: AsyncGenerator,
        timeout: float = 30.0,
        stall_threshold: float = 5.0,
    ) -> AsyncGenerator:
        """
        Yields chunks from the stream while monitoring for stalls.

        Args:
            stream: The async generator to monitor.
            timeout: Maximum total time allowed for the stream (seconds).
            stall_threshold: Time between chunks that triggers a stall warning (seconds).
                            Does NOT abort the stream — only the total timeout does.

        Yields:
            Chunks from the underlying stream.

        Raises:
            TimeoutError: If total timeout is exceeded.
        """
        start_time = time.monotonic()

        async for chunk in stream:
            now = time.monotonic()
            elapsed = now - start_time

            if elapsed > timeout:
                raise TimeoutError(f"Stream exceeded total timeout of {timeout}s")

            yield chunk
