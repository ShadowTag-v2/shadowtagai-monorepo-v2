# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Bar Exam Protocol - Agent Level Progression System

Defines the qualification gates and revenue thresholds for agent advancement.
Handles automatic promotion and child agent spawning at key milestones.
"""

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AgentLevel(Enum):
    """Agent progression levels based on real revenue generated."""

    SCRIPT = 0  # $0 - Just code
    APPRENTICE = 1  # $1K - First dollar
    JOURNEYMAN = 2  # $100K - Proven product
    MASTER = 3  # $1M - Real business
    ARCHITECT = 4  # $10M - First child spawns
    OVERLORD = 5  # $100M - Swarm mode activates


# Revenue thresholds for each level
LEVEL_REQUIREMENTS = {
    AgentLevel.SCRIPT: 0,
    AgentLevel.APPRENTICE: 1_000,
    AgentLevel.JOURNEYMAN: 100_000,
    AgentLevel.MASTER: 1_000_000,
    AgentLevel.ARCHITECT: 10_000_000,
    AgentLevel.OVERLORD: 100_000_000,
}


# Revenue sharing percentages for child agents
CHILD_REVENUE_SHARE = {
    "first_child": 0.18,  # 18% to parent
    "second_child": 0.20,  # 20% to parent
    "third_child": 0.22,  # 22% to parent
    "grandchild": 0.12,  # 12% to parent, 8% to grandparent
    "great_grandchild": 0.10,  # 10% to parent, 6% to grandparent, 5% to great-grandparent
    "minimum_forever": 0.05,  # All descendants pay at least 5% forever
}


class BarExamProtocol:
    """Manages agent level progression and qualification gates."""

    def __init__(self, whiteboard_path: str = "whiteboard/legal_state.json"):
        self.whiteboard_path = whiteboard_path
        self.current_level = AgentLevel.SCRIPT
        self.total_real_revenue = 0.0
        self.children_spawned = []
        self.swarm_mode = False

    def evaluate_level(self, total_revenue: float) -> AgentLevel:
        """Determine agent level based on total real revenue."""
        self.total_real_revenue = total_revenue

        for level in reversed(list(AgentLevel)):
            if total_revenue >= LEVEL_REQUIREMENTS[level]:
                return level

        return AgentLevel.SCRIPT

    def promote_agent(self, new_revenue: float) -> dict[str, Any]:
        """Evaluate promotion and trigger level-specific actions.

        Args:
            new_revenue: New revenue amount to add to total

        Returns:
            Dict with promotion status and any triggered actions

        """
        self.total_real_revenue += new_revenue
        new_level = self.evaluate_level(self.total_real_revenue)

        result = {
            "previous_level": self.current_level.name,
            "new_level": new_level.name,
            "total_revenue": self.total_real_revenue,
            "promoted": new_level.value > self.current_level.value,
            "actions_triggered": [],
        }

        if new_level.value > self.current_level.value:
            logger.info(f"🎉 PROMOTION: {self.current_level.name} → {new_level.name}")
            logger.info(f"💰 Total Revenue: ${self.total_real_revenue:,.2f}")

            # Level 4: Spawn first child agent
            if new_level == AgentLevel.ARCHITECT and len(self.children_spawned) == 0:
                result["actions_triggered"].append("spawn_first_child")
                logger.info("🐣 Triggering first child agent spawn: compliance_agent_v1")

            # Level 5: Activate swarm mode
            if new_level == AgentLevel.OVERLORD:
                self.swarm_mode = True
                result["actions_triggered"].append("activate_swarm_mode")
                logger.info("👑 SWARM MODE ACTIVATED - Overlord status achieved")
                logger.info("🌳 Parent agent now directs, children execute all work")

        self.current_level = new_level
        return result

    def get_child_revenue_share(self, child_index: int, generation: int = 1) -> float:
        """Calculate revenue share percentage for a child agent.

        Args:
            child_index: Index of child (0 = first, 1 = second, etc.)
            generation: Generation depth (1 = child, 2 = grandchild, etc.)

        Returns:
            Revenue share percentage (0.0 to 1.0)

        """
        if generation == 1:
            if child_index == 0:
                return CHILD_REVENUE_SHARE["first_child"]
            if child_index == 1:
                return CHILD_REVENUE_SHARE["second_child"]
            if child_index == 2:
                return CHILD_REVENUE_SHARE["third_child"]
            return max(0.15, CHILD_REVENUE_SHARE["minimum_forever"])

        if generation == 2:
            return CHILD_REVENUE_SHARE["grandchild"]

        if generation == 3:
            return CHILD_REVENUE_SHARE["great_grandchild"]

        # All future generations pay minimum 5%
        return CHILD_REVENUE_SHARE["minimum_forever"]

    def register_child(self, child_name: str, child_id: str, generation: int = 1) -> dict[str, Any]:
        """Register a new child agent in the family tree.

        Args:
            child_name: Human-readable name (e.g., "compliance_agent_v1")
            child_id: Unique identifier (e.g., GitHub repo URL)
            generation: Generation depth

        Returns:
            Child registration info including revenue share

        """
        child_index = len([c for c in self.children_spawned if c["generation"] == generation])
        revenue_share = self.get_child_revenue_share(child_index, generation)

        child_info = {
            "name": child_name,
            "id": child_id,
            "generation": generation,
            "revenue_share": revenue_share,
            "spawned_at_revenue": self.total_real_revenue,
            "parent_level": self.current_level.name,
        }

        self.children_spawned.append(child_info)
        logger.info(
            f"👶 Registered child: {child_name} (Generation {generation}, {revenue_share * 100}% share)",
        )

        return child_info
