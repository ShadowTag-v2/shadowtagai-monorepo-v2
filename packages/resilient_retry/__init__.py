# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Resilient Retry — battle-tested API retry pipeline.

Architecture (ported from Claude Code v2.1.91 services/api/withRetry.ts):
  - Exponential backoff with 25% jitter (BASE_DELAY_MS=500)
  - Retry-After header parsing (seconds → ms)
  - Rate-limit reset delay (anthropic-ratelimit-unified-reset header)
  - Circuit breaker on consecutive 529 overloaded errors (MAX_529_RETRIES=3)
  - Model fallback on repeated overload (original → fallback model)
  - Max-tokens context overflow auto-adjustment
  - Persistent retry mode for unattended sessions (6h reset cap)
  - Foreground vs background query source classification
  - Stale connection detection (ECONNRESET/EPIPE)
  - Cloud auth error cycling (AWS/GCP/OAuth token refresh)

Public API:
  - with_retry: Core retry generator (async generator)
  - RetryConfig: Configuration dataclass
  - RetryContext: Mutable per-attempt context
  - RetryDelay: Delay calculation utilities
  - CannotRetryError: Terminal error wrapper
  - FallbackTriggeredError: Model fallback trigger
  - is_retryable_status: HTTP status → retry decision
  - get_retry_delay: Backoff calculation with jitter
  - parse_context_overflow: Max tokens overflow extraction
"""

from resilient_retry.retry_engine import (
  BASE_DELAY_MS,
  DEFAULT_MAX_RETRIES,
  FLOOR_OUTPUT_TOKENS,
  MAX_529_RETRIES,
  CannotRetryError,
  FallbackTriggeredError,
  RetryConfig,
  RetryContext,
  RetryEvent,
  RetryOutcome,
  RetryState,
  get_retry_delay,
  is_overloaded_error,
  is_retryable_status,
  is_transient_capacity_error,
  parse_context_overflow,
  with_retry,
)

__all__ = [
  # Core
  "with_retry",
  "RetryConfig",
  "RetryContext",
  "RetryState",
  "RetryEvent",
  "RetryOutcome",
  # Errors
  "CannotRetryError",
  "FallbackTriggeredError",
  # Utilities
  "get_retry_delay",
  "is_retryable_status",
  "is_overloaded_error",
  "is_transient_capacity_error",
  "parse_context_overflow",
  # Constants
  "BASE_DELAY_MS",
  "DEFAULT_MAX_RETRIES",
  "FLOOR_OUTPUT_TOKENS",
  "MAX_529_RETRIES",
]
