# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""pnkln_file_search.monitoring.metrics — Metrics collection."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class MetricSample:
    """A single metric sample."""

    timestamp: float = 0.0
    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collects and aggregates operational metrics."""

    def __init__(self, window_size: int = 1000) -> None:
        self.window_size = window_size
        self._samples: deque[MetricSample] = deque(maxlen=window_size)
        self._counters: dict[str, int] = {}

    def record(self, name: str, value: float = 1.0, **labels: str) -> None:
        """Record a metric sample."""
        self._samples.append(MetricSample(timestamp=time.time(), value=value, labels=labels))

    def increment(self, name: str, amount: int = 1) -> None:
        """Increment a counter."""
        self._counters[name] = self._counters.get(name, 0) + amount

    def get_count(self, name: str) -> int:
        """Get counter value."""
        return self._counters.get(name, 0)

    @property
    def sample_count(self) -> int:
        """Return number of collected samples."""
        return len(self._samples)
