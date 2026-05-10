#!/usr/bin/env python3
"""Memory Fabric for 600-agent Flying n-autoresearch/Kosmos/BioAgents swarm.
Implements 3-tier coordination: global, team, agent.
Based on patterns from yyz-agentics-june SPARC orchestrator.
"""

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np


@dataclass
class MemoryEntry:
    """A single memory entry."""

    key: str
    value: Any
    tier: str  # global, team, agent
    created: float
    updated: float
    ttl: float | None = None  # Time to live in seconds
    metadata: dict = field(default_factory=dict)


class MemoryFabric:
    """3-tier memory coordination for Flying n-autoresearch/Kosmos/BioAgents swarm.

    Tiers:
    - Global: Shared by all 600 agents (fitness landscape, best positions)
    - Team: Shared by squad of 25 agents (local optima, pheromones)
    - Agent: Private to individual agent (position, velocity, history)

    Enables cross-agent knowledge sharing and coordination.
    """

    def __init__(
        self,
        num_agents: int = 600,
        num_squads: int = 24,
        default_ttl: float = 3600.0,  # 1 hour
    ):
        """Initialize memory fabric.

        Args:
            num_agents: Total agents in swarm
            num_squads: Number of squads (teams)
            default_ttl: Default time to live for entries

        """
        self.num_agents = num_agents
        self.num_squads = num_squads
        self.default_ttl = default_ttl

        # Memory tiers
        self._global: dict[str, MemoryEntry] = {}
        self._team: dict[int, dict[str, MemoryEntry]] = defaultdict(dict)
        self._agent: dict[int, dict[str, MemoryEntry]] = defaultdict(dict)

        # Initialize with default entries
        self._init_global()
        self._init_teams()

    def _init_global(self):
        """Initialize global memory with defaults."""
        self.set_global("best_fitness", float("inf"))
        self.set_global("best_position", None)
        self.set_global("iteration", 0)
        self.set_global("convergence_history", [])
        self.set_global("active_agents", self.num_agents)

    def _init_teams(self):
        """Initialize team memory for each squad."""
        for squad_id in range(self.num_squads):
            self.set_team(squad_id, "local_best_fitness", float("inf"))
            self.set_team(squad_id, "local_best_position", None)
            self.set_team(squad_id, "pheromone_trail", np.ones((25, 25)))
            self.set_team(squad_id, "active_agents", 25)

    # Global memory operations
    def set_global(self, key: str, value: Any, ttl: float = None, **metadata):
        """Store value in global memory."""
        now = time.time()
        self._global[key] = MemoryEntry(
            key=key,
            value=value,
            tier="global",
            created=now,
            updated=now,
            ttl=ttl or self.default_ttl,
            metadata=metadata,
        )

    def get_global(self, key: str, default: Any = None) -> Any:
        """Get value from global memory."""
        entry = self._global.get(key)
        if entry is None:
            return default
        if entry.ttl and (time.time() - entry.updated) > entry.ttl:
            del self._global[key]
            return default
        return entry.value

    # Team memory operations
    def set_team(self, squad_id: int, key: str, value: Any, ttl: float = None, **metadata):
        """Store value in team memory."""
        now = time.time()
        self._team[squad_id][key] = MemoryEntry(
            key=key,
            value=value,
            tier="team",
            created=now,
            updated=now,
            ttl=ttl or self.default_ttl,
            metadata=metadata,
        )

    def get_team(self, squad_id: int, key: str, default: Any = None) -> Any:
        """Get value from team memory."""
        team_mem = self._team.get(squad_id, {})
        entry = team_mem.get(key)
        if entry is None:
            return default
        if entry.ttl and (time.time() - entry.updated) > entry.ttl:
            del self._team[squad_id][key]
            return default
        return entry.value

    # Agent memory operations
    def set_agent(self, agent_id: int, key: str, value: Any, ttl: float = None, **metadata):
        """Store value in agent memory."""
        now = time.time()
        self._agent[agent_id][key] = MemoryEntry(
            key=key,
            value=value,
            tier="agent",
            created=now,
            updated=now,
            ttl=ttl or self.default_ttl,
            metadata=metadata,
        )

    def get_agent(self, agent_id: int, key: str, default: Any = None) -> Any:
        """Get value from agent memory."""
        agent_mem = self._agent.get(agent_id, {})
        entry = agent_mem.get(key)
        if entry is None:
            return default
        if entry.ttl and (time.time() - entry.updated) > entry.ttl:
            del self._agent[agent_id][key]
            return default
        return entry.value

    # Bulk operations
    def update_global_best(self, fitness: float, position: np.ndarray):
        """Update global best if improved."""
        current_best = self.get_global("best_fitness", float("inf"))
        if fitness < current_best:
            self.set_global("best_fitness", fitness)
            self.set_global(
                "best_position",
                position.tolist() if isinstance(position, np.ndarray) else position,
            )

            # Update history
            history = self.get_global("convergence_history", [])
            history.append(
                {
                    "iteration": self.get_global("iteration", 0),
                    "fitness": fitness,
                    "timestamp": time.time(),
                },
            )
            self.set_global("convergence_history", history)
            return True
        return False

    def update_team_best(self, squad_id: int, fitness: float, position: np.ndarray):
        """Update team best if improved."""
        current_best = self.get_team(squad_id, "local_best_fitness", float("inf"))
        if fitness < current_best:
            self.set_team(squad_id, "local_best_fitness", fitness)
            self.set_team(
                squad_id,
                "local_best_position",
                position.tolist() if isinstance(position, np.ndarray) else position,
            )
            return True
        return False

    def get_agent_squad(self, agent_id: int) -> int:
        """Get squad ID for an agent."""
        return agent_id // 25

    def get_squad_agents(self, squad_id: int) -> list[int]:
        """Get all agent IDs in a squad."""
        start = squad_id * 25
        return list(range(start, start + 25))

    # PSO-specific operations
    def store_particle_state(
        self,
        agent_id: int,
        position: np.ndarray,
        velocity: np.ndarray,
        fitness: float,
    ):
        """Store full particle state."""
        self.set_agent(agent_id, "position", position.tolist())
        self.set_agent(agent_id, "velocity", velocity.tolist())
        self.set_agent(agent_id, "fitness", fitness)

        # Update personal best
        personal_best = self.get_agent(agent_id, "best_fitness", float("inf"))
        if fitness < personal_best:
            self.set_agent(agent_id, "best_fitness", fitness)
            self.set_agent(agent_id, "best_position", position.tolist())

        # Update team best
        squad_id = self.get_agent_squad(agent_id)
        self.update_team_best(squad_id, fitness, position)

        # Update global best
        self.update_global_best(fitness, position)

    def get_particle_state(self, agent_id: int) -> dict:
        """Get full particle state."""
        return {
            "position": self.get_agent(agent_id, "position"),
            "velocity": self.get_agent(agent_id, "velocity"),
            "fitness": self.get_agent(agent_id, "fitness"),
            "best_fitness": self.get_agent(agent_id, "best_fitness"),
            "best_position": self.get_agent(agent_id, "best_position"),
        }

    # ACO-specific operations
    def update_pheromones(
        self,
        squad_id: int,
        route: list[int],
        quality: float,
        evaporation: float = 0.1,
    ):
        """Update pheromone trails for a squad."""
        pheromones = self.get_team(squad_id, "pheromone_trail")
        if pheromones is None:
            pheromones = np.ones((25, 25))

        # Evaporate
        pheromones = pheromones * (1 - evaporation)

        # Deposit along route
        for i in range(len(route) - 1):
            src, dst = route[i] % 25, route[i + 1] % 25
            pheromones[src, dst] += quality

        self.set_team(squad_id, "pheromone_trail", pheromones)

    def get_pheromones(self, squad_id: int) -> np.ndarray:
        """Get pheromone matrix for a squad."""
        pheromones = self.get_team(squad_id, "pheromone_trail")
        if isinstance(pheromones, list):
            pheromones = np.array(pheromones)
        return pheromones

    # Export/import
    def export_state(self) -> dict:
        """Export full memory state."""

        def serialize_entry(entry: MemoryEntry) -> dict:
            value = entry.value
            if isinstance(value, np.ndarray):
                value = value.tolist()
            return {
                "key": entry.key,
                "value": value,
                "tier": entry.tier,
                "created": entry.created,
                "updated": entry.updated,
            }

        return {
            "global": {k: serialize_entry(v) for k, v in self._global.items()},
            "team": {
                str(squad_id): {k: serialize_entry(v) for k, v in team.items()}
                for squad_id, team in self._team.items()
            },
            "agent": {
                str(agent_id): {k: serialize_entry(v) for k, v in agent.items()}
                for agent_id, agent in self._agent.items()
            },
            "metadata": {
                "num_agents": self.num_agents,
                "num_squads": self.num_squads,
                "exported_at": datetime.utcnow().isoformat(),
            },
        }

    def import_state(self, state: dict):
        """Import memory state."""
        # Import global
        for key, entry_data in state.get("global", {}).items():
            self.set_global(key, entry_data["value"])

        # Import team
        for squad_id, team_data in state.get("team", {}).items():
            for key, entry_data in team_data.items():
                self.set_team(int(squad_id), key, entry_data["value"])

        # Import agent
        for agent_id, agent_data in state.get("agent", {}).items():
            for key, entry_data in agent_data.items():
                self.set_agent(int(agent_id), key, entry_data["value"])

    # Metrics
    def get_metrics(self) -> dict:
        """Get memory usage metrics."""
        return {
            "global_entries": len(self._global),
            "team_entries": sum(len(t) for t in self._team.values()),
            "agent_entries": sum(len(a) for a in self._agent.values()),
            "teams_with_data": len(self._team),
            "agents_with_data": len(self._agent),
            "best_fitness": self.get_global("best_fitness"),
            "iteration": self.get_global("iteration"),
        }

    def clear_expired(self):
        """Remove expired entries."""
        now = time.time()

        # Clear global
        expired_global = [k for k, v in self._global.items() if v.ttl and (now - v.updated) > v.ttl]
        for k in expired_global:
            del self._global[k]

        # Clear team
        for _squad_id, team in list(self._team.items()):
            expired = [k for k, v in team.items() if v.ttl and (now - v.updated) > v.ttl]
            for k in expired:
                del team[k]

        # Clear agent
        for _agent_id, agent in list(self._agent.items()):
            expired = [k for k, v in agent.items() if v.ttl and (now - v.updated) > v.ttl]
            for k in expired:
                del agent[k]


def main():
    """Demo of memory fabric usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Memory Fabric Demo")
    parser.add_argument("--agents", type=int, default=600, help="Number of agents")
    parser.add_argument("--squads", type=int, default=24, help="Number of squads")
    parser.add_argument("--export", help="Export state to file")

    args = parser.parse_args()

    print(f"///▞ Initializing memory fabric: {args.agents} agents, {args.squads} squads")

    fabric = MemoryFabric(num_agents=args.agents, num_squads=args.squads)

    # Simulate some operations
    print("///▞ Simulating swarm operations...")

    # Store particle states
    for i in range(args.agents):
        position = np.random.uniform(0, 599, 100)
        velocity = np.random.uniform(-1, 1, 100)
        fitness = np.sum(position**2)

        fabric.store_particle_state(i, position, velocity, fitness)

    # Update global iteration
    fabric.set_global("iteration", 1)

    # Update pheromones
    for squad_id in range(args.squads):
        route = list(range(5))
        fabric.update_pheromones(squad_id, route, quality=1.0)

    # Get metrics
    metrics = fabric.get_metrics()
    print("///▞ Memory metrics:")
    print(f"    Global entries: {metrics['global_entries']}")
    print(f"    Team entries: {metrics['team_entries']}")
    print(f"    Agent entries: {metrics['agent_entries']}")
    print(f"    Best fitness: {metrics['best_fitness']:.2f}")

    # Get specific states
    print("\n///▞ Sample particle state (agent 0):")
    state = fabric.get_particle_state(0)
    print(f"    Fitness: {state['fitness']:.2f}")
    print(f"    Best fitness: {state['best_fitness']:.2f}")

    print("\n///▞ Global best:")
    print(f"    Fitness: {fabric.get_global('best_fitness'):.2f}")

    if args.export:
        state = fabric.export_state()
        with open(args.export, "w") as f:
            json.dump(state, f, indent=2)
        print(f"\n///▞ State exported to: {args.export}")


if __name__ == "__main__":
    main()
