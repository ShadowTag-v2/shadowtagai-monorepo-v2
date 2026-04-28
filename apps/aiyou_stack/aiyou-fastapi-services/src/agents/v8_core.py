# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ============================================================================
# Core Types (V8)
# ============================================================================


class RiskLevel(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    NUCLEAR = 5

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


@dataclass
class Provenance:
    source: str
    method: str
    timestamp: float


@dataclass
class Finding:
    content: str
    provenance: Provenance
    tags: list[str]


@dataclass
class Hypothesis:
    statement: str
    confidence: float
    supporting_findings: list[Finding]


@dataclass
class Task:
    agent_type: str
    description: str
    context_slice: Any | None = None
    priority: int = 1


@dataclass
class GovernanceVerdict:
    approved: bool
    risk_level: RiskLevel
    modifications: list[str]
    required_brakes: list[str]


@dataclass
class ToolDef:
    name: str
    description: str
    func: Any  # Callable
    schema: dict[str, Any]
    risk_level: RiskLevel


@dataclass
class ToolRegistry:
    tools: dict[str, ToolDef] = field(default_factory=dict)

    def register(self, tool_def: ToolDef):
        self.tools[tool_def.name] = tool_def

    def get(self, name: str) -> ToolDef | None:
        return self.tools.get(name)


@dataclass
class TokenLedger:
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost: float = 0.0

    def add(self, input_k: int, output_k: int):
        self.input_tokens += input_k
        self.output_tokens += output_k
        # Estimated cost: $3.50/1M input, $10.50/1M output (Pro)
        self.total_cost += (input_k / 1_000_000 * 3.50) + (output_k / 1_000_000 * 10.50)


class JudgeSixGovernance:
    """Mock Governance Engine for V8."""

    def validate(self, _thought_trace: str, proposed_action: str) -> GovernanceVerdict:
        risk = RiskLevel.LOW
        brakes = []

        if "destroy" in proposed_action.lower() or "delete" in proposed_action.lower():
            risk = RiskLevel.HIGH
            brakes.append("require_human_confirmation")

        return GovernanceVerdict(
            approved=risk != RiskLevel.NUCLEAR,
            risk_level=risk,
            modifications=[],
            required_brakes=brakes,
        )


# ============================================================================
# Agent Abstractions
# ============================================================================


class KosmosREPL:
    """Simulated REPL environment for tool execution."""

    def __init__(self):
        self.local_scope: dict[str, Any] = {}
        self.output_buffer = []
        self.history_file = ".kosmos_history"

    def load_context(self, name: str, content: Any):
        self.local_scope[name] = content

    def _log_history(self, code: str):
        with open(self.history_file, "a") as f:
            timestamp = datetime.now().isoformat()
            f.write(f"[{timestamp}] {code}\n")

    def execute(self, code: str) -> str:
        self._log_history(code)
        try:
            exec(code, {"__builtins__": __builtins__}, self.local_scope)
            return "Executed."
        except Exception as e:
            return f"Error: {e}"


@dataclass
class AgentUnit(ABC):
    """Abstract Base for Kosmos Agents"""

    id: str
    role: str
    status: str
    brain: Any = None

    @abstractmethod
    def execute_task(self, task: Task, repl: KosmosREPL | None = None) -> Finding:
        pass
