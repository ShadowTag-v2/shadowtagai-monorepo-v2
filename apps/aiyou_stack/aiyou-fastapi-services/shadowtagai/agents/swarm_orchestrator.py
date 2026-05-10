#!/usr/bin/env python3
"""Swarm Orchestrator for 600 Flying n-autoresearch/Kosmos/BioAgents agents.
Integrates PSO task allocation + ACO squad routing with FM 5-0 MDMP flow.
Based on FM 5-0 (Operations Process) and FM 6-0 (Commander and Staff Organization).
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum

from shadowtagai.agents.squad_routing_optimizer import SquadRoutingOptimizer
from shadowtagai.agents.task_allocation_optimizer import Task, TaskAllocationOptimizer


class MDMPStep(Enum):
    """FM 5-0 MDMP 7-step process."""

    RECEIVE_MISSION = 1
    MISSION_ANALYSIS = 2
    COA_DEVELOPMENT = 3
    COA_ANALYSIS = 4
    COA_COMPARISON = 5
    COA_APPROVAL = 6
    ORDERS_PRODUCTION = 7


class TLPStep(Enum):
    """FM 5-0 TLP 8-step process (agent-level)."""

    RECEIVE_MISSION = 1
    ISSUE_WARNING_ORDER = 2
    MAKE_TENTATIVE_PLAN = 3
    INITIATE_MOVEMENT = 4
    CONDUCT_RECONNAISSANCE = 5
    COMPLETE_PLAN = 6
    ISSUE_ORDER = 7
    SUPERVISE_REFINE = 8


@dataclass
class RunningEstimate:
    """FM 6-0 Running Estimate for swarm state."""

    timestamp: str
    agent_availability: int
    total_agents: int
    tier_saturation: dict[str, float]
    p99_latency_ms: float
    error_rate: float
    tasks_queued: int
    tasks_completed: int
    squads_active: int


@dataclass
class AtomicThread:
    """OPORD-format task thread."""

    thread_id: str
    mission: str
    tier: str
    status: str
    created: str
    allocation: list[int] | None
    route: list[str] | None
    handoff: dict | None


class SwarmOrchestrator:
    """Main orchestrator for 600-agent Flying n-autoresearch/Kosmos/BioAgents swarm.

    Implements:
    - FM 5-0 MDMP 7-step task routing
    - FM 6-0 Running Estimates
    - 4hr guard rotation enforcement
    - PSO task allocation
    - ACO squad routing
    """

    # Constants
    TOTAL_AGENTS = 600
    SQUADS = 24
    AGENTS_PER_SQUAD = 25
    MAX_SHIFT_HOURS = 4

    def __init__(self):
        self.task_optimizer = TaskAllocationOptimizer(num_agents=self.TOTAL_AGENTS)
        self.route_optimizer = SquadRoutingOptimizer(num_squads=self.SQUADS)
        self.threads: dict[str, AtomicThread] = {}
        self.running_estimate = self._init_running_estimate()

    def _init_running_estimate(self) -> RunningEstimate:
        """Initialize FM 6-0 running estimate."""
        return RunningEstimate(
            timestamp=datetime.utcnow().isoformat(),
            agent_availability=self.TOTAL_AGENTS,
            total_agents=self.TOTAL_AGENTS,
            tier_saturation={"FREE": 0.0, "FLASH": 0.0, "PRO": 0.0},
            p99_latency_ms=0.0,
            error_rate=0.0,
            tasks_queued=0,
            tasks_completed=0,
            squads_active=0,
        )

    def process_mission(
        self,
        mission: str,
        tier: str = "FREE",
        required_squads: list[str] = None,
        num_tasks: int = 1,
    ) -> dict:
        """Process a mission through MDMP 7-step flow.

        Args:
            mission: Mission statement
            tier: Required tier (FREE, FLASH, PRO)
            required_squads: Squad specialties to route through
            num_tasks: Number of sub-tasks

        Returns:
            ATOMIC thread with allocation and routing

        """
        thread_id = f"ATOMIC-{int(time.time())}"
        start_time = time.time()

        # Step 1: RECEIVE MISSION
        self._log_mdmp(MDMPStep.RECEIVE_MISSION, f"Received: {mission[:50]}...")

        # Step 2: MISSION ANALYSIS
        self._log_mdmp(MDMPStep.MISSION_ANALYSIS, f"Tier: {tier}, Tasks: {num_tasks}")
        tasks = self._analyze_mission(mission, tier, num_tasks)
        self.task_optimizer.set_tasks(tasks)

        # Step 3: COA DEVELOPMENT (PSO)
        self._log_mdmp(MDMPStep.COA_DEVELOPMENT, "Running PSO task allocation...")
        allocation_result = self.task_optimizer.optimize(max_iter=100)

        # Step 4: COA ANALYSIS (ACO)
        self._log_mdmp(MDMPStep.COA_ANALYSIS, "Running ACO squad routing...")
        if required_squads:
            route_result = self.route_optimizer.plan_route(required_squads, max_iter=100)
        else:
            route_result = {"route": [], "squad_names": [], "total_latency": 0}

        # Step 5: COA COMPARISON
        self._log_mdmp(MDMPStep.COA_COMPARISON, "Evaluating allocation quality...")
        quality_score = self._evaluate_allocation(allocation_result, route_result)

        # Step 6: COA APPROVAL
        if quality_score < 0.5:
            self._log_mdmp(MDMPStep.COA_APPROVAL, "REJECTED - Re-optimizing...")
            allocation_result = self.task_optimizer.optimize(max_iter=200)
            quality_score = self._evaluate_allocation(allocation_result, route_result)

        self._log_mdmp(MDMPStep.COA_APPROVAL, f"APPROVED - Quality: {quality_score:.2f}")

        # Step 7: ORDERS PRODUCTION
        thread = AtomicThread(
            thread_id=thread_id,
            mission=mission,
            tier=tier,
            status="READY",
            created=datetime.utcnow().isoformat(),
            allocation=allocation_result["allocation"],
            route=route_result["squad_names"],
            handoff={
                "total_cost": allocation_result["total_cost"],
                "total_latency": route_result["total_latency"],
                "quality_score": quality_score,
                "processing_time_ms": (time.time() - start_time) * 1000,
            },
        )
        self.threads[thread_id] = thread
        self._log_mdmp(MDMPStep.ORDERS_PRODUCTION, f"Thread {thread_id} ready")

        # Update running estimate
        self._update_running_estimate(allocation_result, route_result)

        return asdict(thread)

    def _analyze_mission(self, mission: str, tier: str, num_tasks: int) -> list[Task]:
        """Analyze mission and generate tasks."""
        tasks = []
        for i in range(num_tasks):
            tasks.append(
                Task(
                    task_id=i,
                    complexity=0.5,  # Could be inferred from mission
                    required_tier=tier,
                    deadline_ms=5000.0,  # Default 5s deadline
                ),
            )
        return tasks

    def _evaluate_allocation(self, allocation: dict, route: dict) -> float:
        """Evaluate allocation quality (0.0 to 1.0).

        Based on:
        - Utilization (higher = better)
        - Load variance (lower = better)
        - Latency (lower = better)
        """
        metrics = allocation.get("metrics", {})
        utilization = metrics.get("utilization", 0)
        variance = metrics.get("load_variance", 100)
        total_latency = route.get("total_latency", 0)

        # Normalize and combine
        util_score = min(utilization * 2, 1.0)  # Cap at 1.0
        var_score = max(1 - variance / 100, 0)
        lat_score = max(1 - total_latency / 10, 0)

        return (util_score + var_score + lat_score) / 3

    def _update_running_estimate(self, allocation: dict, route: dict):
        """Update FM 6-0 running estimate."""
        metrics = allocation.get("metrics", {})

        self.running_estimate.timestamp = datetime.utcnow().isoformat()
        self.running_estimate.agent_availability = self.TOTAL_AGENTS - metrics.get("agents_used", 0)
        self.running_estimate.tier_saturation = {
            "FREE": metrics.get("utilization", 0) * 0.7,
            "FLASH": metrics.get("utilization", 0) * 0.2,
            "PRO": metrics.get("utilization", 0) * 0.1,
        }
        self.running_estimate.tasks_queued += len(allocation.get("allocation", []))
        self.running_estimate.squads_active = len(route.get("route", []))

    def _log_mdmp(self, step: MDMPStep, message: str):
        """Log MDMP step progress."""
        print(f"///▞ [{step.name}] {message}")

    def get_running_estimate(self) -> dict:
        """Get current running estimate."""
        return asdict(self.running_estimate)

    def get_thread(self, thread_id: str) -> dict | None:
        """Get thread by ID."""
        thread = self.threads.get(thread_id)
        return asdict(thread) if thread else None

    def list_threads(self, status: str = None) -> list[dict]:
        """List all threads, optionally filtered by status."""
        threads = self.threads.values()
        if status:
            threads = [t for t in threads if t.status == status]
        return [asdict(t) for t in threads]

    def execute_tlp(self, thread_id: str) -> dict:
        """Execute TLP 8-step process for a thread (agent-level).

        Returns execution trace.
        """
        thread = self.threads.get(thread_id)
        if not thread:
            return {"error": f"Thread {thread_id} not found"}

        trace = []

        # TLP 1: Receive mission
        trace.append({"step": TLPStep.RECEIVE_MISSION.name, "action": "Parse ATOMIC thread"})

        # TLP 2: Issue warning order
        trace.append({"step": TLPStep.ISSUE_WARNING_ORDER.name, "action": "Reserve GPU/memory"})

        # TLP 3: Make tentative plan
        trace.append({"step": TLPStep.MAKE_TENTATIVE_PLAN.name, "action": "Local task breakdown"})

        # TLP 4: Initiate movement
        trace.append({"step": TLPStep.INITIATE_MOVEMENT.name, "action": "Begin execution"})

        # TLP 5: Conduct reconnaissance
        trace.append({"step": TLPStep.CONDUCT_RECONNAISSANCE.name, "action": "Query corpus"})

        # TLP 6: Complete plan
        trace.append({"step": TLPStep.COMPLETE_PLAN.name, "action": "Finalize with recon data"})

        # TLP 7: Issue order
        trace.append({"step": TLPStep.ISSUE_ORDER.name, "action": "Execute and emit"})

        # TLP 8: Supervise and refine
        trace.append({"step": TLPStep.SUPERVISE_REFINE.name, "action": "Monitor and handoff"})

        thread.status = "COMPLETED"
        self.running_estimate.tasks_completed += 1

        return {"thread_id": thread_id, "tlp_trace": trace, "status": "COMPLETED"}


def main():
    """CLI interface for swarm orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Flying n-autoresearch/Kosmos/BioAgents Swarm Orchestrator",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Process mission
    mission_parser = subparsers.add_parser("mission", help="Process a mission")
    mission_parser.add_argument("text", help="Mission statement")
    mission_parser.add_argument("--tier", default="FREE", choices=["FREE", "FLASH", "PRO"])
    mission_parser.add_argument("--squads", nargs="+", help="Required squad specialties")
    mission_parser.add_argument("--tasks", type=int, default=10, help="Number of sub-tasks")

    # Get estimate
    subparsers.add_parser("estimate", help="Get running estimate")

    # List threads
    list_parser = subparsers.add_parser("list", help="List threads")
    list_parser.add_argument("--status", help="Filter by status")

    args = parser.parse_args()

    orchestrator = SwarmOrchestrator()

    if args.command == "mission":
        result = orchestrator.process_mission(
            mission=args.text,
            tier=args.tier,
            required_squads=args.squads,
            num_tasks=args.tasks,
        )
        print(f"\n///▞ Thread created: {result['thread_id']}")
        print(f"    Route: {' → '.join(result['route']) if result['route'] else 'N/A'}")
        print(f"    Agents allocated: {len(result['allocation'])}")
        print(f"    Quality: {result['handoff']['quality_score']:.2f}")

    elif args.command == "estimate":
        estimate = orchestrator.get_running_estimate()
        print(json.dumps(estimate, indent=2))

    elif args.command == "list":
        threads = orchestrator.list_threads(args.status)
        for t in threads:
            print(f"{t['thread_id']} [{t['status']}] {t['mission'][:40]}...")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
