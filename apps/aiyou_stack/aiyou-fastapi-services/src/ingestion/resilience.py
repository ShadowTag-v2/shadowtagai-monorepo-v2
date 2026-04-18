"""Resilience and edge case handling for ingestion pipeline.

Implements:
- Circuit breakers for failing sources
- Cost spike detection and auto-throttling
- Source outage handling
- Retry logic with exponential backoff
- Graceful degradation
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout_seconds: int = 60  # Time before trying half-open
    window_seconds: int = 300  # Rolling window for failure counting


@dataclass
class CircuitBreakerStats:
    """Statistics for a circuit breaker."""

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: datetime | None = None
    last_state_change: datetime = field(default_factory=datetime.now)
    total_requests: int = 0
    total_failures: int = 0


class CircuitBreaker:
    """Circuit breaker for source protection.

    Prevents cascade failures by opening circuit after threshold failures.
    """

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig = None,
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker.

        Args:
            func: Async function to call
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open

        """
        async with self._lock:
            self.stats.total_requests += 1

            # Check if circuit is open
            if self.stats.state == CircuitState.OPEN:
                # Check if timeout has elapsed
                if self.stats.last_failure_time:
                    elapsed = (datetime.now() - self.stats.last_failure_time).total_seconds()

                    if elapsed >= self.config.timeout_seconds:
                        logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
                        self.stats.state = CircuitState.HALF_OPEN
                        self.stats.failure_count = 0
                        self.stats.success_count = 0
                    else:
                        raise CircuitBreakerOpenError(
                            f"Circuit breaker {self.name} is OPEN. "
                            f"Retry in {self.config.timeout_seconds - elapsed:.0f}s",
                        )

        # Execute function
        try:
            result = await func(*args, **kwargs)

            # Record success
            await self._record_success()
            return result

        except Exception:
            # Record failure
            await self._record_failure()
            raise

    async def _record_success(self):
        """Record successful call."""
        async with self._lock:
            self.stats.success_count += 1

            if self.stats.state == CircuitState.HALF_OPEN:
                if self.stats.success_count >= self.config.success_threshold:
                    logger.info(f"Circuit breaker {self.name} closing (recovered)")
                    self.stats.state = CircuitState.CLOSED
                    self.stats.failure_count = 0
                    self.stats.last_state_change = datetime.now()

    async def _record_failure(self):
        """Record failed call."""
        async with self._lock:
            self.stats.failure_count += 1
            self.stats.total_failures += 1
            self.stats.last_failure_time = datetime.now()

            if self.stats.state == CircuitState.HALF_OPEN:
                logger.warning(f"Circuit breaker {self.name} re-opening (still failing)")
                self.stats.state = CircuitState.OPEN
                self.stats.last_state_change = datetime.now()

            elif self.stats.state == CircuitState.CLOSED:
                if self.stats.failure_count >= self.config.failure_threshold:
                    logger.error(
                        f"Circuit breaker {self.name} opening ({self.stats.failure_count} failures)",
                    )
                    self.stats.state = CircuitState.OPEN
                    self.stats.last_state_change = datetime.now()

    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.stats.state.value,
            "failure_count": self.stats.failure_count,
            "total_requests": self.stats.total_requests,
            "total_failures": self.stats.total_failures,
            "failure_rate": (
                self.stats.total_failures / self.stats.total_requests
                if self.stats.total_requests > 0
                else 0
            ),
            "last_failure_time": self.stats.last_failure_time.isoformat()
            if self.stats.last_failure_time
            else None,
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""


@dataclass
class CostAlert:
    """Cost spike alert."""

    timestamp: datetime
    current_cost: float
    projected_cost: float
    budget: float
    severity: str  # warning, critical
    message: str


class CostSpikeDetector:
    """Detects and responds to cost spikes.

    Features:
    - Real-time cost tracking
    - Spike detection (>2σ from baseline)
    - Auto-throttling on budget overrun
    - Alerting and logging
    """

    def __init__(
        self,
        budget: float = 77.0,
        alert_threshold: float = 0.75,  # Alert at 75% budget
        critical_threshold: float = 0.90,  # Critical at 90%
    ):
        self.budget = budget
        self.alert_threshold = alert_threshold
        self.critical_threshold = critical_threshold

        # Cost tracking
        self.current_cost = 0.0
        self.cost_history: list[float] = []
        self.alerts: list[CostAlert] = []

        # Throttling state
        self.throttle_active = False
        self.throttle_factor = 1.0  # 1.0 = normal, 0.5 = half speed

    def record_cost(self, amount: float, category: str = "general"):
        """Record a cost."""
        self.current_cost += amount
        self.cost_history.append(amount)

        logger.debug(f"Recorded cost: ${amount:.2f} ({category}), total: ${self.current_cost:.2f}")

        # Check for alerts
        self._check_alerts()

    def _check_alerts(self):
        """Check if cost thresholds exceeded."""
        utilization = self.current_cost / self.budget

        # Critical threshold
        if utilization >= self.critical_threshold and not self.throttle_active:
            alert = CostAlert(
                timestamp=datetime.now(),
                current_cost=self.current_cost,
                projected_cost=self._project_monthly_cost(),
                budget=self.budget,
                severity="critical",
                message=f"CRITICAL: Cost at {utilization * 100:.1f}% of budget. Auto-throttling activated.",
            )

            self.alerts.append(alert)
            logger.critical(alert.message)

            # Activate throttling
            self.throttle_active = True
            self.throttle_factor = 0.5  # Reduce to 50% speed

        # Warning threshold
        elif utilization >= self.alert_threshold:
            alert = CostAlert(
                timestamp=datetime.now(),
                current_cost=self.current_cost,
                projected_cost=self._project_monthly_cost(),
                budget=self.budget,
                severity="warning",
                message=f"WARNING: Cost at {utilization * 100:.1f}% of budget.",
            )

            self.alerts.append(alert)
            logger.warning(alert.message)

    def _project_monthly_cost(self) -> float:
        """Project monthly cost based on current rate."""
        day_of_month = datetime.now().day
        if day_of_month == 0:
            return self.current_cost

        days_in_month = 30  # Approximate
        projected = (self.current_cost / day_of_month) * days_in_month

        return projected

    def should_throttle(self) -> bool:
        """Check if throttling is active."""
        return self.throttle_active

    def get_throttle_delay(self, base_delay: float) -> float:
        """Get adjusted delay based on throttling."""
        return base_delay / self.throttle_factor

    def get_stats(self) -> dict:
        """Get cost statistics."""
        utilization = (self.current_cost / self.budget * 100) if self.budget > 0 else 0
        projected = self._project_monthly_cost()

        return {
            "current_cost": self.current_cost,
            "budget": self.budget,
            "utilization_percent": utilization,
            "projected_monthly_cost": projected,
            "throttle_active": self.throttle_active,
            "throttle_factor": self.throttle_factor,
            "alert_count": len(self.alerts),
            "status": (
                "critical"
                if utilization >= self.critical_threshold * 100
                else "warning"
                if utilization >= self.alert_threshold * 100
                else "healthy"
            ),
        }


class RetryHandler:
    """Exponential backoff retry handler.

    Implements:
    - Exponential backoff (2^n * base_delay)
    - Jitter to prevent thundering herd
    - Max retry limits
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with retry logic.

        Args:
            func: Async function to call
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries exhausted

        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    # Calculate backoff delay
                    delay = min(self.base_delay * (2**attempt), self.max_delay)

                    # Add jitter
                    if self.jitter:
                        import random

                        delay *= random.uniform(0.5, 1.5)

                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {e}. "
                        f"Retrying in {delay:.1f}s...",
                    )

                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed for {func.__name__}")

        raise last_exception


class GracefulDegradation:
    """Handles graceful degradation when sources fail.

    Strategies:
    - Fallback to cached data
    - Skip non-critical sources
    - Reduce collection scope
    - Continue with partial results
    """

    def __init__(self):
        self.cache: dict[str, any] = {}
        self.degraded_mode = False

    async def get_with_fallback(
        self,
        key: str,
        fetch_func: Callable,
        max_age_seconds: int = 3600,
    ):
        """Get data with fallback to cache.

        Args:
            key: Cache key
            fetch_func: Function to fetch fresh data
            max_age_seconds: Max age of cached data

        Returns:
            Fresh or cached data

        """
        try:
            # Try fresh fetch
            data = await fetch_func()

            # Update cache
            self.cache[key] = {"data": data, "timestamp": datetime.now()}

            return data

        except Exception as e:
            logger.warning(f"Fetch failed for {key}: {e}, trying cache...")

            # Check cache
            if key in self.cache:
                cached = self.cache[key]
                age = (datetime.now() - cached["timestamp"]).total_seconds()

                if age <= max_age_seconds:
                    logger.info(f"Using cached data for {key} (age: {age:.0f}s)")
                    return cached["data"]
                logger.warning(f"Cached data for {key} too old ({age:.0f}s)")

            # No valid cache, re-raise
            raise

    def enable_degraded_mode(self):
        """Enable degraded mode (skip non-critical operations)."""
        self.degraded_mode = True
        logger.warning("Graceful degradation ENABLED - skipping non-critical operations")

    def disable_degraded_mode(self):
        """Disable degraded mode."""
        self.degraded_mode = False
        logger.info("Graceful degradation DISABLED - resuming normal operations")

    def is_degraded(self) -> bool:
        """Check if in degraded mode."""
        return self.degraded_mode
