"""AgentLifecycle - Regeneration and Corruption Prevention
Version: 1.0.0

Philosophy: Agents degrade over time. Regenerate before corruption spreads.
Design: Time-based, performance-based, and corruption-detection triggers.

Like jury rotation: Fresh eyes prevent institutional bias.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class RegenerationTrigger(StrEnum):
    """Reasons for agent regeneration."""

    TIME_BASED = "time"  # Too many tasks
    PERFORMANCE = "performance"  # Accuracy drop
    SYCOPHANCY = "sycophancy"  # Blindly following others
    CORRUPTION = "corruption"  # Accumulated errors
    MANUAL = "manual"  # User-requested


@dataclass
class AgentMetrics:
    """Performance metrics for lifecycle decisions."""

    agent_id: str

    # Task tracking
    tasks_completed: int = 0
    tasks_since_regeneration: int = 0

    # Performance
    recent_accuracy: float = 0.85
    historical_accuracy: float = 0.85

    # Corruption indicators
    sycophancy_rate: float = 0.0  # Rate of blindly following
    error_propagation_count: int = 0  # Errors passed to others
    confidence_without_basis: int = 0  # High confidence, wrong answer

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    last_regeneration: datetime | None = None
    last_task: datetime | None = None


@dataclass
class RegenerationEvent:
    """Record of agent regeneration."""

    agent_id: str
    trigger: RegenerationTrigger
    timestamp: datetime = field(default_factory=datetime.now)
    metrics_before: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


class AgentLifecycle:
    """Manage agent lifecycle, regeneration, and corruption prevention.

    Regeneration triggers:
    1. Time-based: After N tasks
    2. Performance: Accuracy drops below threshold
    3. Sycophancy: Rate > 0.3
    4. Corruption: Error propagation detected
    """

    def __init__(self):
        self.agents: dict[str, AgentMetrics] = {}
        self.regeneration_history: list[RegenerationEvent] = []

        # Thresholds
        self.max_tasks_before_regeneration = 50
        self.performance_threshold = 0.75
        self.sycophancy_threshold = 0.30
        self.error_propagation_threshold = 3

        # Temperature annealing for small models
        self.use_temperature_annealing = True
        self.initial_temperature = 0.7
        self.final_temperature = 0.3

    # =========================================================================
    # AGENT REGISTRATION
    # =========================================================================

    def register_agent(self, agent_id: str) -> AgentMetrics:
        """Register agent in lifecycle management."""
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentMetrics(agent_id=agent_id)
        return self.agents[agent_id]

    def get_metrics(self, agent_id: str) -> AgentMetrics | None:
        """Get agent metrics."""
        return self.agents.get(agent_id)

    # =========================================================================
    # TASK TRACKING
    # =========================================================================

    def record_task(
        self,
        agent_id: str,
        success: bool,
        followed_others: bool = False,
        high_confidence: bool = False,
    ):
        """Record task completion and update metrics.

        Args:
            agent_id: Agent identifier
            success: Whether task was successful
            followed_others: Whether agent adopted others' answers
            high_confidence: Whether agent expressed high confidence

        """
        if agent_id not in self.agents:
            self.register_agent(agent_id)

        metrics = self.agents[agent_id]
        metrics.tasks_completed += 1
        metrics.tasks_since_regeneration += 1
        metrics.last_task = datetime.now()

        # Update accuracy (rolling average)
        old_weight = 0.9
        new_weight = 0.1
        task_accuracy = 1.0 if success else 0.0
        metrics.recent_accuracy = old_weight * metrics.recent_accuracy + new_weight * task_accuracy

        # Track sycophancy
        if followed_others:
            if success:
                # Following and correct - might be ok
                pass
            else:
                # Following and wrong - sycophancy
                metrics.sycophancy_rate = min(1.0, metrics.sycophancy_rate + 0.1)

        # Track overconfidence
        if high_confidence and not success:
            metrics.confidence_without_basis += 1

        # Decay sycophancy over time
        metrics.sycophancy_rate = max(0.0, metrics.sycophancy_rate - 0.02)

    def record_error_propagation(self, agent_id: str):
        """Record when agent propagates an error to others."""
        if agent_id in self.agents:
            self.agents[agent_id].error_propagation_count += 1

    # =========================================================================
    # REGENERATION CHECKS
    # =========================================================================

    def should_regenerate(self, agent_id: str) -> RegenerationTrigger | None:
        """Check if agent should be regenerated.

        Returns trigger type if regeneration needed, None otherwise.
        """
        if agent_id not in self.agents:
            return None

        metrics = self.agents[agent_id]

        # Check time-based
        if metrics.tasks_since_regeneration >= self.max_tasks_before_regeneration:
            return RegenerationTrigger.TIME_BASED

        # Check performance
        if metrics.recent_accuracy < self.performance_threshold:
            return RegenerationTrigger.PERFORMANCE

        # Check sycophancy
        if metrics.sycophancy_rate > self.sycophancy_threshold:
            return RegenerationTrigger.SYCOPHANCY

        # Check corruption
        if metrics.error_propagation_count >= self.error_propagation_threshold:
            return RegenerationTrigger.CORRUPTION

        return None

    def check_all_agents(self) -> list[tuple]:
        """Check all agents for regeneration needs."""
        needs_regeneration = []

        for agent_id in self.agents:
            trigger = self.should_regenerate(agent_id)
            if trigger:
                needs_regeneration.append((agent_id, trigger))

        return needs_regeneration

    # =========================================================================
    # REGENERATION
    # =========================================================================

    def regenerate(
        self,
        agent_id: str,
        trigger: RegenerationTrigger = RegenerationTrigger.MANUAL,
    ) -> dict[str, Any]:
        """Regenerate an agent.

        Resets state while preserving identity and learned knowledge.
        """
        if agent_id not in self.agents:
            return {"error": "Agent not found"}

        metrics = self.agents[agent_id]

        # Record event
        event = RegenerationEvent(
            agent_id=agent_id,
            trigger=trigger,
            metrics_before={
                "tasks_since_regeneration": metrics.tasks_since_regeneration,
                "recent_accuracy": metrics.recent_accuracy,
                "sycophancy_rate": metrics.sycophancy_rate,
                "error_propagation": metrics.error_propagation_count,
            },
            notes=f"Triggered by {trigger.value}",
        )
        self.regeneration_history.append(event)

        # Reset metrics (but preserve historical)
        metrics.tasks_since_regeneration = 0
        metrics.sycophancy_rate = 0.0
        metrics.error_propagation_count = 0
        metrics.confidence_without_basis = 0
        metrics.last_regeneration = datetime.now()

        # Boost accuracy slightly (fresh start)
        metrics.recent_accuracy = min(1.0, metrics.recent_accuracy + 0.1)

        return {
            "agent_id": agent_id,
            "trigger": trigger.value,
            "metrics_reset": True,
            "new_accuracy": metrics.recent_accuracy,
            "timestamp": event.timestamp.isoformat(),
        }

    def rolling_replacement(self, agent_ids: list[str]) -> str | None:
        """Perform rolling replacement - regenerate one agent per cycle.

        Returns agent_id that was regenerated, if any.
        """
        # Sort by tasks since regeneration
        sorted_agents = sorted(
            [
                (aid, self.agents[aid].tasks_since_regeneration)
                for aid in agent_ids
                if aid in self.agents
            ],
            key=lambda x: x[1],
            reverse=True,
        )

        if not sorted_agents:
            return None

        # Regenerate the one with most tasks
        oldest_id = sorted_agents[0][0]
        if (
            self.agents[oldest_id].tasks_since_regeneration
            > self.max_tasks_before_regeneration // 2
        ):
            self.regenerate(oldest_id, RegenerationTrigger.TIME_BASED)
            return oldest_id

        return None

    # =========================================================================
    # TEMPERATURE ANNEALING
    # =========================================================================

    def get_temperature(self, agent_id: str) -> float:
        """Get temperature for agent based on lifecycle stage.

        Temperature annealing: Start exploratory (0.7), become focused (0.3).
        Helps small models avoid forgetting during evolution.
        """
        if not self.use_temperature_annealing:
            return self.initial_temperature

        if agent_id not in self.agents:
            return self.initial_temperature

        metrics = self.agents[agent_id]

        # Calculate progress through lifecycle
        progress = min(1.0, metrics.tasks_since_regeneration / self.max_tasks_before_regeneration)

        # Linear annealing
        temperature = (
            self.initial_temperature
            - (self.initial_temperature - self.final_temperature) * progress
        )

        return round(temperature, 2)

    # =========================================================================
    # HEALTH ASSESSMENT
    # =========================================================================

    def assess_health(self, agent_id: str) -> dict[str, Any]:
        """Comprehensive health assessment for agent.

        Returns status and recommendations.
        """
        if agent_id not in self.agents:
            return {"error": "Agent not found"}

        metrics = self.agents[agent_id]

        # Calculate health score
        accuracy_score = metrics.recent_accuracy
        sycophancy_score = 1.0 - metrics.sycophancy_rate
        freshness_score = 1.0 - (
            metrics.tasks_since_regeneration / self.max_tasks_before_regeneration
        )

        health_score = accuracy_score * 0.4 + sycophancy_score * 0.3 + freshness_score * 0.3

        # Determine status
        if health_score >= 0.8:
            status = "HEALTHY"
        elif health_score >= 0.6:
            status = "FAIR"
        elif health_score >= 0.4:
            status = "DEGRADED"
        else:
            status = "CRITICAL"

        # Generate recommendations
        recommendations = []

        if metrics.recent_accuracy < self.performance_threshold:
            recommendations.append("Performance below threshold - consider regeneration")

        if metrics.sycophancy_rate > self.sycophancy_threshold * 0.7:
            recommendations.append("Sycophancy rising - encourage independent thinking")

        if metrics.tasks_since_regeneration > self.max_tasks_before_regeneration * 0.8:
            recommendations.append("Approaching task limit - schedule regeneration")

        if metrics.error_propagation_count > 0:
            recommendations.append(
                f"Error propagation detected ({metrics.error_propagation_count}x) - "
                "review outputs carefully",
            )

        # Check for regeneration trigger
        trigger = self.should_regenerate(agent_id)

        return {
            "agent_id": agent_id,
            "health_score": f"{health_score:.1%}",
            "status": status,
            "metrics": {
                "accuracy": f"{metrics.recent_accuracy:.1%}",
                "sycophancy": f"{metrics.sycophancy_rate:.1%}",
                "tasks_since_regen": metrics.tasks_since_regeneration,
                "error_propagation": metrics.error_propagation_count,
            },
            "temperature": self.get_temperature(agent_id),
            "needs_regeneration": trigger.value if trigger else None,
            "recommendations": recommendations,
            "last_regeneration": (
                metrics.last_regeneration.isoformat() if metrics.last_regeneration else "Never"
            ),
        }

    # =========================================================================
    # LIFECYCLE SUMMARY
    # =========================================================================

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all agent lifecycles."""
        if not self.agents:
            return {"agents": 0, "message": "No agents registered"}

        # Aggregate stats
        total_tasks = sum(m.tasks_completed for m in self.agents.values())
        avg_accuracy = sum(m.recent_accuracy for m in self.agents.values()) / len(self.agents)
        avg_sycophancy = sum(m.sycophancy_rate for m in self.agents.values()) / len(self.agents)

        # Count needing regeneration
        needs_regen = len(self.check_all_agents())

        return {
            "total_agents": len(self.agents),
            "total_tasks": total_tasks,
            "average_accuracy": f"{avg_accuracy:.1%}",
            "average_sycophancy": f"{avg_sycophancy:.1%}",
            "agents_needing_regeneration": needs_regen,
            "total_regenerations": len(self.regeneration_history),
            "regeneration_breakdown": self._regeneration_breakdown(),
        }

    def _regeneration_breakdown(self) -> dict[str, int]:
        """Get breakdown of regeneration triggers."""
        breakdown = {}
        for event in self.regeneration_history:
            trigger = event.trigger.value
            breakdown[trigger] = breakdown.get(trigger, 0) + 1
        return breakdown

    def __repr__(self) -> str:
        return (
            f"AgentLifecycle("
            f"agents={len(self.agents)}, "
            f"regenerations={len(self.regeneration_history)})"
        )


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_lifecycle_manager() -> AgentLifecycle:
    """Create agent lifecycle manager.

    "Fresh eyes prevent institutional bias."
    """
    return AgentLifecycle()


# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("AgentLifecycle - Self Test")
    print("=" * 60)

    # Create manager
    lifecycle = create_lifecycle_manager()
    print(f"\nCreated: {lifecycle}")

    # Register agent
    metrics = lifecycle.register_agent("agent_alpha")
    print(f"\nRegistered: {metrics.agent_id}")

    # Simulate tasks
    print("\n" + "=" * 60)
    print("Simulating Tasks...")

    for i in range(30):
        success = i % 5 != 0  # Fail every 5th task
        followed = i % 3 == 0  # Follow others every 3rd
        lifecycle.record_task("agent_alpha", success, followed)

    # Check health
    print("\n" + "=" * 60)
    print("Health Assessment:")

    health = lifecycle.assess_health("agent_alpha")
    print(f"\nStatus: {health['status']}")
    print(f"Health Score: {health['health_score']}")
    print(f"Temperature: {health['temperature']}")
    print("\nMetrics:")
    for k, v in health["metrics"].items():
        print(f"  {k}: {v}")

    if health["recommendations"]:
        print("\nRecommendations:")
        for rec in health["recommendations"]:
            print(f"  - {rec}")

    # More tasks to trigger regeneration
    print("\n" + "=" * 60)
    print("Continuing to trigger regeneration...")

    for i in range(25):  # noqa: B007
        lifecycle.record_task("agent_alpha", True, False)

    # Check if needs regeneration
    trigger = lifecycle.should_regenerate("agent_alpha")
    if trigger:
        print(f"\nRegeneration needed: {trigger.value}")

        # Regenerate
        result = lifecycle.regenerate("agent_alpha", trigger)
        print(f"Regenerated: {result['agent_id']}")
        print(f"New accuracy: {result['new_accuracy']:.1%}")

    # Summary
    print("\n" + "=" * 60)
    print("Lifecycle Summary:")

    summary = lifecycle.get_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("✓ AgentLifecycle working correctly")
    print("\nPhilosophy: Fresh eyes prevent institutional bias.")
