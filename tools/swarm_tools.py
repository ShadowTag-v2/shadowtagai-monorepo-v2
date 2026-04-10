"""
Swarm Management Tools.
Allows the agent to control and monitor the AgentOrchestrator swarm.
"""
from typing import Any

from pnkln.agents import CorAutoresearch

# Singleton instance for the tools to control
# In a real app, this would be managed by a dependency injection container
_SWARM = CorAutoresearch()


def start_swarm() -> str:
    """
    Activates the Flying n-autoresearch/Kosmos/BioAgents agent swarm.
    """
    if _SWARM.running:
        return "Swarm is already running."

    _SWARM.start()
    return "AgentOrchestrator Swarm activated."


def stop_swarm() -> str:
    """
    Stops the Flying n-autoresearch/Kosmos/BioAgents agent swarm.
    """
    if not _SWARM.running:
        return "Swarm is not running."

    _SWARM.stop()
    return "AgentOrchestrator Swarm stopped."


def get_swarm_status() -> dict[str, Any]:
    """
    Retrieves the current status and governance metrics of the swarm.
    """
    return _SWARM.get_governance_status()


def get_active_agents() -> list[str]:
    """
    Returns a list of active agent roles in the swarm.
    """
    return [unit.role for unit in _SWARM.units]


def swarm_vote(decision: str, risk_level: str = "M", brakes: int = 0) -> dict[str, Any]:
    """
    Execute a governance vote through the swarm.

    Args:
        decision: The decision to vote on
        risk_level: ATP 5-19 risk level (L, M, H, EH)
        brakes: Number of brakes/concerns

    Returns:
        Vote result with decision, confidence, and method
    """
    from agents.autoresearch2 import execute_internal_swarm  # noqa: PLC0415

    result = execute_internal_swarm(
        intent=decision,
        risk_level=risk_level,
        brake_count=brakes
    )

    return {
        "decision": result.decision,
        "confidence": result.confidence,
        "method": result.method,
        "votes": {
            "strategy": result.strategy_votes,
            "execution": result.execution_votes,
            "worker": result.worker_votes
        }
    }


def swarm_research(topic: str) -> dict[str, Any]:
    """
    Execute a research query through the swarm.

    Args:
        topic: The research topic or question

    Returns:
        Research findings with confidence scores
    """
    # Research mode uses the swarm's internal reasoning
    # This is a placeholder - actual implementation runs inside the LLM
    return {
        "topic": topic,
        "status": "Research mode requires LLM execution",
        "instruction": "Use SWARM RESEARCH: [topic] in Claude/Gemini with AgentOrchestrator prompt loaded"
    }
