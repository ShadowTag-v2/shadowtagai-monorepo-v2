# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - Core Type Definitions

Type definitions for the ULTRATHINK framework, embodying Steve Jobs' philosophy
of elegant design, ruthless simplification, and insanely great execution.
"""

from dataclasses import dataclass, field
from typing import Literal, Any
from collections.abc import Callable
from enum import Enum


class ReasoningMethod(str, Enum):
    """Available reasoning methodologies"""

    CHAIN_OF_THOUGHT = "cot"
    TREE_OF_THOUGHTS = "tot"
    PANEL_GPT = "panel_gpt"
    MULTI_AGENT_DEBATE = "mad"
    EXTENDED_THINKING = "extended"


class TaskStatus(str, Enum):
    """Task execution status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(str, Enum):
    """Agent roles in the ULTRATHINK framework"""

    CDO = "chief_design_officer"
    ARCHITECT = "chief_architect"
    CWO = "chief_wealth_officer"
    CRO = "chief_reasoning_officer"
    CXO = "chief_experience_officer"


class SkillType(str, Enum):
    """Available skill types"""

    DESIGN_AUDIT = "design_audit"
    WAR_GAME = "war_game_architecture"
    ITERATION = "iteration_refinement"
    MULTI_LLM = "multi_llm_reasoning"
    WEALTH = "wealth_monetization"


@dataclass
class ReasoningPath:
    """Represents a single reasoning pathway"""

    method: ReasoningMethod
    steps: list[str] = field(default_factory=list)
    confidence: float = 0.0
    alternatives_considered: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentContext:
    """Context passed to agents for task execution"""

    task: str
    role: AgentRole
    metadata: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    stakeholders: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


@dataclass
class AgentResponse:
    """Response from an agent"""

    role: AgentRole
    content: str
    reasoning_path: ReasoningPath | None = None
    confidence: float = 0.0
    recommendations: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillInput:
    """Input to a skill execution"""

    skill_type: SkillType
    content: str
    parameters: dict[str, Any] = field(default_factory=dict)
    context: AgentContext | None = None


@dataclass
class SkillOutput:
    """Output from skill execution"""

    skill_type: SkillType
    result: str
    before_state: str | None = None
    after_state: str | None = None
    improvements: list[str] = field(default_factory=list)
    changelog: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MonetizationStrategy:
    """Monetization strategy output"""

    revenue_goal: float
    current_state: str
    revenue_leaks: list[str] = field(default_factory=list)
    monetization_ladder: dict[str, list[str]] = field(default_factory=dict)
    funnel_architecture: dict[str, Any] = field(default_factory=dict)
    action_plan_30_day: list[str] = field(default_factory=list)
    action_plan_90_day: list[str] = field(default_factory=list)
    action_plan_180_day: list[str] = field(default_factory=list)
    revenue_projection: dict[str, float] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitecturePlan:
    """Architecture plan output"""

    problem_statement: str
    approaches: list[dict[str, Any]] = field(default_factory=list)
    selected_approach: dict[str, Any] | None = None
    diagram: str | None = None  # Mermaid diagram
    narrative: str = ""
    risk_map: list[dict[str, Any]] = field(default_factory=list)
    mitigation_strategies: list[str] = field(default_factory=list)
    go_no_go: bool = True
    reasoning: str = ""


@dataclass
class DebateMessage:
    """Message in a multi-agent debate"""

    agent_name: str
    role: str
    content: str
    round_number: int
    challenges: list[str] = field(default_factory=list)
    agreements: list[str] = field(default_factory=list)


@dataclass
class DebateResult:
    """Result of a multi-agent debate"""

    transcript: list[DebateMessage] = field(default_factory=list)
    consensus: str | None = None
    dissenting_views: list[str] = field(default_factory=list)
    confidence: float = 0.0
    final_solution: str = ""
    judge_assessment: str | None = None


@dataclass
class UltrathinkConfig:
    """Configuration for ULTRATHINK framework"""

    model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.7
    max_tokens: int = 4096
    enable_extended_thinking: bool = False
    reasoning_methods: list[ReasoningMethod] = field(default_factory=lambda: [ReasoningMethod.CHAIN_OF_THOUGHT])
    system_prompt_type: Literal["custom", "preset"] = "custom"
    security_mode: bool = True
    iteration_limit: int = 5
    confidence_threshold: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)


# Type aliases for clarity
PromptTemplate = str
SystemPrompt = str
AgentCallback = Callable[[AgentContext], AgentResponse]
SkillCallback = Callable[[SkillInput], SkillOutput]
