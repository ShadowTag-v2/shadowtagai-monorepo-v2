"""
COR CONTEXT - Lightweight Execution Context
=============================================

Extracted from cor_orchestrator.py as part of the Rich Hickey refactor.

Replaces SK's KernelContext with a zero-overhead dataclass.
Latency: <1μs creation time.
Memory: ~500 bytes per context.

Author: Pnkln Architecture Team
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """
    Lightweight execution context for agent pipeline.

    SK Equivalent: KernelContext (but without DI overhead)
    Latency: <1μs creation time
    Memory: ~500 bytes per context
    """

    request_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    latency_budget_ms: float = 90.0  # p99 SLA target

    # Performance tracking
    stage_latencies: dict[str, float] = field(default_factory=dict)
    total_latency_ms: float = 0.0

    def set_variable(self, key: str, value: Any) -> None:
        """Store variable for downstream stages."""
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Retrieve variable from upstream stages."""
        return self.variables.get(key, default)

    def record_stage_latency(self, stage_name: str, latency_ms: float) -> None:
        """Track latency per pipeline stage."""
        self.stage_latencies[stage_name] = latency_ms
        self.total_latency_ms += latency_ms

        if self.total_latency_ms > self.latency_budget_ms:
            logger.warning(
                f"Context {self.request_id} exceeded latency budget: "
                f"{self.total_latency_ms:.2f}ms > {self.latency_budget_ms}ms"
            )

    def is_over_budget(self) -> bool:
        """Check if execution has exceeded latency SLA."""
        return self.total_latency_ms > self.latency_budget_ms
