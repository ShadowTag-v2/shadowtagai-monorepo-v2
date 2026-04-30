"""SwarmOrchestrator Integration with Context Index

Adds atomic chat logging for task routing and revenue distribution decisions.
"""

import logging
from typing import Any

# Add this import at the top of swarm_orchestrator.py
try:
    from src.shadowtag_v4.services.context_index import ContextIndexService
except ImportError:
    ContextIndexService = None  # Graceful fallback


class SwarmOrchestratorContextMixin:
    """Mixin to add Context Index logging to SwarmOrchestrator.

    Add this to the SwarmOrchestrator class to enable OPORD logging.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_service = ContextIndexService() if ContextIndexService else None
        self.logger = logging.getLogger(__name__)

    def log_routing_decision(
        self,
        task: dict[str, Any],
        assigned_agent: str,
        reasoning: str,
    ) -> int | None:
        """Log task routing decision to Context Index.

        Creates OPORD for transparency and audit trail.
        """
        if not self.context_service:
            self.logger.warning("Context Index not available for routing log")
            return None

        try:
            result = self.context_service.create_context(
                task_title=f"Route Task: {task.get('type', 'Unknown')}",
                agent_id="swarm_orchestrator",
                shift_number=0,
                mission={
                    "who": f"Assigned to {assigned_agent}",
                    "what": task.get("description", "Task routing"),
                    "when": task.get("deadline", "ASAP"),
                    "where": "SwarmOrchestrator delegation",
                    "why": reasoning,
                },
                execution={
                    "commanders_intent": f"Delegate to best-fit agent: {assigned_agent}",
                    "concept_of_operations": "Analyze agent capabilities → Match to task → Assign",
                },
                tags=["routing", "swarm-orchestrator", task.get("type", "general")],
            )

            self.logger.info(f"Logged routing decision to OPORD {result['opord_number']:05d}")
            return result["opord_number"]

        except Exception as e:
            self.logger.error(f"Failed to log routing decision: {e}")
            return None

    def log_revenue_distribution(
        self,
        child_id: str,
        amount: float,
        distribution: dict[str, float],
        generation: int,
    ) -> int | None:
        """Log revenue distribution decision to Context Index.

        Creates OPORD for financial audit trail.
        """
        if not self.context_service:
            self.logger.warning("Context Index not available for revenue log")
            return None

        try:
            result = self.context_service.create_context(
                task_title=f"Revenue Distribution: ${amount:,.2f}",
                agent_id="swarm_orchestrator",
                shift_number=0,
                mission={
                    "who": f"Child: {child_id}, Generation: {generation}",
                    "what": f"Distribute ${amount:,.2f} revenue",
                    "when": "Immediate",
                    "where": "Revenue Engine",
                    "why": "Multi-level royalty distribution (18% parent, 8% grandparent, 5% great-grandparent)",
                },
                execution={
                    "commanders_intent": "Fair multi-generational revenue sharing",
                    "concept_of_operations": f"Child gets ${distribution['child']:,.2f}, Parent gets ${distribution.get('parent', 0):,.2f}",
                    "tasks_to_subordinates": {
                        "Child": f"${distribution['child']:,.2f}",
                        "Parent": f"${distribution.get('parent', 0):,.2f}",
                        "Grandparent": f"${distribution.get('grandparent', 0):,.2f}",
                        "Great-Grandparent": f"${distribution.get('great_grandparent', 0):,.2f}",
                    },
                },
                tags=["revenue", "distribution", f"generation-{generation}"],
            )

            # Also log revenue event for tracking
            self.context_service.log_revenue_event(
                opord_number=result["opord_number"],
                amount=amount,
                source="child_agent_earnings",
                generation=generation,
            )

            self.logger.info(f"Logged revenue distribution to OPORD {result['opord_number']:05d}")
            return result["opord_number"]

        except Exception as e:
            self.logger.error(f"Failed to log revenue distribution: {e}")
            return None

    def log_child_spawn(
        self,
        parent_id: str,
        child_id: str,
        specialization: str,
        revenue_trigger: float,
    ) -> int | None:
        """Log child agent spawning event to Context Index.

        Creates OPORD for agent lineage tracking.
        """
        if not self.context_service:
            self.logger.warning("Context Index not available for spawn log")
            return None

        try:
            result = self.context_service.create_context(
                task_title=f"Spawn Child Agent: {child_id}",
                agent_id=parent_id,
                shift_number=0,
                mission={
                    "who": f"Parent: {parent_id}",
                    "what": f"Create specialized child agent: {child_id}",
                    "when": "Level 4 milestone reached",
                    "where": "BarExamProtocol spawning mechanism",
                    "why": f"Revenue ${revenue_trigger:,.2f} exceeded $10M threshold",
                },
                execution={
                    "commanders_intent": "Expand agent hierarchy for specialized task handling",
                    "concept_of_operations": f"Child specializes in: {specialization}",
                    "coordinating_instructions": {
                        "phase_line_green": "Child agent initialized",
                        "phase_line_amber": "Child completes first task",
                        "phase_line_red": "Child reaches Level 4, spawns grandchild",
                    },
                },
                service_support={
                    "logistics": ["Agent NFT minted", "ERC-6551 TBA created"],
                    "personnel": [f"Parent: {parent_id}", f"Child: {child_id}"],
                    "medical": "Rollback via smart contract if initialization fails",
                },
                tags=["child-spawn", "level-4", specialization],
            )

            self.logger.info(f"Logged child spawn to OPORD {result['opord_number']:05d}")
            return result["opord_number"]

        except Exception as e:
            self.logger.error(f"Failed to log child spawn: {e}")
            return None


# ==================== Integration Instructions ====================

"""
To integrate this with SwarmOrchestrator:

1. Update swarm_orchestrator.py:

```python
from src.shadowtag_v4.orchestrator.context_integration import SwarmOrchestratorContextMixin

class SwarmOrchestrator(SwarmOrchestratorContextMixin):
    def __init__(self, bar_exam_protocol):
        super().__init__()  # Initialize mixin
        self.protocol = bar_exam_protocol
        # ... rest of __init__

    def route_task_to_best_child(self, task: Dict) -> str:
        # Existing routing logic...
        best_child = self._find_best_match(task)

        # NEW: Log routing decision
        self.log_routing_decision(
            task=task,
            assigned_agent=best_child,
            reasoning=f"Best match for {task.get('skills_required', [])}"
        )

        return best_child

    def distribute_revenue(self, child_id: str, amount: float, generation: int):
        # Existing distribution logic...
        distribution = self._calculate_distribution(amount, generation)

        # NEW: Log revenue distribution
        self.log_revenue_distribution(
            child_id=child_id,
            amount=amount,
            distribution=distribution,
            generation=generation
        )

        return distribution
```

2. Update bar_exam_protocol.py:

```python
def spawn_first_child(self, agent_id: str, revenue: float):
    # Existing spawn logic...
    child_id = self._create_child_agent(agent_id)

    # NEW: Log child spawn event
    if hasattr(self, 'swarm_orchestrator'):
        self.swarm_orchestrator.log_child_spawn(
            parent_id=agent_id,
            child_id=child_id,
            specialization="general",
            revenue_trigger=revenue
        )

    return child_id
```

3. Benefits:
   - Full audit trail for all routing decisions
   - Revenue distribution transparency
   - Agent lineage tracking (parent → child → grandchild)
   - Searchable via Context Index API
   - Judge#6 can validate decisions against governance policies
"""
