#!/usr/bin/env python3
"""Running Estimate Manager for Flying n-autoresearch/Kosmos/BioAgents swarm.
Implements FM 6-0 Running Estimates for continuous swarm state tracking.
"""

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass
class AgentMetrics:
    """Per-agent metrics."""

    agent_id: int
    tier: str
    tasks_completed: int
    errors: int
    avg_latency_ms: float
    shift_start: str
    shift_end: str
    available: bool


@dataclass
class SquadMetrics:
    """Per-squad metrics."""

    squad_id: int
    specialty: str
    active_agents: int
    total_agents: int
    tasks_queued: int
    avg_latency_ms: float
    error_rate: float


@dataclass
class RunningEstimate:
    """FM 6-0 Running Estimate for Flying n-autoresearch/Kosmos/BioAgents swarm.

    Updated continuously to reflect current operational state.
    Used for decision support and kill-switch conditions.
    """

    # Timestamp
    timestamp: str

    # Agent availability
    agent_availability: int
    total_agents: int
    agents_on_shift: int
    agents_relieved: int

    # Tier saturation (0.0 to 1.0)
    tier_saturation: dict[str, float]

    # Performance metrics
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_rate: float
    throughput_rps: float

    # Task metrics
    tasks_queued: int
    tasks_in_progress: int
    tasks_completed: int
    tasks_failed: int

    # Squad metrics
    squads_active: int
    squad_utilization: dict[int, float]

    # Kill-switch conditions
    kill_conditions: dict[str, bool]

    # History (last N updates)
    history: list[dict] = field(default_factory=list)


class RunningEstimateManager:
    """Manager for FM 6-0 Running Estimates.

    Provides:
    - Real-time metrics collection
    - Decision support calculations
    - Kill-switch condition monitoring
    - Historical trend analysis
    """

    # Constants
    TOTAL_AGENTS = 600
    TOTAL_SQUADS = 24
    MAX_HISTORY = 100

    # Kill-switch thresholds
    KILL_P99_LATENCY_MS = 2000
    KILL_ERROR_RATE = 0.1
    KILL_QUEUE_DEPTH = 1000

    def __init__(self):
        self.estimate = self._init_estimate()
        self.agent_metrics: dict[int, AgentMetrics] = {}
        self.squad_metrics: dict[int, SquadMetrics] = {}

    def _init_estimate(self) -> RunningEstimate:
        """Initialize running estimate with defaults."""
        return RunningEstimate(
            timestamp=datetime.utcnow().isoformat(),
            agent_availability=self.TOTAL_AGENTS,
            total_agents=self.TOTAL_AGENTS,
            agents_on_shift=self.TOTAL_AGENTS,
            agents_relieved=0,
            tier_saturation={"FREE": 0.0, "FLASH": 0.0, "PRO": 0.0},
            p50_latency_ms=0.0,
            p95_latency_ms=0.0,
            p99_latency_ms=0.0,
            error_rate=0.0,
            throughput_rps=0.0,
            tasks_queued=0,
            tasks_in_progress=0,
            tasks_completed=0,
            tasks_failed=0,
            squads_active=0,
            squad_utilization=dict.fromkeys(range(self.TOTAL_SQUADS), 0.0),
            kill_conditions={
                "p99_exceeded": False,
                "error_rate_exceeded": False,
                "queue_overflow": False,
                "shift_violation": False,
            },
            history=[],
        )

    def update(
        self,
        latencies: list[float] = None,
        errors: int = 0,
        tasks_completed: int = 0,
        tasks_queued: int = 0,
        agents_active: int = None,
    ):
        """Update running estimate with new metrics.

        Args:
            latencies: List of recent latency measurements
            errors: Number of errors in this period
            tasks_completed: Tasks completed in this period
            tasks_queued: Current queue depth
            agents_active: Number of active agents

        """
        # Snapshot current state for history
        self._snapshot()

        # Update timestamp
        self.estimate.timestamp = datetime.utcnow().isoformat()

        # Update latency percentiles
        if latencies:
            sorted_lat = sorted(latencies)
            n = len(sorted_lat)
            self.estimate.p50_latency_ms = sorted_lat[int(n * 0.5)] if n > 0 else 0
            self.estimate.p95_latency_ms = sorted_lat[int(n * 0.95)] if n > 0 else 0
            self.estimate.p99_latency_ms = sorted_lat[int(n * 0.99)] if n > 0 else 0

        # Update task metrics
        self.estimate.tasks_completed += tasks_completed
        self.estimate.tasks_failed += errors
        self.estimate.tasks_queued = tasks_queued

        # Update agent availability
        if agents_active is not None:
            self.estimate.agent_availability = agents_active
            self.estimate.agents_on_shift = agents_active

        # Calculate error rate
        total_attempts = self.estimate.tasks_completed + self.estimate.tasks_failed
        if total_attempts > 0:
            self.estimate.error_rate = self.estimate.tasks_failed / total_attempts

        # Check kill conditions
        self._check_kill_conditions()

    def _snapshot(self):
        """Save current state to history."""
        snapshot = {
            "timestamp": self.estimate.timestamp,
            "agent_availability": self.estimate.agent_availability,
            "p99_latency_ms": self.estimate.p99_latency_ms,
            "error_rate": self.estimate.error_rate,
            "tasks_queued": self.estimate.tasks_queued,
        }
        self.estimate.history.append(snapshot)

        # Trim history
        if len(self.estimate.history) > self.MAX_HISTORY:
            self.estimate.history = self.estimate.history[-self.MAX_HISTORY :]

    def _check_kill_conditions(self):
        """Check and update kill-switch conditions."""
        self.estimate.kill_conditions["p99_exceeded"] = (
            self.estimate.p99_latency_ms > self.KILL_P99_LATENCY_MS
        )
        self.estimate.kill_conditions["error_rate_exceeded"] = (
            self.estimate.error_rate > self.KILL_ERROR_RATE
        )
        self.estimate.kill_conditions["queue_overflow"] = (
            self.estimate.tasks_queued > self.KILL_QUEUE_DEPTH
        )

    def should_throttle(self) -> bool:
        """Check if any kill condition is active."""
        return any(self.estimate.kill_conditions.values())

    def get_throttle_tier(self) -> str:
        """Get recommended tier to throttle based on conditions."""
        if self.estimate.kill_conditions["p99_exceeded"]:
            return "FREE"  # Throttle FREE tier first
        if self.estimate.kill_conditions["error_rate_exceeded"]:
            return "FLASH"  # Then FLASH
        if self.estimate.kill_conditions["queue_overflow"]:
            return "PRO"  # Finally PRO
        return None

    def update_squad(self, squad_id: int, active: int, queued: int, latency: float):
        """Update squad-specific metrics."""
        self.estimate.squad_utilization[squad_id] = active / 25  # 25 agents per squad
        if active > 0 and squad_id not in self.estimate.squad_utilization:
            self.estimate.squads_active += 1

    def get_estimate(self) -> dict:
        """Get current running estimate as dictionary."""
        return asdict(self.estimate)

    def get_decision_support(self) -> dict:
        """Get decision support summary.

        Returns key metrics and recommendations for operators.
        """
        return {
            "timestamp": self.estimate.timestamp,
            "health": "RED" if self.should_throttle() else "GREEN",
            "recommendations": self._get_recommendations(),
            "key_metrics": {
                "availability": f"{self.estimate.agent_availability}/{self.estimate.total_agents}",
                "p99_latency": f"{self.estimate.p99_latency_ms:.0f}ms",
                "error_rate": f"{self.estimate.error_rate:.1%}",
                "queue_depth": self.estimate.tasks_queued,
            },
            "kill_conditions": self.estimate.kill_conditions,
        }

    def _get_recommendations(self) -> list[str]:
        """Generate recommendations based on current state."""
        recs = []

        if self.estimate.kill_conditions["p99_exceeded"]:
            recs.append(
                f"THROTTLE FREE tier: p99 latency {self.estimate.p99_latency_ms:.0f}ms > {self.KILL_P99_LATENCY_MS}ms",
            )

        if self.estimate.kill_conditions["error_rate_exceeded"]:
            recs.append(
                f"INVESTIGATE errors: rate {self.estimate.error_rate:.1%} > {self.KILL_ERROR_RATE:.1%}",
            )

        if self.estimate.kill_conditions["queue_overflow"]:
            recs.append(
                f"SCALE UP: queue depth {self.estimate.tasks_queued} > {self.KILL_QUEUE_DEPTH}",
            )

        if self.estimate.agent_availability < self.TOTAL_AGENTS * 0.5:
            recs.append(f"ROTATE agents: only {self.estimate.agent_availability} available")

        if not recs:
            recs.append("All systems nominal")

        return recs


def main():
    """CLI interface for running estimate manager."""
    import argparse

    import numpy as np

    parser = argparse.ArgumentParser(description="FM 6-0 Running Estimate Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Get current estimate
    subparsers.add_parser("status", help="Get current running estimate")

    # Get decision support
    subparsers.add_parser("decide", help="Get decision support summary")

    # Simulate updates
    sim_parser = subparsers.add_parser("simulate", help="Simulate metric updates")
    sim_parser.add_argument("--updates", type=int, default=10, help="Number of updates")

    args = parser.parse_args()

    manager = RunningEstimateManager()

    if args.command == "status":
        estimate = manager.get_estimate()
        print(json.dumps(estimate, indent=2, default=str))

    elif args.command == "decide":
        support = manager.get_decision_support()
        print(f"///▞ Health: {support['health']}")
        print("///▞ Metrics:")
        for k, v in support["key_metrics"].items():
            print(f"    {k}: {v}")
        print("///▞ Recommendations:")
        for rec in support["recommendations"]:
            print(f"    • {rec}")

    elif args.command == "simulate":
        print(f"///▞ Simulating {args.updates} updates...")
        for _i in range(args.updates):
            # Generate random metrics
            latencies = np.random.exponential(100, 100).tolist()
            errors = np.random.poisson(2)
            completed = np.random.poisson(50)
            queued = np.random.poisson(100)

            manager.update(
                latencies=latencies,
                errors=errors,
                tasks_completed=completed,
                tasks_queued=queued,
            )

            time.sleep(0.1)

        support = manager.get_decision_support()
        print("\n///▞ Final state:")
        print(f"    Health: {support['health']}")
        print(f"    P99: {support['key_metrics']['p99_latency']}")
        print(f"    Errors: {support['key_metrics']['error_rate']}")
        print(f"    Queue: {support['key_metrics']['queue_depth']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
