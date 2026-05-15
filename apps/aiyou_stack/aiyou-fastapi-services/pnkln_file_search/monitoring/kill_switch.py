# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""pnkln_file_search.monitoring.kill_switch — Safety kill switch."""

from __future__ import annotations

import enum
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pnkln_file_search.monitoring.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class KillSwitchState(enum.Enum):
    """Kill switch states."""

    ACTIVE = "active"
    TRIPPED = "tripped"
    COOLDOWN = "cooldown"


class KillSwitch:
    """Safety mechanism to halt operations on excessive errors."""

    def __init__(
        self,
        metrics_collector: MetricsCollector,
        max_violations: int = 10,
        cooldown_seconds: float = 60.0,
    ) -> None:
        self.metrics = metrics_collector
        self.max_violations = max_violations
        self.cooldown_seconds = cooldown_seconds
        self.state = KillSwitchState.ACTIVE
        self.violation_count = 0

    def record_violation(self) -> KillSwitchState:
        """Record a violation and potentially trip the switch."""
        self.violation_count += 1
        if self.violation_count >= self.max_violations:
            self.state = KillSwitchState.TRIPPED
            logger.warning("Kill switch TRIPPED after %d violations", self.violation_count)
        return self.state

    def reset(self) -> None:
        """Reset the kill switch."""
        self.violation_count = 0
        self.state = KillSwitchState.ACTIVE

    def is_active(self) -> bool:
        """Check if operations should proceed."""
        return self.state == KillSwitchState.ACTIVE
