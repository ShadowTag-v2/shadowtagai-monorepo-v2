# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Context Index Service - CRUD Operations for OPORD Contexts

Provides service layer for creating, reading, updating, and deleting
OPORD contexts with Elasticsearch integration for full-text search.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from agents.atomic_chat_manager import AtomicChatManager

logger = logging.getLogger(__name__)


class ContextIndexService:
    """Service layer for Context Index operations.

    Wraps AtomicChatManager with business logic for:
    - OPORD creation with validation
    - Search and retrieval
    - Revenue tracking integration
    - Judge#6 decision logging
    """

    def __init__(self, db_path: str = "data/context_index.db"):
        self.chat_manager = AtomicChatManager(db_path=db_path)

    def create_context(
        self,
        task_title: str,
        agent_id: str,
        shift_number: int,
        mission: dict[str, str],
        situation: dict[str, str] | None = None,
        execution: dict[str, Any] | None = None,
        service_support: dict[str, Any] | None = None,
        command_signal: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create new OPORD context with validation.

        Returns:
            Dict with opord_number, created_at, status

        """
        # Validation
        required_mission_keys = ["who", "what", "when", "where", "why"]
        missing_keys = [k for k in required_mission_keys if k not in mission]
        if missing_keys:
            raise ValueError(f"Mission missing required keys: {missing_keys}")

        # Create OPORD
        opord_num = self.chat_manager.create_opord(
            task_title=task_title,
            agent_id=agent_id,
            shift_number=shift_number,
            mission=mission,
            situation=situation,
            execution=execution,
            service_support=service_support,
            command_signal=command_signal,
            tags=tags,
        )

        logger.info(f"Created context OPORD {opord_num:05d} for agent {agent_id}")

        return {
            "opord_number": opord_num,
            "task_title": task_title,
            "agent_id": agent_id,
            "shift_number": shift_number,
            "created_at": datetime.now(UTC).isoformat(),
            "status": "active",
        }

    def get_context(self, opord_number: int) -> dict | None:
        """Get single OPORD context by number."""
        results = self.chat_manager.search_opords(query=None)
        for opord in results:
            if opord.get("opord_number") == opord_number:
                return opord
        return None

    def update_context(
        self,
        opord_number: int,
        summary: str | None = None,
        decisions: list[str] | None = None,
        status: str | None = None,
    ) -> bool:
        """Update OPORD context with summary and decisions.

        Args:
            opord_number: OPORD to update
            summary: Task summary
            decisions: List of key decisions made
            status: New status (active, completed, archived)

        """
        if summary or decisions:
            success = self.chat_manager.complete_opord(
                opord_number=opord_number,
                summary=summary or "",
                decisions=decisions or [],
            )
            logger.info(f"Updated OPORD {opord_number:05d} with summary")
            return success

        # TODO: Add status update to AtomicChatManager
        return True

    def search_contexts(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        agent_id: str | None = None,
        shift_number: int | None = None,
        status: str | None = None,
        date_range: tuple | None = None,
    ) -> list[dict]:
        """Search OPORD contexts with filters.

        Full-text search via query, structured filters via other params.
        """
        results = self.chat_manager.search_opords(
            query=query,
            tags=tags,
            agent_id=agent_id,
            date_range=date_range,
        )

        # Additional filters
        if shift_number is not None:
            results = [r for r in results if r.get("shift_number") == shift_number]

        if status:
            results = [r for r in results if r.get("status") == status]

        logger.info(f"Search returned {len(results)} contexts")
        return results

    def get_agent_history(self, agent_id: str, limit: int = 100) -> list[dict]:
        """Get all contexts for a specific agent."""
        return self.chat_manager.search_opords(agent_id=agent_id)[:limit]

    def get_shift_contexts(self, shift_number: int, status: str = "active") -> list[dict]:
        """Get all contexts for a specific shift."""
        return self.chat_manager.get_shift_opords(shift_number=shift_number, status=status)

    def clear_shift_memory(self, shift_number: int) -> int:
        """Archive completed contexts for shift rotation."""
        return self.chat_manager.clear_shift_memory(shift_number)

    def acknowledge_context(self, opord_number: int, agent_id: str) -> bool:
        """Agent acknowledges receipt of OPORD."""
        return self.chat_manager.acknowledge_opord(opord_number, agent_id)

    def log_revenue_event(
        self,
        opord_number: int,
        amount: float,
        source: str,
        generation: int,
    ) -> dict:
        """Log revenue event to context for audit trail.

        Integrates with revenue_engine for transaction tracking.
        """
        # Get existing context
        context = self.get_context(opord_number)
        if not context:
            raise ValueError(f"OPORD {opord_number} not found")

        # Create revenue log entry
        revenue_log = {
            "opord_number": opord_number,
            "amount": amount,
            "source": source,
            "generation": generation,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # TODO: Integrate with revenue_engine
        logger.info(f"Logged revenue ${amount:,.2f} to OPORD {opord_number:05d}")

        return revenue_log

    def log_Cor.Claude_Code_6_decision(
        self,
        opord_number: int,
        policy_violated: str,
        severity: str,
        action_taken: str,
        reasoning: str,
    ) -> dict:
        """Log Judge#6 governance decision to context.

        Creates audit trail for compliance.
        """
        decision_log = {
            "opord_number": opord_number,
            "policy_violated": policy_violated,
            "severity": severity,
            "action_taken": action_taken,
            "reasoning": reasoning,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # TODO: Push to Elasticsearch Cor.Claude_Code_6_decisions index
        logger.warning(
            f"Judge#6 decision logged for OPORD {opord_number:05d}: "
            f"{severity} violation of {policy_violated}",
        )

        return decision_log
