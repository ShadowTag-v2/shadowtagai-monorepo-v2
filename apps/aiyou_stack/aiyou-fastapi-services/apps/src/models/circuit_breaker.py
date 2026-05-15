"""Circuit Breaker pattern for model serving."""

import logging
import time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if recovered


@dataclass
class BreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0  # seconds
    half_open_max_calls: int = 3


class CircuitBreaker:
    def __init__(self, name: str, config: BreakerConfig = None):
        self.name = name
        self.config = config or BreakerConfig()
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0
        self.half_open_calls = 0

    @property
    def is_open(self) -> bool:
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.config.recovery_timeout:
                self._transition_to_half_open()
                return False  # Allow probe
            return True
        return False

    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.config.half_open_max_calls:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            self.failures = 0

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.CLOSED:
            if self.failures >= self.config.failure_threshold:
                self._transition_to_open()
        elif self.state == CircuitState.HALF_OPEN:
            self._transition_to_open()

    def _transition_to_open(self):
        self.state = CircuitState.OPEN
        logger.warning(f"Circuit breaker {self.name} opened")

    def _transition_to_half_open(self):
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        logger.info(f"Circuit breaker {self.name} half-open (probing)")

    def _transition_to_closed(self):
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.half_open_calls = 0
        logger.info(f"Circuit breaker {self.name} closed (recovered)")


# Global registry of breakers
_breakers: dict[str, CircuitBreaker] = {}


def get_breaker_for_model(model_id: str) -> CircuitBreaker:
    if model_id not in _breakers:
        _breakers[model_id] = CircuitBreaker(model_id)
    return _breakers[model_id]
