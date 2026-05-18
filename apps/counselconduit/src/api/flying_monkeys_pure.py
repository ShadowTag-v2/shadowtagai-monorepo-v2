# Copyright 2026 ShadowTag AI — All Rights Reserved.
# flying_monkeys_pure.py — Pure GCP Circuit Breaker (Zero GPT-4 Fallback)
#
# The FlyingMonkeySwarm traps 429/503 errors from primary Vertex AI endpoints
# and falls back EXCLUSIVELY to Gemini Flash — never to external OpenAI/Anthropic.

"""
FlyingMonkeySwarm — Pure GCP LLM Circuit Breaker

Eliminates the GPT-4 fallback vulnerability from the legacy codebase.
All routing stays within the Google Cloud Vertex AI ecosystem.

Primary: gemini-3.1-pro (via Vertex AI)
Fallback: gemini-3.1-flash-lite-preview-thinking (authorized runtime model)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CircuitState(Enum):
  CLOSED = "closed"  # Normal operation
  OPEN = "open"  # Tripped — routing to fallback
  HALF_OPEN = "half_open"  # Testing primary recovery


@dataclass
class CircuitBreakerConfig:
  """Configuration for the circuit breaker."""

  failure_threshold: int = 3  # Failures before tripping
  recovery_timeout_s: float = 60.0  # Seconds before half-open test
  half_open_max_calls: int = 1  # Test calls in half-open state
  rate_limit_backoff_s: float = 5.0  # Backoff on 429 errors


@dataclass
class CircuitBreaker:
  """Circuit breaker state machine for LLM endpoint protection."""

  config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
  state: CircuitState = CircuitState.CLOSED
  failure_count: int = 0
  last_failure_time: float = 0.0
  half_open_calls: int = 0

  def record_success(self) -> None:
    """Reset on successful call."""
    self.failure_count = 0
    self.half_open_calls = 0
    if self.state != CircuitState.CLOSED:
      logger.info("🟢 Circuit CLOSED — primary endpoint recovered")
      self.state = CircuitState.CLOSED

  def record_failure(self) -> None:
    """Track failure and potentially trip the breaker."""
    self.failure_count += 1
    self.last_failure_time = time.monotonic()

    if self.failure_count >= self.config.failure_threshold:
      logger.warning(
        "🔴 Circuit OPEN — %d failures exceeded threshold (%d). "
        "Routing to Gemini Flash fallback.",
        self.failure_count,
        self.config.failure_threshold,
      )
      self.state = CircuitState.OPEN

  def should_use_fallback(self) -> bool:
    """Determine if traffic should route to fallback."""
    if self.state == CircuitState.CLOSED:
      return False

    if self.state == CircuitState.OPEN:
      elapsed = time.monotonic() - self.last_failure_time
      if elapsed >= self.config.recovery_timeout_s:
        logger.info("🟡 Circuit HALF-OPEN — testing primary endpoint")
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        return False  # Allow test call through
      return True

    # HALF_OPEN: allow limited test calls
    if self.half_open_calls < self.config.half_open_max_calls:
      self.half_open_calls += 1
      return False
    return True


# ─── Model Registry (Pure GCP Only) ───────────────────────────────

PRIMARY_MODEL = "gemini-3.1-pro"
FALLBACK_MODEL = "gemini-3.1-flash-lite-preview-thinking"

# BANNED: "gpt-4", "gpt-4-turbo", "claude-3", "claude-4" — NEVER fallback to non-GCP


class FlyingMonkeySwarm:
  """
  Pure GCP LLM orchestrator with circuit breaker protection.

  Routes all inference through Vertex AI endpoints exclusively.
  Traps 429 (rate limit) and 503 (overloaded) errors and falls back
  to Gemini Flash — never to external providers.
  """

  def __init__(
    self, project_id: str = "shadowtag-omega-v4", location: str = "us-central1"
  ):
    self.project_id = project_id
    self.location = location
    self.breaker = CircuitBreaker()
    self._request_count = 0
    self._fallback_count = 0

  @property
  def stats(self) -> dict[str, Any]:
    """Return operational statistics."""
    return {
      "total_requests": self._request_count,
      "fallback_requests": self._fallback_count,
      "circuit_state": self.breaker.state.value,
      "failure_count": self.breaker.failure_count,
      "primary_model": PRIMARY_MODEL,
      "fallback_model": FALLBACK_MODEL,
    }

  async def invoke(
    self,
    prompt: str,
    *,
    max_tokens: int = 4096,
    temperature: float = 0.7,
  ) -> dict[str, Any]:
    """
    Invoke the LLM with circuit breaker protection.

    Returns dict with 'text', 'model_used', 'latency_ms' keys.
    """
    self._request_count += 1
    use_fallback = self.breaker.should_use_fallback()
    model = FALLBACK_MODEL if use_fallback else PRIMARY_MODEL

    if use_fallback:
      self._fallback_count += 1

    start = time.monotonic()

    try:
      result = await self._call_vertex(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
      )
      self.breaker.record_success()
      latency = (time.monotonic() - start) * 1000

      return {
        "text": result,
        "model_used": model,
        "latency_ms": round(latency, 2),
        "fallback": use_fallback,
      }

    except RateLimitError:
      logger.warning(
        "⚡ 429 Rate Limit on %s — backing off %.1fs",
        model,
        self.breaker.config.rate_limit_backoff_s,
      )
      self.breaker.record_failure()
      await asyncio.sleep(self.breaker.config.rate_limit_backoff_s)

      # Retry on fallback
      if model != FALLBACK_MODEL:
        return await self._retry_on_fallback(prompt, max_tokens, temperature, start)
      raise

    except ServiceOverloadedError:
      logger.warning("🔥 503 Overloaded on %s — circuit breaker engaged", model)
      self.breaker.record_failure()

      if model != FALLBACK_MODEL:
        return await self._retry_on_fallback(prompt, max_tokens, temperature, start)
      raise

  async def _retry_on_fallback(
    self, prompt: str, max_tokens: int, temperature: float, start: float
  ) -> dict[str, Any]:
    """Retry on Gemini Flash fallback after primary failure."""
    self._fallback_count += 1
    logger.info("♻️ Retrying on fallback model: %s", FALLBACK_MODEL)

    result = await self._call_vertex(
      model=FALLBACK_MODEL,
      prompt=prompt,
      max_tokens=max_tokens,
      temperature=temperature,
    )
    latency = (time.monotonic() - start) * 1000

    return {
      "text": result,
      "model_used": FALLBACK_MODEL,
      "latency_ms": round(latency, 2),
      "fallback": True,
    }

  async def _call_vertex(
    self,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
  ) -> str:
    """
    Call Vertex AI GenerativeModel endpoint.

    In production, this uses google-cloud-aiplatform SDK.
    Stubbed here for structural integration — replace with real SDK call.
    """
    # Production implementation:
    # from google.cloud import aiplatform
    # from vertexai.generative_models import GenerativeModel
    # aiplatform.init(project=self.project_id, location=self.location)
    # model_obj = GenerativeModel(model)
    # response = await model_obj.generate_content_async(prompt, ...)
    # return response.text

    logger.info(
      "[FlyingMonkey] model=%s prompt_len=%d max_tokens=%d temp=%.1f",
      model,
      len(prompt),
      max_tokens,
      temperature,
    )
    # Stub return for structural validation
    return f"[STUB:{model}] Response to: {prompt[:50]}..."


# ─── Custom Exceptions ────────────────────────────────────────────


class RateLimitError(Exception):
  """429 Too Many Requests from Vertex AI."""


class ServiceOverloadedError(Exception):
  """503 Service Unavailable from Vertex AI."""
