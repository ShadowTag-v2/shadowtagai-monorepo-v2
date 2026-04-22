"""Kill Switch Monitoring
Automatic fallback when file search degrades or fails
"""

from enum import Enum

import structlog

from pnkln_file_search.config.settings import get_settings
from pnkln_file_search.monitoring.metrics import MetricsCollector

logger = structlog.get_logger(__name__)


class KillSwitchState(Enum):
    """Kill switch states"""

    ACTIVE = "active"  # File search enabled
    DEGRADED = "degraded"  # File search experiencing issues
    DISABLED = "disabled"  # File search disabled, fallback to Judge 6 only


class KillSwitch:
    """Monitors file search health and automatically disables on degradation

    Monitors:
    1. File search P99 latency threshold
    2. Corpus sync failure rate
    3. False positive policy match rate

    When thresholds are exceeded, automatically disables file search
    and falls back to pure Judge 6 enforcement.
    """

    def __init__(self, metrics_collector: MetricsCollector | None = None):
        """Initialize kill switch

        Args:
            metrics_collector: Optional metrics collector (creates new if None)

        """
        self.settings = get_settings()
        self.metrics = metrics_collector or MetricsCollector()
        self.state = KillSwitchState.ACTIVE

        # Thresholds
        self.max_p99_latency = self.settings.kill_switch_file_search_p99_latency
        self.max_sync_failure_rate = self.settings.kill_switch_corpus_sync_failure_rate
        self.max_false_positive_rate = self.settings.kill_switch_false_positive_rate

        # Violation tracking
        self.violation_count = 0
        self.max_violations_before_disable = 3  # Disable after 3 consecutive violations

        logger.info(
            "kill_switch_initialized",
            max_p99_latency=self.max_p99_latency,
            max_sync_failure_rate=self.max_sync_failure_rate,
            max_false_positive_rate=self.max_false_positive_rate,
        )

    def check_health(self) -> dict:
        """Check file search health against thresholds

        Returns:
            Health check results with status and violations

        """
        metrics_summary = self.metrics.get_metrics_summary()

        violations = []

        # Check P99 latency
        file_search_p99 = metrics_summary["file_search"]["p99_latency_ms"]
        if file_search_p99 > self.max_p99_latency:
            violations.append(
                {
                    "type": "latency",
                    "threshold": self.max_p99_latency,
                    "actual": file_search_p99,
                    "message": f"File search P99 latency ({file_search_p99:.1f}ms) "
                    f"exceeds threshold ({self.max_p99_latency}ms)",
                },
            )

        # Check corpus sync failure rate
        sync_failure_rate = metrics_summary["corpus"]["sync_failure_rate"]
        if sync_failure_rate > self.max_sync_failure_rate:
            violations.append(
                {
                    "type": "sync_failure",
                    "threshold": self.max_sync_failure_rate,
                    "actual": sync_failure_rate,
                    "message": f"Corpus sync failure rate ({sync_failure_rate:.2%}) "
                    f"exceeds threshold ({self.max_sync_failure_rate:.2%})",
                },
            )

        # Check false positive rate
        false_positive_rate = metrics_summary["accuracy"]["false_positive_rate"]
        if false_positive_rate > self.max_false_positive_rate:
            violations.append(
                {
                    "type": "false_positive",
                    "threshold": self.max_false_positive_rate,
                    "actual": false_positive_rate,
                    "message": f"False positive rate ({false_positive_rate:.2%}) "
                    f"exceeds threshold ({self.max_false_positive_rate:.2%})",
                },
            )

        # Update state based on violations
        if violations:
            self.violation_count += 1
            logger.warning(
                "kill_switch_violations_detected",
                violations=len(violations),
                consecutive_violations=self.violation_count,
                details=violations,
            )

            if self.violation_count >= self.max_violations_before_disable:
                self._disable()
            elif self.state == KillSwitchState.ACTIVE:
                self._degrade()
        else:
            # Reset violation count on healthy check
            if self.violation_count > 0:
                logger.info("kill_switch_violations_cleared")
            self.violation_count = 0
            if self.state != KillSwitchState.ACTIVE:
                self._activate()

        return {
            "state": self.state.value,
            "healthy": len(violations) == 0,
            "violations": violations,
            "consecutive_violation_count": self.violation_count,
            "metrics": metrics_summary,
        }

    def _activate(self) -> None:
        """Activate file search (normal operation)"""
        if self.state != KillSwitchState.ACTIVE:
            self.state = KillSwitchState.ACTIVE
            logger.info("kill_switch_activated", state="active")

    def _degrade(self) -> None:
        """Mark file search as degraded"""
        if self.state != KillSwitchState.DEGRADED:
            self.state = KillSwitchState.DEGRADED
            logger.warning("kill_switch_degraded", state="degraded")

    def _disable(self) -> None:
        """Disable file search (fallback to Judge 6 only)"""
        if self.state != KillSwitchState.DISABLED:
            self.state = KillSwitchState.DISABLED
            logger.error(
                "kill_switch_disabled",
                state="disabled",
                reason="Threshold violations exceeded",
                consecutive_violations=self.violation_count,
            )

    def is_enabled(self) -> bool:
        """Check if file search is enabled

        Returns:
            True if file search should be used, False for fallback

        """
        return self.state in [KillSwitchState.ACTIVE, KillSwitchState.DEGRADED]

    def force_disable(self) -> None:
        """Manually force disable file search"""
        logger.warning("kill_switch_force_disabled", reason="Manual override")
        self._disable()

    def force_enable(self) -> None:
        """Manually force enable file search"""
        logger.info("kill_switch_force_enabled", reason="Manual override")
        self.violation_count = 0
        self._activate()

    def get_state(self) -> str:
        """Get current kill switch state"""
        return self.state.value
