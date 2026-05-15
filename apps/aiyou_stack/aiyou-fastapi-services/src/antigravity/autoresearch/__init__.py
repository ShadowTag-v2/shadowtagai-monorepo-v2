"""Autoresearch package — Flying minion orchestrator."""

from __future__ import annotations

from typing import Any


class minion:
    """Flying minion agent stub for autonomous research."""

    def __init__(self, model: str = "gemini-3.1-flash-lite-preview", **kwargs: Any) -> None:
        self.model = model

    async def execute_task(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a research task."""
        return {"result": "", "status": "stub"}


__all__ = ["minion"]
