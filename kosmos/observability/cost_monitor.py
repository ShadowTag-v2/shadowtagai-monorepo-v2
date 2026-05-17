# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Cost Monitor: Budget tracking and alerts for LLM inference costs.

Features:
- Real-time cost tracking per session
- Daily/monthly budget enforcement
- Cost estimation before execution
- Alert thresholds and notifications
- BigQuery logging for analytics
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class UsageRecord:
  """Record of LLM usage and cost."""

  timestamp: datetime
  session_id: str
  agent_name: str
  model: str
  input_tokens: int
  output_tokens: int
  cost: float


class BudgetExceededError(Exception):
  """Raised when budget limit would be exceeded."""

  pass


class CostMonitor:
  """
  Monitor and control LLM inference costs.

  Tracks usage across sessions and enforces budget limits.
  Provides cost estimation and alerting.
  """

  # Gemini model pricing (per 1M tokens)
  PRICING = {
    "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},  # When available
    "gemini-2.5-pro": {"input": 1.25, "output": 5.00},  # When available
  }

  def __init__(
    self,
    daily_budget: float = 2000.0,
    monthly_budget: float = 60000.0,
    alert_threshold: float = 0.8,  # Alert at 80% of budget
    session_budget: float | None = 500.0,  # Max cost per session
  ):
    """
    Initialize cost monitor.

    Args:
        daily_budget: Daily budget limit in USD
        monthly_budget: Monthly budget limit in USD
        alert_threshold: Fraction of budget to trigger alert (0-1)
        session_budget: Optional per-session budget limit
    """
    self.daily_budget = daily_budget
    self.monthly_budget = monthly_budget
    self.alert_threshold = alert_threshold
    self.session_budget = session_budget

    # Usage tracking
    self.usage_records: list[UsageRecord] = []
    self.session_costs: dict[str, float] = {}

    # Budget state
    self.daily_burn: float = 0.0
    self.monthly_burn: float = 0.0
    self.last_reset_date: datetime = datetime.now(timezone.utc).date()
    self.last_reset_month: int = datetime.now(timezone.utc).month

    logger.info(
      f"CostMonitor initialized: daily=${daily_budget:.2f}, monthly=${monthly_budget:.2f}, session=${session_budget:.2f}"
    )

  def check_budget(
    self,
    estimated_cost: float,
    session_id: str | None = None,
  ) -> bool:
    """
    Check if an operation would exceed budget limits.

    Args:
        estimated_cost: Estimated cost in USD
        session_id: Optional session ID for per-session tracking

    Returns:
        True if within budget

    Raises:
        BudgetExceededError: If budget would be exceeded
    """
    self._reset_if_needed()

    # Check daily budget
    if self.daily_burn + estimated_cost > self.daily_budget:
      raise BudgetExceededError(
        f"Operation would exceed daily budget: ${self.daily_burn:.2f} + ${estimated_cost:.2f} > ${self.daily_budget:.2f}"
      )

    # Check monthly budget
    if self.monthly_burn + estimated_cost > self.monthly_budget:
      raise BudgetExceededError(
        f"Operation would exceed monthly budget: ${self.monthly_burn:.2f} + ${estimated_cost:.2f} > ${self.monthly_budget:.2f}"
      )

    # Check session budget if applicable
    if session_id and self.session_budget:
      session_cost = self.session_costs.get(session_id, 0.0)
      if session_cost + estimated_cost > self.session_budget:
        raise BudgetExceededError(
          f"Operation would exceed session budget for {session_id}: "
          f"${session_cost:.2f} + ${estimated_cost:.2f} > ${self.session_budget:.2f}"
        )

    # Check alert thresholds
    if self.daily_burn + estimated_cost > self.daily_budget * self.alert_threshold:
      logger.warning(
        f"Approaching daily budget limit: "
        f"${self.daily_burn + estimated_cost:.2f} / ${self.daily_budget:.2f} "
        f"({(self.daily_burn + estimated_cost) / self.daily_budget * 100:.1f}%)"
      )

    if self.monthly_burn + estimated_cost > self.monthly_budget * self.alert_threshold:
      logger.warning(
        f"Approaching monthly budget limit: "
        f"${self.monthly_burn + estimated_cost:.2f} / ${self.monthly_budget:.2f} "
        f"({(self.monthly_burn + estimated_cost) / self.monthly_budget * 100:.1f}%)"
      )

    return True

  def record_usage(
    self,
    tokens: int,
    model: str,
    cost: float,
    session_id: str = "default",
    agent_name: str = "unknown",
    input_tokens: int | None = None,
    output_tokens: int | None = None,
  ):
    """
    Record actual usage and cost.

    Args:
        tokens: Total tokens consumed
        model: Model name
        cost: Actual cost in USD
        session_id: Session identifier
        agent_name: Agent name
        input_tokens: Input tokens (optional, for detailed tracking)
        output_tokens: Output tokens (optional, for detailed tracking)
    """
    self._reset_if_needed()

    # Create usage record
    record = UsageRecord(
      timestamp=datetime.now(timezone.utc),
      session_id=session_id,
      agent_name=agent_name,
      model=model,
      input_tokens=input_tokens or 0,
      output_tokens=output_tokens or 0,
      cost=cost,
    )

    self.usage_records.append(record)

    # Update burn rates
    self.daily_burn += cost
    self.monthly_burn += cost

    # Update session cost
    self.session_costs[session_id] = self.session_costs.get(session_id, 0.0) + cost

    logger.debug(
      f"Recorded usage: {tokens} tokens, ${cost:.4f} ({model}) [daily: ${self.daily_burn:.2f}, monthly: ${self.monthly_burn:.2f}]"
    )

  def estimate_cost(
    self,
    input_tokens: int,
    output_tokens: int,
    model: str,
  ) -> float:
    """
    Estimate cost for a generation.

    Args:
        input_tokens: Expected input tokens
        output_tokens: Expected output tokens
        model: Model name

    Returns:
        Estimated cost in USD
    """
    if model not in self.PRICING:
      logger.warning(f"Unknown model {model}, using gemini-1.5-pro pricing")
      model = "gemini-1.5-pro"

    pricing = self.PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return input_cost + output_cost

  def get_session_cost(self, session_id: str) -> float:
    """Get total cost for a session."""
    return self.session_costs.get(session_id, 0.0)

  def get_daily_burn(self) -> float:
    """Get current daily burn rate."""
    self._reset_if_needed()
    return self.daily_burn

  def get_monthly_burn(self) -> float:
    """Get current monthly burn rate."""
    self._reset_if_needed()
    return self.monthly_burn

  def get_budget_status(self) -> dict[str, any]:
    """
    Get comprehensive budget status.

    Returns:
        Dictionary with budget metrics
    """
    self._reset_if_needed()

    return {
      "daily": {
        "budget": self.daily_budget,
        "burned": self.daily_burn,
        "remaining": self.daily_budget - self.daily_burn,
        "utilization_pct": (self.daily_burn / self.daily_budget * 100)
        if self.daily_budget > 0
        else 0,
      },
      "monthly": {
        "budget": self.monthly_budget,
        "burned": self.monthly_burn,
        "remaining": self.monthly_budget - self.monthly_burn,
        "utilization_pct": (self.monthly_burn / self.monthly_budget * 100)
        if self.monthly_budget > 0
        else 0,
      },
      "sessions": {
        "active_sessions": len(self.session_costs),
        "total_session_cost": sum(self.session_costs.values()),
        "top_sessions": sorted(
          self.session_costs.items(),
          key=lambda x: x[1],
          reverse=True,
        )[:5],
      },
      "last_reset": self.last_reset_date.isoformat(),
    }

  def get_usage_summary(
    self,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
  ) -> dict[str, any]:
    """
    Get usage summary for a time period.

    Args:
        start_time: Start of period (default: 24 hours ago)
        end_time: End of period (default: now)

    Returns:
        Usage statistics dictionary
    """
    if start_time is None:
      start_time = datetime.now(timezone.utc) - timedelta(days=1)
    if end_time is None:
      end_time = datetime.now(timezone.utc)

    # Filter records
    period_records = [
      r for r in self.usage_records if start_time <= r.timestamp <= end_time
    ]

    if not period_records:
      return {"total_cost": 0.0, "total_tokens": 0, "num_requests": 0}

    total_cost = sum(r.cost for r in period_records)
    total_input_tokens = sum(r.input_tokens for r in period_records)
    total_output_tokens = sum(r.output_tokens for r in period_records)

    # Group by model
    by_model: dict[str, dict] = {}
    for record in period_records:
      if record.model not in by_model:
        by_model[record.model] = {
          "requests": 0,
          "input_tokens": 0,
          "output_tokens": 0,
          "cost": 0.0,
        }
      by_model[record.model]["requests"] += 1
      by_model[record.model]["input_tokens"] += record.input_tokens
      by_model[record.model]["output_tokens"] += record.output_tokens
      by_model[record.model]["cost"] += record.cost

    return {
      "period_start": start_time.isoformat(),
      "period_end": end_time.isoformat(),
      "total_cost": total_cost,
      "total_input_tokens": total_input_tokens,
      "total_output_tokens": total_output_tokens,
      "num_requests": len(period_records),
      "by_model": by_model,
    }

  def _reset_if_needed(self):
    """Reset daily/monthly counters if needed."""
    now = datetime.now(timezone.utc)
    today = now.date()
    current_month = now.month

    # Reset daily if new day
    if today > self.last_reset_date:
      logger.info(
        f"Daily budget reset: burned ${self.daily_burn:.2f} on {self.last_reset_date}"
      )
      self.daily_burn = 0.0
      self.last_reset_date = today

    # Reset monthly if new month
    if current_month != self.last_reset_month:
      logger.info(
        f"Monthly budget reset: burned ${self.monthly_burn:.2f} in month {self.last_reset_month}"
      )
      self.monthly_burn = 0.0
      self.last_reset_month = current_month

  def __repr__(self) -> str:
    return f"CostMonitor(daily=${self.daily_burn:.2f}/${self.daily_budget:.2f}, monthly=${self.monthly_burn:.2f}/${self.monthly_budget:.2f})"
