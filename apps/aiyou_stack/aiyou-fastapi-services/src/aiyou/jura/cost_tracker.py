"""JuraCostTracker: Cost accounting and revenue attribution for requests.

Tracks:
- Per-request costs
- Per-agent attribution
- Tier utilization metrics
- Historical cost data
"""

import json
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .classifier import CostTier

logger = logging.getLogger(__name__)


@dataclass
class JuraCostRecord:
    """Record of a single request's cost."""

    request_id: str
    timestamp: datetime
    tier: CostTier
    agent_ids: list[str]
    model_used: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    success: bool
    task_type: str = "execution"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            "tier": self.tier.value,
            "agent_ids": self.agent_ids,
            "model_used": self.model_used,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "task_type": self.task_type,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JuraCostRecord":
        """Create from dictionary."""
        return cls(
            request_id=data["request_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            tier=CostTier(data["tier"]),
            agent_ids=data["agent_ids"],
            model_used=data["model_used"],
            input_tokens=data["input_tokens"],
            output_tokens=data["output_tokens"],
            cost_usd=data["cost_usd"],
            latency_ms=data["latency_ms"],
            success=data["success"],
            task_type=data.get("task_type", "execution"),
            metadata=data.get("metadata", {}),
        )


class JuraCostTracker:
    """Tracks costs and generates metrics for JURA protocol.

    Features:
    - In-memory cost tracking (last 1000 requests)
    - Per-tier aggregation
    - Per-agent attribution
    - Export to JSON for persistence
    """

    MAX_HISTORY = 1000  # Keep last 1000 requests in memory

    def __init__(self):
        self._records: list[JuraCostRecord] = []
        self._tier_totals: dict[CostTier, float] = defaultdict(float)
        self._tier_counts: dict[CostTier, int] = defaultdict(int)
        self._agent_costs: dict[str, float] = defaultdict(float)
        self._agent_counts: dict[str, int] = defaultdict(int)
        self._total_cost: float = 0.0
        self._total_requests: int = 0

    def record(
        self,
        tier: CostTier,
        agent_ids: list[str],
        model_used: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: int,
        success: bool,
        task_type: str = "execution",
        metadata: dict[str, Any] | None = None,
    ) -> JuraCostRecord:
        """Record a completed request.

        Args:
            tier: Cost tier used
            agent_ids: List of agent IDs that participated
            model_used: LLM model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost_usd: Total cost in USD
            latency_ms: Response latency in milliseconds
            success: Whether request succeeded
            task_type: Type of task (execution/governance)
            metadata: Additional metadata

        Returns:
            The created JuraCostRecord

        """
        record = JuraCostRecord(
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC),
            tier=tier,
            agent_ids=agent_ids,
            model_used=model_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            success=success,
            task_type=task_type,
            metadata=metadata or {},
        )

        # Add to history (with size limit)
        self._records.append(record)
        if len(self._records) > self.MAX_HISTORY:
            self._records.pop(0)

        # Update aggregates
        self._tier_totals[tier] += cost_usd
        self._tier_counts[tier] += 1
        self._total_cost += cost_usd
        self._total_requests += 1

        # Per-agent attribution (split cost evenly among agents)
        if agent_ids:
            cost_per_agent = cost_usd / len(agent_ids)
            for agent_id in agent_ids:
                self._agent_costs[agent_id] += cost_per_agent
                self._agent_counts[agent_id] += 1

        logger.debug(
            f"Recorded cost: tier={tier.value}, cost=${cost_usd:.4f}, "
            f"agents={len(agent_ids)}, latency={latency_ms}ms",
        )

        return record

    def get_metrics(self) -> dict[str, Any]:
        """Get current cost metrics."""
        return {
            "total_cost_usd": self._total_cost,
            "total_requests": self._total_requests,
            "average_cost_usd": self._total_cost / max(1, self._total_requests),
            "tier_breakdown": {
                tier.value: {
                    "total_cost": self._tier_totals[tier],
                    "request_count": self._tier_counts[tier],
                    "average_cost": self._tier_totals[tier] / max(1, self._tier_counts[tier]),
                    "percentage": (self._tier_counts[tier] / max(1, self._total_requests)) * 100,
                }
                for tier in [CostTier.FREE, CostTier.FLASH, CostTier.PRO]
            },
            "recent_records": len(self._records),
        }

    def get_tier_metrics(self, tier: CostTier) -> dict[str, Any]:
        """Get metrics for a specific tier."""
        tier_records = [r for r in self._records if r.tier == tier]

        if not tier_records:
            return {
                "tier": tier.value,
                "total_cost": 0.0,
                "request_count": 0,
                "average_cost": 0.0,
                "average_latency_ms": 0,
                "success_rate": 0.0,
            }

        total_latency = sum(r.latency_ms for r in tier_records)
        success_count = sum(1 for r in tier_records if r.success)

        return {
            "tier": tier.value,
            "total_cost": self._tier_totals[tier],
            "request_count": self._tier_counts[tier],
            "average_cost": self._tier_totals[tier] / max(1, self._tier_counts[tier]),
            "average_latency_ms": total_latency / len(tier_records),
            "success_rate": success_count / len(tier_records),
        }

    def get_agent_metrics(self, agent_id: str) -> dict[str, Any]:
        """Get metrics for a specific agent."""
        return {
            "agent_id": agent_id,
            "total_cost": self._agent_costs.get(agent_id, 0.0),
            "request_count": self._agent_counts.get(agent_id, 0),
            "average_cost": (
                self._agent_costs.get(agent_id, 0.0) / max(1, self._agent_counts.get(agent_id, 0))
            ),
        }

    def get_top_agents(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get top agents by cost."""
        sorted_agents = sorted(self._agent_costs.items(), key=lambda x: x[1], reverse=True)[:limit]

        return [self.get_agent_metrics(agent_id) for agent_id, _ in sorted_agents]

    def get_recent_records(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent cost records."""
        return [r.to_dict() for r in self._records[-limit:]]

    def export_json(self) -> str:
        """Export all records to JSON."""
        return json.dumps(
            {
                "metrics": self.get_metrics(),
                "records": [r.to_dict() for r in self._records],
            },
            indent=2,
        )

    def reset(self) -> None:
        """Reset all tracking data."""
        self._records.clear()
        self._tier_totals.clear()
        self._tier_counts.clear()
        self._agent_costs.clear()
        self._agent_counts.clear()
        self._total_cost = 0.0
        self._total_requests = 0
        logger.info("Cost tracker reset")

    def get_cost_projection(self, daily_requests: int = 1000) -> dict[str, Any]:
        """Project monthly costs based on current tier distribution.

        Args:
            daily_requests: Expected daily request count

        Returns:
            Projected costs by tier and total

        """
        if self._total_requests == 0:
            return {"error": "No data for projection"}

        # Calculate tier distribution
        distribution = {
            tier: self._tier_counts[tier] / self._total_requests
            for tier in [CostTier.FREE, CostTier.FLASH, CostTier.PRO]
        }

        # Average cost per tier
        avg_costs = {
            tier: self._tier_totals[tier] / max(1, self._tier_counts[tier])
            for tier in [CostTier.FREE, CostTier.FLASH, CostTier.PRO]
        }

        # Project monthly (30 days)
        monthly_requests = daily_requests * 30
        projections = {}
        total_projected = 0.0

        for tier in [CostTier.FREE, CostTier.FLASH, CostTier.PRO]:
            tier_requests = monthly_requests * distribution[tier]
            tier_cost = tier_requests * avg_costs[tier]
            projections[tier.value] = {
                "percentage": distribution[tier] * 100,
                "requests": int(tier_requests),
                "cost_usd": tier_cost,
            }
            total_projected += tier_cost

        return {
            "daily_requests": daily_requests,
            "monthly_requests": monthly_requests,
            "tier_projections": projections,
            "total_monthly_cost_usd": total_projected,
        }
