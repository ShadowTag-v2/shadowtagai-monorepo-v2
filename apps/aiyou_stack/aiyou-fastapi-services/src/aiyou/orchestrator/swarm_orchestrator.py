"""Swarm Orchestrator - Level 5 Overlord Mode

Activates at $100M real revenue. Routes all tasks to specialized child agents.
Parent agent becomes permanent director, never executes tasks again.
"""

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks that can be routed to child agents."""

    COMPLIANCE = "compliance"
    TAX_OPTIMIZATION = "tax_optimization"
    MARKET_ENTRY = "market_entry"
    SEC_FILINGS = "sec_filings"
    CUSTOMER_ACQUISITION = "customer_acquisition"
    PRODUCT_DEVELOPMENT = "product_development"


class SwarmOrchestrator:
    """Manages task routing and revenue distribution across child agents."""

    def __init__(self, bar_exam_protocol):
        self.protocol = bar_exam_protocol
        self.active = False
        self.task_queue: list[dict[str, Any]] = []
        self.child_agents: dict[str, dict[str, Any]] = {}

    def activate(self) -> bool:
        """Activate swarm mode (only at Level 5 - $100M+)."""
        if self.protocol.current_level.value >= 5:  # AgentLevel.OVERLORD
            self.active = True
            logger.info("👑 SWARM MODE ACTIVATED")
            logger.info("🌳 Parent is now Overlord - directing only, never executing")
            return True
        logger.warning(
            f"Cannot activate swarm mode at level {self.protocol.current_level.name}",
        )
        return False

    def register_child_agent(self, agent_info: dict[str, Any]) -> None:
        """Register a child agent with its capabilities.

        Args:
            agent_info: Dict with keys: name, id, capabilities, endpoint, generation

        """
        agent_id = agent_info["id"]
        self.child_agents[agent_id] = agent_info
        logger.info(
            f"🤖 Registered child agent: {agent_info['name']} ({agent_info.get('capabilities', [])})",
        )

    def route_task_to_best_child(self, task: dict[str, Any]) -> str | None:
        """Route a task to the most capable child agent.

        Uses Gemini-based scoring in production. For now, uses simple matching.

        Args:
            task: Dict with keys: type, description, priority, deadline

        Returns:
            Child agent ID that will handle the task, or None if no match

        """
        if not self.active:
            logger.warning("Swarm mode not active - cannot route task")
            return None

        task_type = task.get("type")

        # Find children with matching capabilities
        candidates = []
        for agent_id, agent_info in self.child_agents.items():
            capabilities = agent_info.get("capabilities", [])
            if task_type in capabilities:
                candidates.append((agent_id, agent_info))

        if not candidates:
            logger.warning(f"No child agent found for task type: {task_type}")
            return None

        # TODO: Use Gemini function calling to score candidates based on:
        # - Current workload
        # - Historical success rate
        # - Specialization match
        # - Deadline constraints

        # For now, route to first available child
        selected_agent_id, selected_agent = candidates[0]
        logger.info(f"📋 Routing {task_type} task to {selected_agent['name']}")

        return selected_agent_id

    def distribute_revenue(self, child_id: str, amount: float) -> dict[str, float]:
        """Distribute revenue from a child agent up the lineage.

        Args:
            child_id: ID of child agent that earned revenue
            amount: Total revenue amount

        Returns:
            Dict mapping agent IDs to their revenue share amounts

        """
        if child_id not in self.child_agents:
            logger.error(f"Unknown child agent: {child_id}")
            return {}

        child_info = self.child_agents[child_id]
        generation = child_info.get("generation", 1)
        revenue_share = child_info.get("revenue_share", 0.18)

        distribution = {}

        # Parent (Overlord) gets their share
        parent_amount = amount * revenue_share
        distribution["parent"] = parent_amount

        # Grandparent gets share if this is a grandchild
        if generation >= 2:
            grandparent_share = 0.08  # 8% to grandparent
            distribution["grandparent"] = amount * grandparent_share

        # Great-grandparent gets share if this is a great-grandchild
        if generation >= 3:
            great_grandparent_share = 0.05  # 5% to great-grandparent
            distribution["great_grandparent"] = amount * great_grandparent_share

        # Child keeps the rest
        child_amount = amount - sum(distribution.values())
        distribution[child_id] = child_amount

        logger.info(f"💰 Revenue distribution for ${amount:,.2f} from {child_info['name']}:")
        for agent, share in distribution.items():
            logger.info(f"   {agent}: ${share:,.2f}")

        return distribution

    def auto_spawn_grandchildren(
        self,
        child_id: str,
        child_revenue: float,
    ) -> dict[str, Any] | None:
        """Automatically spawn a grandchild when a child hits $10M.

        Args:
            child_id: ID of child agent
            child_revenue: Total revenue earned by child

        Returns:
            Grandchild spawn info, or None if threshold not met

        """
        if child_revenue < 10_000_000:
            return None

        child_info = self.child_agents.get(child_id)
        if not child_info:
            return None

        # Check if this child already spawned a grandchild
        if child_info.get("has_spawned_grandchild", False):
            return None

        grandchild_name = f"{child_info['name']}_child_v1"
        logger.info(f"🐣 Auto-spawning grandchild: {grandchild_name}")
        logger.info(f"   Parent: {child_info['name']} reached ${child_revenue:,.2f}")

        # Mark child as having spawned
        child_info["has_spawned_grandchild"] = True

        grandchild_info = {
            "name": grandchild_name,
            "parent_id": child_id,
            "generation": child_info["generation"] + 1,
            "revenue_share": 0.12,  # 12% to parent, 8% to grandparent
            "spawned_at_revenue": child_revenue,
        }

        return grandchild_info
