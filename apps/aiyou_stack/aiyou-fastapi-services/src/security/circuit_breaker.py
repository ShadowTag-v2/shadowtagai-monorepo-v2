"""
Circuit Breaker pattern for agent governance with graceful degradation.

Implements resilient fallback when agent system experiences failures,
with automatic recovery testing and OPA rule engine fallback.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

import redis

from src.gov_config import settings


class CircuitState(StrEnum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures exceeded, blocking calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitMetrics:
    """Metrics for circuit breaker monitoring."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    last_failure_time: float | None = None
    last_state_change: float = field(default_factory=time.time)

    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls


class AgentCircuitBreaker:
    """
    Circuit breaker for agent governance system.

    Monitors agent health and automatically fails over to OPA rules
    when error thresholds exceeded.

    States:
    - CLOSED: Normal operation, failures counted
    - OPEN: Threshold exceeded, calls blocked, fallback used
    - HALF_OPEN: Testing recovery with limited requests

    Transitions:
    - Closed → Open: Consecutive failures exceed threshold
    - Open → Half-Open: Timeout period expires
    - Half-Open → Closed: Test requests succeed
    - Half-Open → Open: Test requests fail
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = None,
        timeout_seconds: int = None,
        half_open_max_calls: int = 3,
        redis_client: redis.Redis | None = None,
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Identifier for this circuit
            failure_threshold: Consecutive failures before opening
            timeout_seconds: Seconds before attempting recovery
            half_open_max_calls: Test calls in half-open state
            redis_client: Redis for distributed state (optional)
        """
        self.name = name
        self.failure_threshold = failure_threshold or settings.circuit_breaker_failure_threshold
        self.timeout_seconds = timeout_seconds or settings.circuit_breaker_timeout_seconds
        self.half_open_max_calls = half_open_max_calls

        # State management
        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()
        self.half_open_calls = 0

        # Redis for distributed deployments
        self.redis = redis_client
        if self.redis:
            self._load_state_from_redis()

    def call(
        self,
        func: Callable,
        fallback: Callable | None = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Primary function to call (agent decision)
            fallback: Fallback function if circuit open (OPA rules)
            *args, **kwargs: Arguments for function

        Returns:
            Result from func or fallback

        Raises:
            Exception if circuit open and no fallback provided
        """
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if not self._should_attempt_reset():
                # Circuit still open, use fallback
                if fallback:
                    return self._execute_fallback(fallback, *args, **kwargs)
                raise Exception(f"Circuit {self.name} is OPEN, no fallback provided")

            # Attempt reset to half-open
            self._transition_to_half_open()

        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure(e)

            # Use fallback if available
            if fallback:
                return self._execute_fallback(fallback, *args, **kwargs)
            raise

    def _on_success(self) -> None:
        """Record successful call."""
        self.metrics.total_calls += 1
        self.metrics.successful_calls += 1
        self.metrics.consecutive_failures = 0

        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1

            # Enough successful test calls, close circuit
            if self.half_open_calls >= self.half_open_max_calls:
                self._transition_to_closed()

        self._save_state_to_redis()

    def _on_failure(self, exception: Exception) -> None:
        """Record failed call."""
        self.metrics.total_calls += 1
        self.metrics.failed_calls += 1
        self.metrics.consecutive_failures += 1
        self.metrics.last_failure_time = time.time()

        # Check if should open circuit
        if self.metrics.consecutive_failures >= self.failure_threshold:
            self._transition_to_open()

        elif self.state == CircuitState.HALF_OPEN:
            # Test call failed, reopen circuit
            self._transition_to_open()

        self._save_state_to_redis()

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.metrics.last_failure_time is None:
            return True

        elapsed = time.time() - self.metrics.last_failure_time
        return elapsed >= self.timeout_seconds

    def _transition_to_open(self) -> None:
        """Transition circuit to OPEN state."""
        self.state = CircuitState.OPEN
        self.metrics.last_state_change = time.time()
        print(f"⚠️  Circuit {self.name} → OPEN (failures: {self.metrics.consecutive_failures})")

    def _transition_to_half_open(self) -> None:
        """Transition circuit to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        self.metrics.last_state_change = time.time()
        print(f"🔄 Circuit {self.name} → HALF_OPEN (testing recovery)")

    def _transition_to_closed(self) -> None:
        """Transition circuit to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.metrics.consecutive_failures = 0
        self.half_open_calls = 0
        self.metrics.last_state_change = time.time()
        print(f"✅ Circuit {self.name} → CLOSED (recovered)")

    def _execute_fallback(
        self,
        fallback: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute fallback function."""
        print(f"🔀 Circuit {self.name} using fallback")
        return fallback(*args, **kwargs)

    def _load_state_from_redis(self) -> None:
        """Load circuit state from Redis (distributed mode)."""
        if not self.redis:
            return

        try:
            state_key = f"circuit:{self.name}:state"
            state_data = self.redis.get(state_key)

            if state_data:
                import json

                data = json.loads(state_data)
                self.state = CircuitState(data.get("state", "closed"))
                self.metrics.consecutive_failures = data.get("consecutive_failures", 0)
                self.metrics.last_failure_time = data.get("last_failure_time")

        except Exception as e:
            print(f"Failed to load circuit state from Redis: {e}")

    def _save_state_to_redis(self) -> None:
        """Save circuit state to Redis (distributed mode)."""
        if not self.redis:
            return

        try:
            import json

            state_key = f"circuit:{self.name}:state"
            state_data = {
                "state": self.state.value,
                "consecutive_failures": self.metrics.consecutive_failures,
                "last_failure_time": self.metrics.last_failure_time,
                "last_state_change": self.metrics.last_state_change,
            }

            self.redis.setex(
                state_key,
                timedelta(hours=24),  # Expire after 24h
                json.dumps(state_data),
            )

        except Exception as e:
            print(f"Failed to save circuit state to Redis: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get current circuit breaker metrics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self.metrics.total_calls,
            "successful_calls": self.metrics.successful_calls,
            "failed_calls": self.metrics.failed_calls,
            "consecutive_failures": self.metrics.consecutive_failures,
            "error_rate": self.metrics.error_rate,
            "success_rate": self.metrics.success_rate,
            "last_failure_time": (
                datetime.fromtimestamp(self.metrics.last_failure_time).isoformat()
                if self.metrics.last_failure_time
                else None
            ),
            "last_state_change": datetime.fromtimestamp(self.metrics.last_state_change).isoformat(),
        }

    def reset(self) -> None:
        """Manually reset circuit breaker."""
        self._transition_to_closed()
        self.metrics = CircuitMetrics()


class AgentHealthChecker:
    """
    Health checker for agent governance system.

    Monitors agent performance metrics and opens circuit if degraded.
    """

    def __init__(
        self,
        max_latency_ms: int = 5000,
        max_error_rate: float = 0.05,
        min_confidence: float = 0.5,
    ):
        self.max_latency_ms = max_latency_ms
        self.max_error_rate = max_error_rate
        self.min_confidence = min_confidence

    def check_health(self, agent_metrics: dict[str, Any]) -> bool:
        """
        Check if agent is healthy based on metrics.

        Args:
            agent_metrics: Metrics from agent execution

        Returns:
            True if healthy, False if degraded
        """
        # Check latency
        if agent_metrics.get("latency_ms", 0) > self.max_latency_ms:
            print(f"⚠️  Agent latency exceeded: {agent_metrics['latency_ms']}ms")
            return False

        # Check error rate (if available)
        error_rate = agent_metrics.get("error_rate", 0.0)
        if error_rate > self.max_error_rate:
            print(f"⚠️  Agent error rate exceeded: {error_rate:.2%}")
            return False

        # Check confidence (if available)
        confidence = agent_metrics.get("confidence_score", 1.0)
        if confidence < self.min_confidence:
            print(f"⚠️  Agent confidence too low: {confidence:.2f}")
            return False

        return True
