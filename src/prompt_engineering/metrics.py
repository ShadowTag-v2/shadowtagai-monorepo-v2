# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Prompt Metrics Tracking.

Track and analyze prompt performance metrics over time.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PromptExecution:
  """Single prompt execution record."""

  prompt_id: str
  prompt_text: str
  timestamp: datetime
  model: str
  success: bool
  first_try_success: bool
  revisions_needed: int
  tokens_used: int
  cost_usd: float
  response_time_sec: float
  user_satisfaction: int | None = None  # 1-5 scale
  notes: str | None = None


@dataclass
class PromptMetrics:
  """Aggregated metrics for prompt performance."""

  total_executions: int = 0
  successful_executions: int = 0
  first_try_success_count: int = 0
  total_revisions: int = 0
  total_tokens: int = 0
  total_cost_usd: float = 0.0
  total_time_sec: float = 0.0
  executions: list[PromptExecution] = field(default_factory=list)

  @property
  def success_rate(self) -> float:
    """Overall success rate."""
    if self.total_executions == 0:
      return 0.0
    return self.successful_executions / self.total_executions

  @property
  def first_try_success_rate(self) -> float:
    """First-try success rate."""
    if self.total_executions == 0:
      return 0.0
    return self.first_try_success_count / self.total_executions

  @property
  def avg_revisions(self) -> float:
    """Average revisions needed."""
    if self.total_executions == 0:
      return 0.0
    return self.total_revisions / self.total_executions

  @property
  def avg_tokens(self) -> float:
    """Average tokens per execution."""
    if self.total_executions == 0:
      return 0.0
    return self.total_tokens / self.total_executions

  @property
  def avg_cost_usd(self) -> float:
    """Average cost per execution."""
    if self.total_executions == 0:
      return 0.0
    return self.total_cost_usd / self.total_executions

  @property
  def avg_time_sec(self) -> float:
    """Average response time."""
    if self.total_executions == 0:
      return 0.0
    return self.total_time_sec / self.total_executions

  def add_execution(self, execution: PromptExecution):
    """Add a new execution record."""
    self.executions.append(execution)
    self.total_executions += 1

    if execution.success:
      self.successful_executions += 1

    if execution.first_try_success:
      self.first_try_success_count += 1

    self.total_revisions += execution.revisions_needed
    self.total_tokens += execution.tokens_used
    self.total_cost_usd += execution.cost_usd
    self.total_time_sec += execution.response_time_sec

  def compare_to_baseline(self, baseline: "PromptMetrics") -> dict:
    """
    Compare current metrics to baseline (e.g., before KERNEL vs after).

    Args:
        baseline: Baseline metrics to compare against

    Returns:
        Dictionary with improvement metrics
    """
    return {
      "first_try_success_improvement": (
        self.first_try_success_rate - baseline.first_try_success_rate
      ),
      "revision_reduction": baseline.avg_revisions - self.avg_revisions,
      "token_reduction_pct": (
        (baseline.avg_tokens - self.avg_tokens) / baseline.avg_tokens * 100
        if baseline.avg_tokens > 0
        else 0
      ),
      "cost_reduction_pct": (
        (baseline.avg_cost_usd - self.avg_cost_usd) / baseline.avg_cost_usd * 100
        if baseline.avg_cost_usd > 0
        else 0
      ),
      "time_reduction_pct": (
        (baseline.avg_time_sec - self.avg_time_sec) / baseline.avg_time_sec * 100
        if baseline.avg_time_sec > 0
        else 0
      ),
    }

  def generate_report(self) -> str:
    """Generate human-readable metrics report."""
    report = "=== Prompt Performance Metrics ===\n\n"
    report += f"Total Executions: {self.total_executions}\n"
    report += f"Success Rate: {self.success_rate:.1%}\n"
    report += f"First-Try Success Rate: {self.first_try_success_rate:.1%}\n"
    report += f"Avg Revisions Needed: {self.avg_revisions:.1f}\n"
    report += f"Avg Tokens: {self.avg_tokens:.0f}\n"
    report += f"Avg Cost: ${self.avg_cost_usd:.4f}\n"
    report += f"Avg Response Time: {self.avg_time_sec:.1f}s\n"
    return report

  def to_dict(self) -> dict:
    """Convert to dictionary for serialization."""
    return {
      "total_executions": self.total_executions,
      "successful_executions": self.successful_executions,
      "first_try_success_count": self.first_try_success_count,
      "total_revisions": self.total_revisions,
      "total_tokens": self.total_tokens,
      "total_cost_usd": self.total_cost_usd,
      "total_time_sec": self.total_time_sec,
      "success_rate": self.success_rate,
      "first_try_success_rate": self.first_try_success_rate,
      "avg_revisions": self.avg_revisions,
      "avg_tokens": self.avg_tokens,
      "avg_cost_usd": self.avg_cost_usd,
      "avg_time_sec": self.avg_time_sec,
    }

  def save_to_file(self, filepath: str):
    """Save metrics to JSON file."""
    with open(filepath, "w") as f:
      json.dump(self.to_dict(), f, indent=2)

  @classmethod
  def load_from_file(cls, filepath: str) -> "PromptMetrics":
    """Load metrics from JSON file."""
    with open(filepath) as f:
      data = json.load(f)

    metrics = cls()
    metrics.total_executions = data["total_executions"]
    metrics.successful_executions = data["successful_executions"]
    metrics.first_try_success_count = data["first_try_success_count"]
    metrics.total_revisions = data["total_revisions"]
    metrics.total_tokens = data["total_tokens"]
    metrics.total_cost_usd = data["total_cost_usd"]
    metrics.total_time_sec = data["total_time_sec"]
    return metrics


class MetricsTracker:
  """Track metrics for multiple prompts over time."""

  def __init__(self):
    self.prompts: dict[str, PromptMetrics] = {}

  def track_execution(self, execution: PromptExecution):
    """Track a single prompt execution."""
    if execution.prompt_id not in self.prompts:
      self.prompts[execution.prompt_id] = PromptMetrics()

    self.prompts[execution.prompt_id].add_execution(execution)

  def get_metrics(self, prompt_id: str) -> PromptMetrics | None:
    """Get metrics for a specific prompt."""
    return self.prompts.get(prompt_id)

  def get_all_metrics(self) -> dict[str, PromptMetrics]:
    """Get all tracked metrics."""
    return self.prompts

  def generate_comparison_report(
    self, before_ids: list[str], after_ids: list[str]
  ) -> str:
    """
    Generate comparison report (e.g., before KERNEL vs after KERNEL).

    Args:
        before_ids: List of prompt IDs from before period
        after_ids: List of prompt IDs from after period

    Returns:
        Formatted comparison report
    """
    # Aggregate before metrics
    before = PromptMetrics()
    for prompt_id in before_ids:
      if prompt_id in self.prompts:
        for exec in self.prompts[prompt_id].executions:
          before.add_execution(exec)

    # Aggregate after metrics
    after = PromptMetrics()
    for prompt_id in after_ids:
      if prompt_id in self.prompts:
        for exec in self.prompts[prompt_id].executions:
          after.add_execution(exec)

    # Generate comparison
    comparison = after.compare_to_baseline(before)

    report = "=== KERNEL Framework Impact Report ===\n\n"
    report += "BEFORE:\n"
    report += f"  First-Try Success: {before.first_try_success_rate:.1%}\n"
    report += f"  Avg Revisions: {before.avg_revisions:.1f}\n"
    report += f"  Avg Tokens: {before.avg_tokens:.0f}\n"
    report += f"  Avg Cost: ${before.avg_cost_usd:.4f}\n"
    report += f"  Avg Time: {before.avg_time_sec:.1f}s\n\n"

    report += "AFTER:\n"
    report += f"  First-Try Success: {after.first_try_success_rate:.1%}\n"
    report += f"  Avg Revisions: {after.avg_revisions:.1f}\n"
    report += f"  Avg Tokens: {after.avg_tokens:.0f}\n"
    report += f"  Avg Cost: ${after.avg_cost_usd:.4f}\n"
    report += f"  Avg Time: {after.avg_time_sec:.1f}s\n\n"

    report += "IMPROVEMENTS:\n"
    report += (
      f"  First-Try Success: {comparison['first_try_success_improvement']:+.1%}\n"
    )
    report += f"  Revision Reduction: {comparison['revision_reduction']:+.1f}\n"
    report += f"  Token Reduction: {comparison['token_reduction_pct']:+.1f}%\n"
    report += f"  Cost Reduction: {comparison['cost_reduction_pct']:+.1f}%\n"
    report += f"  Time Reduction: {comparison['time_reduction_pct']:+.1f}%\n"

    return report
