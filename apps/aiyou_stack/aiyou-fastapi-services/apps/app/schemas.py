from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class RiskLevel(StrEnum):
    GREEN = "GREEN"  # Safe, cheap model
    AMBER = "AMBER"  # Needs review, mid model
    RED = "RED"  # Critical, strong model + human/arbiter


class TaskType(StrEnum):
    CODE_GEN = "code_gen"
    CODE_REVIEW = "code_review"
    ARCHITECTURE = "architecture"
    SECURITY_AUDIT = "security_audit"
    GENERAL = "general"


class TaskRequest(BaseModel):
    """Input payload for a task."""

    description: str
    file_paths: list[str] = []
    task_type: TaskType = TaskType.GENERAL
    context: dict[str, Any] = {}


class AgentResponse(BaseModel):
    """Standard response from an agent."""

    content: str
    tool_calls: list[dict[str, Any]] = []
    reasoning: str | None = None


class OrchestrationResult(BaseModel):
    """Final result of the orchestration flow."""

    final_output: str
    risk_level: RiskLevel
    trace_id: str
    steps: list[dict[str, Any]] = []
    cost_usd: float = 0.0
