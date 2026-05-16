# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Base agent framework for Pinkln multi-agent system.

Agents are evolved versions of kernels with:
- Glicko-2 ratings for performance tracking
- Cheat sheet enhanced prompts
- DTE self-evolution capability
"""

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.ratings import Glicko2Player
from app.models.kernel import KernelOutput


class AgentConfig(BaseModel):
  """Configuration for an agent."""

  name: str
  description: str
  model: str = "gemini-2.0-flash-exp"
  temperature: float = 0.7
  max_tokens: int = 2048
  cheat_sheet_enabled: bool = True
  dte_enabled: bool = True


class AgentPerformance(BaseModel):
  """Performance tracking for an agent."""

  agent_name: str
  rating: Glicko2Player = Field(default_factory=Glicko2Player)
  total_executions: int = 0
  successful_executions: int = 0
  failed_executions: int = 0
  average_latency_ms: float = 0.0
  average_cost_usd: float = 0.0
  last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

  @property
  def success_rate(self) -> float:
    """Calculate success rate."""
    if self.total_executions == 0:
      return 0.0
    return self.successful_executions / self.total_executions

  def update_metrics(self, success: bool, latency_ms: float, cost_usd: float):
    """Update performance metrics."""
    self.total_executions += 1
    if success:
      self.successful_executions += 1
    else:
      self.failed_executions += 1

    # Rolling average
    n = self.total_executions
    self.average_latency_ms = (self.average_latency_ms * (n - 1) + latency_ms) / n
    self.average_cost_usd = (self.average_cost_usd * (n - 1) + cost_usd) / n
    self.last_updated = datetime.now(timezone.utc)


class Agent(ABC):
  """
  Base agent for Pinkln multi-agent system.

  Agents extend kernels with:
  - Performance ratings (Glicko-2)
  - Evolved prompts (cheat sheet fusion)
  - Self-evolution (DTE)
  """

  def __init__(self, config: AgentConfig):
    self.config = config
    self.performance = AgentPerformance(agent_name=config.name)

  @abstractmethod
  async def execute(self, input_data: Any) -> Any:
    """
    Execute agent task.

    Args:
        input_data: Input for agent

    Returns:
        Agent output
    """
    pass

  async def __call__(self, input_data: Any) -> KernelOutput:
    """Execute with performance tracking."""
    import time

    start_time = time.perf_counter()

    try:
      result = await self.execute(input_data)
      latency_ms = (time.perf_counter() - start_time) * 1000

      # Update performance metrics
      self.performance.update_metrics(
        success=True,
        latency_ms=latency_ms,
        cost_usd=0.0,  # Will be updated by specific agents
      )

      return KernelOutput(
        data=result,
        kernel_name=self.config.name,
        success=True,
        metadata={
          "agent_rating": self.performance.rating.get_rating(),
          "agent_success_rate": self.performance.success_rate,
        },
      )

    except Exception as e:
      latency_ms = (time.perf_counter() - start_time) * 1000
      self.performance.update_metrics(
        success=False,
        latency_ms=latency_ms,
        cost_usd=0.0,
      )

      return KernelOutput(
        data=None,
        kernel_name=self.config.name,
        success=False,
        error=str(e),
      )

  def get_stats(self) -> dict[str, Any]:
    """Get agent performance statistics."""
    return {
      "name": self.config.name,
      "rating": self.performance.rating.get_rating(),
      "rating_deviation": self.performance.rating.get_rd(),
      "volatility": self.performance.rating.get_vol(),
      "total_executions": self.performance.total_executions,
      "success_rate": self.performance.success_rate,
      "average_latency_ms": self.performance.average_latency_ms,
      "average_cost_usd": self.performance.average_cost_usd,
    }
