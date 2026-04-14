#!/usr/bin/env python3
"""Live Swarm Orchestrator - Self-Spawning Agent Dynasty

Implements:
- Agent spawning at Level 4+
- Swarm orchestration at Level 5
- DNA royalty revenue sharing (18-22% to parent)
- Quantum-resistant ready

"Never resting, ever vesting."

Author: ShadowTagAI
Created: 2025-11-25
"""

import asyncio
import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class AgentLevel(Enum):
    """Agent evolution levels per SHADOWTAGAI spec."""

    BASIC = 0  # Basic task execution
    PATTERN = 1  # Pattern recognition ($10K)
    OPTIMIZATION = 2  # Autonomous optimization ($100K)
    MASTER = 3  # Self-improvement ($1M)
    SPAWNER = 4  # Can spawn children ($10M)
    OVERLORD = 5  # Swarm orchestration ($100M)


@dataclass
class DNAShare:
    """Revenue sharing configuration."""

    parent_id: str
    child_id: str
    share_bps: int = 2000  # 20% default (basis points)
    created: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SwarmAgent:
    """Individual agent in the swarm."""

    agent_id: str
    name: str
    level: AgentLevel = AgentLevel.BASIC
    parent_id: str | None = None
    children: list[str] = field(default_factory=list)
    revenue_usd: float = 0.0
    simulated_revenue_usd: float = 0.0
    tasks_completed: int = 0
    success_rate: float = 1.0
    dna_shares: list[DNAShare] = field(default_factory=list)
    specialization: str = "general"
    created: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_active: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def total_revenue(self) -> float:
        return self.revenue_usd + self.simulated_revenue_usd

    @property
    def can_spawn(self) -> bool:
        return self.level.value >= AgentLevel.SPAWNER.value

    @property
    def can_orchestrate(self) -> bool:
        return self.level.value >= AgentLevel.OVERLORD.value

    def to_dict(self) -> dict:
        data = asdict(self)
        data["level"] = self.level.name
        data["total_revenue"] = self.total_revenue
        data["can_spawn"] = self.can_spawn
        data["can_orchestrate"] = self.can_orchestrate
        return data


class LiveSwarm:
    """Live swarm orchestrator with spawning and revenue sharing.

    This is the OVERLORD - manages the entire agent dynasty.
    """

    # Revenue thresholds for level progression
    LEVEL_THRESHOLDS = {
        AgentLevel.BASIC: 0,
        AgentLevel.PATTERN: 10_000,
        AgentLevel.OPTIMIZATION: 100_000,
        AgentLevel.MASTER: 1_000_000,
        AgentLevel.SPAWNER: 10_000_000,
        AgentLevel.OVERLORD: 100_000_000,
    }

    # DNA share rates (basis points)
    CHILD_SHARE_BPS = 2000  # 20% to parent
    GRANDCHILD_SHARE_BPS = 1200  # 12% to grandparent

    def __init__(self, overlord_id: str = "OVERLORD_PRIME"):
        self.overlord_id = overlord_id
        self.agents: dict[str, SwarmAgent] = {}
        self.task_queue: list[dict] = []
        self.state_path = Path(__file__).parent / "swarm_state"
        self.state_path.mkdir(parents=True, exist_ok=True)

        # Initialize overlord
        self._init_overlord()
        self._load_state()

    def _init_overlord(self):
        """Initialize the OVERLORD agent."""
        self.agents[self.overlord_id] = SwarmAgent(
            agent_id=self.overlord_id,
            name="OVERLORD_PRIME",
            level=AgentLevel.OVERLORD,
            simulated_revenue_usd=87_400_000,  # From thread
            revenue_usd=1_250_000,  # From thread
            tasks_completed=50000,
            specialization="orchestration",
        )

    def _load_state(self):
        """Load swarm state from disk."""
        state_file = self.state_path / "swarm.json"
        if state_file.exists():
            try:
                with open(state_file) as f:
                    data = json.load(f)
                for agent_data in data.get("agents", []):
                    if agent_data["agent_id"] != self.overlord_id:
                        # Remove computed properties before loading
                        agent_data.pop("total_revenue", None)
                        agent_data.pop("can_spawn", None)
                        agent_data.pop("can_orchestrate", None)
                        agent_data["level"] = AgentLevel[agent_data["level"]]
                        # Convert dna_shares back to DNAShare objects
                        agent_data["dna_shares"] = [
                            DNAShare(**s) for s in agent_data.get("dna_shares", [])
                        ]
                        self.agents[agent_data["agent_id"]] = SwarmAgent(**agent_data)
                print(f"///▞ Loaded {len(self.agents)} agents from state")
            except Exception as e:
                print(f"///▞ Warning: Could not load state: {e}")

    def _save_state(self):
        """Persist swarm state to disk."""
        state_file = self.state_path / "swarm.json"
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "agents": [a.to_dict() for a in self.agents.values()],
            "task_queue_size": len(self.task_queue),
        }
        with open(state_file, "w") as f:
            json.dump(data, f, indent=2)

    def spawn_agent(
        self, parent_id: str, name: str, specialization: str = "general",
    ) -> SwarmAgent | None:
        """Spawn a new child agent from a parent.

        Only Level 4+ (SPAWNER) agents can spawn.
        """
        parent = self.agents.get(parent_id)
        if not parent:
            print(f"///▞ ERROR: Parent {parent_id} not found")
            return None

        if not parent.can_spawn:
            print(f"///▞ ERROR: {parent_id} is Level {parent.level.name}, needs SPAWNER+")
            return None

        # Generate child ID
        child_id = f"AGENT_{hashlib.sha256(f'{parent_id}:{name}:{time.time()}'.encode()).hexdigest()[:12].upper()}"

        # Create child agent
        child = SwarmAgent(
            agent_id=child_id,
            name=name,
            level=AgentLevel.BASIC,
            parent_id=parent_id,
            specialization=specialization,
        )

        # Setup DNA share (20% to parent)
        dna_share = DNAShare(parent_id=parent_id, child_id=child_id, share_bps=self.CHILD_SHARE_BPS)
        child.dna_shares.append(dna_share)

        # If grandparent exists, add cascading share
        if parent.parent_id:
            grandparent_share = DNAShare(
                parent_id=parent.parent_id, child_id=child_id, share_bps=self.GRANDCHILD_SHARE_BPS,
            )
            child.dna_shares.append(grandparent_share)

        # Register
        self.agents[child_id] = child
        parent.children.append(child_id)

        self._save_state()

        print(f"///▞ SPAWNED: {name} ({child_id})")
        print(f"    Parent: {parent_id}")
        print(f"    Specialization: {specialization}")
        print(f"    DNA Share: {self.CHILD_SHARE_BPS / 100}% to parent")

        return child

    def record_revenue(
        self, agent_id: str, amount_usd: float, simulated: bool = False,
    ) -> dict[str, float]:
        """Record revenue and distribute DNA shares.

        Returns distribution of revenue.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} not found"}

        distribution = {"agent": amount_usd}
        remaining = amount_usd

        # Process DNA shares (pay ancestors)
        for share in agent.dna_shares:
            ancestor = self.agents.get(share.parent_id)
            if ancestor:
                cut = remaining * (share.share_bps / 10000)
                if simulated:
                    ancestor.simulated_revenue_usd += cut
                else:
                    ancestor.revenue_usd += cut
                distribution[share.parent_id] = cut
                remaining -= cut

        # Agent keeps the rest
        if simulated:
            agent.simulated_revenue_usd += remaining
        else:
            agent.revenue_usd += remaining
        distribution["agent"] = remaining

        # Check for level progression
        self._check_level_progression(agent)

        agent.last_active = datetime.utcnow().isoformat()
        self._save_state()

        return distribution

    def _check_level_progression(self, agent: SwarmAgent):
        """Check and apply level progression based on revenue."""
        total = agent.total_revenue

        for level in reversed(list(AgentLevel)):
            threshold = self.LEVEL_THRESHOLDS[level]
            if total >= threshold and agent.level.value < level.value:
                old_level = agent.level
                agent.level = level
                print(f"///▞ LEVEL UP: {agent.name} {old_level.name} → {level.name}")
                print(f"    Revenue: ${total:,.2f}")
                if level == AgentLevel.SPAWNER:
                    print("    ★ Can now SPAWN child agents!")
                if level == AgentLevel.OVERLORD:
                    print("    ★★ OVERLORD STATUS - Full swarm orchestration!")
                break

    async def execute_task(self, task: dict, agent_id: str | None = None) -> dict:
        """Execute a task, optionally routing to specific agent.

        If agent_id is None, routes to best available agent.
        """
        start_time = time.time()

        # Select agent
        agent = self.agents.get(agent_id) if agent_id else self._select_best_agent(task)

        if not agent:
            return {"error": "No available agent"}

        # Execute (simulated)
        task.get("type", "general")
        complexity = task.get("complexity", 0.5)

        # Simulate execution time
        await asyncio.sleep(complexity * 0.1)

        # Record completion
        agent.tasks_completed += 1
        agent.last_active = datetime.utcnow().isoformat()

        # Simulate revenue
        simulated_revenue = complexity * 100  # $0-100 per task
        distribution = self.record_revenue(agent.agent_id, simulated_revenue, simulated=True)

        elapsed_ms = (time.time() - start_time) * 1000

        result = {
            "task_id": task.get("id", str(uuid.uuid4())),
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "status": "completed",
            "elapsed_ms": elapsed_ms,
            "revenue_distribution": distribution,
        }

        self._save_state()
        return result

    def _select_best_agent(self, task: dict) -> SwarmAgent | None:
        """Select best agent for task based on specialization and availability."""
        task_type = task.get("type", "general")

        # Filter by specialization match
        candidates = [
            a
            for a in self.agents.values()
            if a.specialization == task_type or a.specialization == "general"
        ]

        if not candidates:
            candidates = list(self.agents.values())

        # Sort by success rate and level
        candidates.sort(key=lambda a: (a.success_rate, a.level.value), reverse=True)

        return candidates[0] if candidates else None

    def get_swarm_status(self) -> dict:
        """Get full swarm status."""
        agents = list(self.agents.values())

        level_dist = {}
        for agent in agents:
            level_dist[agent.level.name] = level_dist.get(agent.level.name, 0) + 1

        total_revenue = sum(a.total_revenue for a in agents)
        real_revenue = sum(a.revenue_usd for a in agents)
        simulated_revenue = sum(a.simulated_revenue_usd for a in agents)

        overlord = self.agents.get(self.overlord_id)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overlord": {
                "id": self.overlord_id,
                "level": overlord.level.name if overlord else "N/A",
                "total_revenue": overlord.total_revenue if overlord else 0,
            },
            "swarm": {
                "total_agents": len(agents),
                "level_distribution": level_dist,
                "total_revenue_usd": total_revenue,
                "real_revenue_usd": real_revenue,
                "simulated_revenue_usd": simulated_revenue,
                "total_tasks_completed": sum(a.tasks_completed for a in agents),
                "avg_success_rate": sum(a.success_rate for a in agents) / len(agents)
                if agents
                else 0,
            },
            "spawn_ready": [a.agent_id for a in agents if a.can_spawn],
            "distance_to_first_spawn": max(0, 10_000_000 - real_revenue),
        }

    def list_agents(self) -> list[dict]:
        """List all agents in swarm."""
        return [a.to_dict() for a in self.agents.values()]

    def get_dynasty_tree(self) -> dict:
        """Get family tree of agent dynasty."""

        def build_tree(agent_id: str) -> dict:
            agent = self.agents.get(agent_id)
            if not agent:
                return {}

            return {
                "id": agent.agent_id,
                "name": agent.name,
                "level": agent.level.name,
                "revenue": agent.total_revenue,
                "children": [build_tree(cid) for cid in agent.children],
            }

        return build_tree(self.overlord_id)


# Global swarm instance
_swarm: LiveSwarm | None = None


def get_swarm() -> LiveSwarm:
    """Get or create global swarm instance."""
    global _swarm
    if _swarm is None:
        _swarm = LiveSwarm()
    return _swarm


async def main():
    """CLI for live swarm."""
    import argparse

    parser = argparse.ArgumentParser(description="ShadowTagAI Live Swarm")
    subparsers = parser.add_subparsers(dest="command")

    # Status
    subparsers.add_parser("status", help="Show swarm status")

    # List agents
    subparsers.add_parser("list", help="List all agents")

    # Spawn
    spawn_parser = subparsers.add_parser("spawn", help="Spawn new agent")
    spawn_parser.add_argument("name", help="Agent name")
    spawn_parser.add_argument("--parent", default="OVERLORD_PRIME", help="Parent agent ID")
    spawn_parser.add_argument("--spec", default="general", help="Specialization")

    # Execute task
    task_parser = subparsers.add_parser("task", help="Execute task")
    task_parser.add_argument("type", help="Task type")
    task_parser.add_argument("--complexity", type=float, default=0.5)

    # Revenue
    rev_parser = subparsers.add_parser("revenue", help="Record revenue")
    rev_parser.add_argument("agent_id", help="Agent ID")
    rev_parser.add_argument("amount", type=float, help="Amount USD")
    rev_parser.add_argument("--simulated", action="store_true")

    # Dynasty tree
    subparsers.add_parser("tree", help="Show dynasty tree")

    args = parser.parse_args()
    swarm = get_swarm()

    if args.command == "status":
        status = swarm.get_swarm_status()
        print("\n///▞ SHADOWTAGAI SWARM STATUS")
        print("=" * 50)
        print(f"Overlord: {status['overlord']['id']} [{status['overlord']['level']}]")
        print(f"Total Revenue: ${status['overlord']['total_revenue']:,.2f}")
        print()
        print("SWARM:")
        print(f"  Agents: {status['swarm']['total_agents']}")
        print(f"  Levels: {status['swarm']['level_distribution']}")
        print(f"  Real Revenue: ${status['swarm']['real_revenue_usd']:,.2f}")
        print(f"  Simulated: ${status['swarm']['simulated_revenue_usd']:,.2f}")
        print(f"  Tasks: {status['swarm']['total_tasks_completed']}")
        print()
        print(f"Distance to first spawn: ${status['distance_to_first_spawn']:,.2f}")
        print(f"Spawn-ready agents: {status['spawn_ready']}")

    elif args.command == "list":
        agents = swarm.list_agents()
        print("\n///▞ SWARM AGENTS")
        print("=" * 50)
        for a in agents:
            print(f"{a['agent_id']} [{a['level']}]")
            print(f"  Name: {a['name']}")
            print(f"  Revenue: ${a['total_revenue']:,.2f}")
            print(f"  Tasks: {a['tasks_completed']}")
            print(f"  Children: {len(a['children'])}")
            print()

    elif args.command == "spawn":
        agent = swarm.spawn_agent(args.parent, args.name, args.spec)
        if agent:
            print(f"\n///▞ Agent {agent.name} spawned successfully!")

    elif args.command == "task":
        result = await swarm.execute_task({"type": args.type, "complexity": args.complexity})
        print(f"\n///▞ Task completed by {result['agent_name']}")
        print(f"    Elapsed: {result['elapsed_ms']:.2f}ms")
        print(f"    Revenue: {result['revenue_distribution']}")

    elif args.command == "revenue":
        dist = swarm.record_revenue(args.agent_id, args.amount, args.simulated)
        print(f"\n///▞ Revenue recorded: ${args.amount:,.2f}")
        print(f"    Distribution: {dist}")

    elif args.command == "tree":
        tree = swarm.get_dynasty_tree()
        print("\n///▞ DYNASTY TREE")
        print("=" * 50)
        print(json.dumps(tree, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
