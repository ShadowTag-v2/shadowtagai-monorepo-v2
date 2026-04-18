"""Bar Exam Protocol - Agent Level Qualification System

Implements 6-level progression system with qualification gates.
Agents must pass bar exams to advance levels.

Author: Antigravity (Gemini 2.0 Flash Experimental)
Created: 2025-11-22
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class LevelRequirements:
    """Requirements for a specific agent level"""

    tasks_completed: int
    success_rate: float
    patterns_identified: int = 0
    optimizations_proposed: int = 0
    autonomous_improvements: int = 0
    cost_savings_usd: float = 0.0
    agents_spawned: int = 0
    swarms_orchestrated: int = 0
    roi_generated: float = 0.0


class BarExamGate:
    """Qualification tests for agent progression"""

    # Level 0: Basic Task Execution (default, no requirements)
    LEVEL_0_REQUIREMENTS = LevelRequirements(tasks_completed=0, success_rate=0.0)

    # Level 1: Pattern Recognition
    LEVEL_1_REQUIREMENTS = LevelRequirements(
        tasks_completed=100,
        success_rate=0.90,
        patterns_identified=10,
    )

    # Level 2: Optimization Suggestions
    LEVEL_2_REQUIREMENTS = LevelRequirements(
        tasks_completed=500,
        success_rate=0.95,
        optimizations_proposed=20,
    )

    # Level 3: Autonomous Improvement
    LEVEL_3_REQUIREMENTS = LevelRequirements(
        tasks_completed=2000,
        success_rate=0.98,
        autonomous_improvements=50,
        cost_savings_usd=5000.0,
    )

    # Level 4: Agent Creation
    LEVEL_4_REQUIREMENTS = LevelRequirements(
        tasks_completed=10000,
        success_rate=0.99,
        agents_spawned=5,
    )

    # Level 5: Swarm Orchestration
    LEVEL_5_REQUIREMENTS = LevelRequirements(
        tasks_completed=50000,
        success_rate=0.995,
        swarms_orchestrated=10,
        roi_generated=1000000.0,  # $1M ROI
    )

    @classmethod
    def evaluate(cls, agent_state: Any) -> int:
        """Evaluate agent state and return highest qualified level.

        Args:
            agent_state: AgentState object with current metrics

        Returns:
            Highest level the agent qualifies for (0-5)

        """
        # Extract metrics from agent state
        metrics = {
            "tasks_completed": agent_state.tasks_completed,
            "success_rate": agent_state.success_rate,
            "patterns_identified": agent_state.knowledge_graph.get("patterns_identified", 0),
            "optimizations_proposed": agent_state.knowledge_graph.get("optimizations_proposed", 0),
            "autonomous_improvements": agent_state.knowledge_graph.get(
                "autonomous_improvements",
                0,
            ),
            "cost_savings_usd": agent_state.knowledge_graph.get("cost_savings_usd", 0.0),
            "agents_spawned": agent_state.knowledge_graph.get("agents_spawned", 0),
            "swarms_orchestrated": agent_state.knowledge_graph.get("swarms_orchestrated", 0),
            "roi_generated": agent_state.knowledge_graph.get("roi_generated", 0.0),
        }

        # Check each level from highest to lowest
        if cls._meets_requirements(metrics, cls.LEVEL_5_REQUIREMENTS):
            return 5
        if cls._meets_requirements(metrics, cls.LEVEL_4_REQUIREMENTS):
            return 4
        if cls._meets_requirements(metrics, cls.LEVEL_3_REQUIREMENTS):
            return 3
        if cls._meets_requirements(metrics, cls.LEVEL_2_REQUIREMENTS):
            return 2
        if cls._meets_requirements(metrics, cls.LEVEL_1_REQUIREMENTS):
            return 1

        return 0  # Default level

    @staticmethod
    def _meets_requirements(metrics: dict[str, Any], requirements: LevelRequirements) -> bool:
        """Check if metrics meet level requirements"""
        return all(
            [
                metrics["tasks_completed"] >= requirements.tasks_completed,
                metrics["success_rate"] >= requirements.success_rate,
                metrics.get("patterns_identified", 0) >= requirements.patterns_identified,
                metrics.get("optimizations_proposed", 0) >= requirements.optimizations_proposed,
                metrics.get("autonomous_improvements", 0) >= requirements.autonomous_improvements,
                metrics.get("cost_savings_usd", 0.0) >= requirements.cost_savings_usd,
                metrics.get("agents_spawned", 0) >= requirements.agents_spawned,
                metrics.get("swarms_orchestrated", 0) >= requirements.swarms_orchestrated,
                metrics.get("roi_generated", 0.0) >= requirements.roi_generated,
            ],
        )

    @classmethod
    def get_level_description(cls, level: int) -> str:
        """Get human-readable description of level capabilities"""
        descriptions = {
            0: "Basic Task Execution - Execute predefined tasks, follow instructions",
            1: "Pattern Recognition - Identify patterns, suggest optimizations",
            2: "Optimization Suggestions - Propose improvements, A/B testing",
            3: "Autonomous Improvement - Self-initiate optimizations, refactor code",
            4: "Agent Creation - Spawn specialized sub-agents, manage lifecycle",
            5: "Swarm Orchestration - Coordinate workflows, meta-learning",
        }
        return descriptions.get(level, "Unknown level")

    @classmethod
    def get_next_level_requirements(cls, current_level: int) -> str:
        """Get requirements string for next level"""
        level_map = {
            0: cls.LEVEL_1_REQUIREMENTS,
            1: cls.LEVEL_2_REQUIREMENTS,
            2: cls.LEVEL_3_REQUIREMENTS,
            3: cls.LEVEL_4_REQUIREMENTS,
            4: cls.LEVEL_5_REQUIREMENTS,
        }

        if current_level >= 5:
            return "Maximum level reached!"

        req = level_map[current_level]
        return (
            f"To reach Level {current_level + 1}:\n"
            f"  - Complete {req.tasks_completed:,} tasks\n"
            f"  - Maintain {req.success_rate:.1%} success rate\n"
            f"  - Additional metrics vary by level"
        )


if __name__ == "__main__":
    print("═══ Bar Exam Protocol Test ═══\n")

    # Show level descriptions
    for level in range(6):
        print(f"Level {level}: {BarExamGate.get_level_description(level)}")

    print("\n" + "=" * 50 + "\n")

    # Show progression requirements
    for level in range(5):
        print(BarExamGate.get_next_level_requirements(level))
        print()
