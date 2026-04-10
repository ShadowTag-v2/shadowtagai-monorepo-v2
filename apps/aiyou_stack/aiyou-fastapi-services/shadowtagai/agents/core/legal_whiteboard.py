"""
Legal Whiteboard - Persistent Agent Evolution System

GitHub-based persistent memory for agent evolution across context windows.
Implements "Never Resting, Ever Vesting" principle.

Author: Antigravity (Gemini 2.0 Flash Experimental)
Created: 2025-11-22
"""

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class AgentState:
    """Persistent agent state stored in GitHub"""

    agent_id: str
    level: int = 0
    tasks_completed: int = 0
    success_rate: float = 1.0
    knowledge_graph: dict[str, Any] = field(default_factory=dict)
    task_history: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def load_from_git(cls, agent_id: str) -> "AgentState":
        """Read agent state from GitHub repo"""
        base_path = Path(__file__).parent.parent / "state"
        state_file = base_path / f"{agent_id}.json"

        try:
            with open(state_file) as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            # New agent, create default state
            print(f"📝 Creating new agent state for: {agent_id}")
            return cls(agent_id=agent_id)

    def save_to_git(self, commit_message: str) -> None:
        """Persist state to GitHub with commit"""
        base_path = Path(__file__).parent.parent / "state"
        base_path.mkdir(parents=True, exist_ok=True)

        state_file = base_path / f"{self.agent_id}.json"

        # Update timestamp
        self.last_updated = datetime.now().isoformat()

        # Write state
        with open(state_file, "w") as f:
            json.dump(asdict(self), f, indent=2)

        # Git commit + push
        try:
            subprocess.run(["git", "add", str(state_file)], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=False)
            print(f"✅ Agent state persisted: {commit_message}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git operation failed: {e}")
            print("   State saved locally, but not pushed to remote")

    def update_after_task(self, task_result: dict[str, Any]) -> None:
        """Update state after task completion"""
        self.tasks_completed += 1

        # Update success rate (exponential moving average)
        success = 1.0 if task_result.get("success", False) else 0.0
        alpha = 0.1  # Smoothing factor
        self.success_rate = alpha * success + (1 - alpha) * self.success_rate

        # Update knowledge graph
        if "learnings" in task_result:
            for key, value in task_result["learnings"].items():
                self.knowledge_graph[key] = value

        # Add to task history (keep last 100 tasks)
        self.task_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "task_type": task_result.get("task_type", "unknown"),
                "success": task_result.get("success", False),
                "duration_ms": task_result.get("duration_ms", 0),
                "learnings": task_result.get("learnings", {}),
            }
        )
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]

        # Check for level up
        self.check_level_progression()

    def check_level_progression(self) -> None:
        """Evaluate if agent qualifies for next level"""
        try:
            from shadowtagai.agents.core.bar_exam_protocol import BarExamGate

            current_level = self.level
            qualified_level = BarExamGate.evaluate(self)

            if qualified_level > current_level:
                self.level = qualified_level
                print(f"🎓 Agent {self.agent_id} advanced to Level {qualified_level}!")
                print(f"   Tasks: {self.tasks_completed}, Success Rate: {self.success_rate:.1%}")
        except ImportError:
            # Bar exam protocol not yet implemented
            pass

    def get_stats(self) -> dict[str, Any]:
        """Get agent statistics summary"""
        return {
            "agent_id": self.agent_id,
            "level": self.level,
            "tasks_completed": self.tasks_completed,
            "success_rate": self.success_rate,
            "knowledge_nodes": len(self.knowledge_graph),
            "age_days": (datetime.now() - datetime.fromisoformat(self.created_at)).days,
            "last_active": self.last_updated,
        }


class Whiteboard:
    """Central whiteboard for agent swarm coordination"""

    def __init__(self):
        """Initialize whiteboard"""
        self.base_path = Path(__file__).parent.parent / "state"
        self.base_path.mkdir(parents=True, exist_ok=True)

    def load_agent_state(self, agent_id: str, create_if_missing: bool = False) -> AgentState:
        """
        Load agent state from GitHub repo.

        Args:
            agent_id: Agent identifier
            create_if_missing: Create new state if not found

        Returns:
            AgentState object
        """
        state_file = self.base_path / f"{agent_id}.json"

        try:
            with open(state_file) as f:
                data = json.load(f)
            return AgentState(**data)
        except FileNotFoundError:
            if create_if_missing:
                print(f"📝 Creating new agent state for: {agent_id}")
                state = AgentState(agent_id=agent_id)
                self.save_agent_state(state)
                return state
            else:
                raise ValueError(f"Agent state not found: {agent_id}")

    def save_agent_state(self, state: AgentState) -> None:
        """
        Save agent state to disk.

        Args:
            state: AgentState to persist
        """
        state_file = self.base_path / f"{state.agent_id}.json"

        # Update timestamp
        state.last_updated = datetime.now().isoformat()

        # Write state
        with open(state_file, "w") as f:
            json.dump(asdict(state), f, indent=2)

        print(f"   ✓ Saved agent state: {state.agent_id}")

    def git_commit_state(self, commit_message: str) -> None:
        """
        Commit all agent states to git.

        Args:
            commit_message: Git commit message
        """
        max_retries = 3

        for attempt in range(max_retries):
            try:
                subprocess.run(["git", "add", str(self.base_path)], check=True)
                subprocess.run(["git", "commit", "-m", commit_message], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=False)
                print(f"✅ Git commit: {commit_message}")
                return
            except subprocess.CalledProcessError as e:
                self._handle_git_error(e, attempt, max_retries)

    def _handle_git_error(
        self, error: subprocess.CalledProcessError, attempt: int, max_retries: int
    ) -> None:
        """Handle git failure with retry logic"""
        import random
        import time

        if attempt < max_retries - 1:
            wait_time = 1.0 + random.random()
            print(
                f"⚠️  Git operation failed (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time:.1f}s..."
            )
            time.sleep(wait_time)

            if attempt == 1:
                self._clear_stale_lock()
        else:
            print(f"⚠️  Git operation failed after {max_retries} attempts: {error}")

    def _clear_stale_lock(self) -> None:
        """Attempt to clear stale git lock file"""
        lock_file = Path(".git/index.lock")
        if lock_file.exists():
            try:
                lock_file.unlink()
                print("🧹 Cleared stale .git/index.lock")
            except Exception as exc:
                print(f"Failed to clear lock: {exc}")

    def add_task(self, agent_id: str, task_id: str, success: bool) -> None:
        """
        Add task result to agent's history.

        Args:
            agent_id: Agent identifier
            task_id: Task identifier
            success: Whether task was successful
        """
        state = self.load_agent_state(agent_id)
        state.update_after_task(
            {"task_type": task_id, "success": success, "duration_ms": 100, "learnings": {}}
        )
        self.save_agent_state(state)

    @staticmethod
    def get_all_agents() -> list[AgentState]:
        """Load all agent states from GitHub"""
        base_path = Path(__file__).parent.parent / "state"
        base_path.mkdir(parents=True, exist_ok=True)

        agents = []
        for state_file in base_path.glob("*.json"):
            agent_id = state_file.stem
            agents.append(AgentState.load_from_git(agent_id))

        return agents

    @staticmethod
    def get_swarm_stats() -> dict[str, Any]:
        """Get statistics for entire swarm"""
        agents = Whiteboard.get_all_agents()

        if not agents:
            return {
                "total_agents": 0,
                "level_distribution": {},
                "total_tasks": 0,
                "avg_success_rate": 0.0,
            }

        level_dist: dict[int, int] = {}
        for agent in agents:
            level_dist[agent.level] = level_dist.get(agent.level, 0) + 1

        return {
            "total_agents": len(agents),
            "level_distribution": level_dist,
            "total_tasks": sum(a.tasks_completed for a in agents),
            "avg_success_rate": sum(a.success_rate for a in agents) / len(agents),
            "avg_knowledge_nodes": sum(len(a.knowledge_graph) for a in agents) / len(agents),
        }


if __name__ == "__main__":
    # Example usage
    print("═══ Legal Whiteboard Test ═══\n")

    # Create test agent
    agent = AgentState.load_from_git("test_agent_001")
    print(f"Agent stats: {agent.get_stats()}\n")

    # Simulate task completion
    agent.update_after_task(
        {
            "success": True,
            "task_type": "code_review",
            "duration_ms": 250,
            "learnings": {
                "pattern_1": "Always validate input before processing",
                "optimization_1": "Use EMA checkpoints for +2-3% accuracy",
            },
        }
    )

    # Save to git
    agent.save_to_git(f"Agent {agent.agent_id}: Completed task #{agent.tasks_completed}")

    # Show swarm stats
    print("\n═══ Swarm Statistics ═══")
    stats = Whiteboard.get_swarm_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
