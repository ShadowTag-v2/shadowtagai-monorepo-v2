"""Agent implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.agents.base import Agent, AgentConfig, AgentPerformance


# ---------------------------------------------------------------------------
# Lightweight debate stubs — real logic lives in main_ecosystem or a
# dedicated module.  These exist so that ``from app.agents import
# DebateAgent, DebateOrchestrator`` works at import-time without pulling
# heavy ML dependencies.
# ---------------------------------------------------------------------------


class DebateAgent:
    """Single agent participating in a multi-agent debate."""

    def __init__(
        self, agent_id: str = "default", model: str = "gemini-2.5-flash", **kw: Any
    ) -> None:
        self.agent_id = agent_id
        self.model = model

    async def respond(self, context: str) -> str:  # pragma: no cover
        return f"[{self.agent_id}] stub response"


class DebateOrchestrator:
    """Orchestrates a multi-agent debate (PanelGPT / MAD)."""

    def __init__(self, agents: list[DebateAgent] | None = None, **kw: Any) -> None:
        self.agents = agents or []

    async def run(self, question: str, max_rounds: int = 3) -> dict[str, Any]:  # pragma: no cover
        return {"question": question, "rounds": max_rounds, "result": "stub"}


def __getattr__(name: str):
    """Lazy re-exports to avoid eager import of heavy dependencies."""
    if name in {"Agent", "AgentConfig", "AgentPerformance"}:
        from app.agents.base import Agent, AgentConfig, AgentPerformance

        _map = {
            "Agent": Agent,
            "AgentConfig": AgentConfig,
            "AgentPerformance": AgentPerformance,
        }
        return _map[name]
    raise AttributeError(f"module 'app.agents' has no attribute {name!r}")


__all__ = [
    "Agent",
    "AgentConfig",
    "AgentPerformance",
    "DebateAgent",
    "DebateOrchestrator",
]
