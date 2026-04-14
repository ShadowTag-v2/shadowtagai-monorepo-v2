"""METT-TC Context Builder for minion
==========================================
Mission, Enemy, Terrain, Troops, Time, Civilian considerations.
Dynamic context injection for Antigravity prompts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class METTTCContext:
    """METT-TC tactical context for mission planning.

    Mission  - Task and purpose
    Enemy    - Threats, blockers, constraints
    Terrain  - Codebase structure, files, dependencies
    Troops   - Available agents and capabilities
    Time     - Deadlines, timeouts, token budgets
    Civilian - Compliance, user data, external dependencies
    """

    # Mission
    mission_type: str = ""
    mission_statement: str = ""
    commander_intent: str = ""
    end_state: str = ""

    # Enemy (Blockers/Threats)
    blockers: list[str] = field(default_factory=list)
    rate_limits: dict[str, Any] = field(default_factory=dict)
    complexity_factors: list[str] = field(default_factory=list)
    known_issues: list[str] = field(default_factory=list)

    # Terrain (Codebase)
    target_files: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    api_endpoints: list[str] = field(default_factory=list)
    codebase_summary: str = ""

    # Troops (Available Forces)
    available_agents: int = 600
    available_vehicles: int = 134
    troop_allocation: dict[str, int] = field(default_factory=dict)
    model_distribution: dict[str, str] = field(default_factory=dict)

    # Time
    timeout_seconds: int = 300
    token_budget: int = 100000
    deadline: datetime | None = None
    priority: str = "normal"  # critical, high, normal, low

    # Civilian (Compliance/External)
    compliance_requirements: list[str] = field(default_factory=list)
    user_data_involved: bool = False
    external_apis: list[str] = field(default_factory=list)
    jura_gates: list[str] = field(default_factory=list)

    def to_prompt_context(self) -> dict[str, str]:
        """Convert to format suitable for prompt injection"""
        return {
            "mission_type": self.mission_type,
            "mission_statement": self.mission_statement,
            "blockers": self._format_list(self.blockers) or "None identified",
            "codebase_context": self._format_terrain(),
            "available_agents": str(self.available_agents),
            "timeout": str(self.timeout_seconds),
            "token_budget": str(self.token_budget),
            "compliance_requirements": self._format_list(self.compliance_requirements)
            or "Standard JURA gates",
        }

    def _format_list(self, items: list[str]) -> str:
        """Format list for prompt"""
        if not items:
            return ""
        return ", ".join(items)

    def _format_terrain(self) -> str:
        """Format terrain/codebase info"""
        parts = []
        if self.target_files:
            parts.append(f"Files: {', '.join(self.target_files[:5])}")
        if self.dependencies:
            parts.append(f"Deps: {', '.join(self.dependencies[:5])}")
        if self.codebase_summary:
            parts.append(self.codebase_summary)
        return " | ".join(parts) if parts else "Standard codebase"


class METTTCBuilder:
    """Builder for constructing METT-TC context from various sources.
    """

    def __init__(self):
        self.context = METTTCContext()

    def with_mission(
        self, mission_type: str, statement: str, intent: str = "", end_state: str = "",
    ) -> "METTTCBuilder":
        """Set mission parameters"""
        self.context.mission_type = mission_type
        self.context.mission_statement = statement
        self.context.commander_intent = intent
        self.context.end_state = end_state
        return self

    def with_blockers(self, *blockers: str) -> "METTTCBuilder":
        """Add enemy/blocker elements"""
        self.context.blockers.extend(blockers)
        return self

    def with_rate_limits(self, limits: dict[str, Any]) -> "METTTCBuilder":
        """Add rate limit information"""
        self.context.rate_limits = limits
        return self

    def with_terrain(
        self, files: list[str] = None, dependencies: list[str] = None, summary: str = "",
    ) -> "METTTCBuilder":
        """Set terrain/codebase context"""
        if files:
            self.context.target_files = files
        if dependencies:
            self.context.dependencies = dependencies
        if summary:
            self.context.codebase_summary = summary
        return self

    def with_troops(
        self, agents: int = 600, vehicles: int = 134, allocation: dict[str, int] = None,
    ) -> "METTTCBuilder":
        """Set available forces"""
        self.context.available_agents = agents
        self.context.available_vehicles = vehicles
        if allocation:
            self.context.troop_allocation = allocation
        return self

    def with_time(
        self, timeout: int = 300, token_budget: int = 100000, priority: str = "normal",
    ) -> "METTTCBuilder":
        """Set time constraints"""
        self.context.timeout_seconds = timeout
        self.context.token_budget = token_budget
        self.context.priority = priority
        return self

    def with_compliance(
        self, requirements: list[str] = None, user_data: bool = False, jura_gates: list[str] = None,
    ) -> "METTTCBuilder":
        """Set civilian/compliance considerations"""
        if requirements:
            self.context.compliance_requirements = requirements
        self.context.user_data_involved = user_data
        if jura_gates:
            self.context.jura_gates = jura_gates
        else:
            # Default JURA gates
            self.context.jura_gates = [
                "legal",
                "regulatory",
                "financial",
                "reputational",
                "security",
            ]
        return self

    def build(self) -> METTTCContext:
        """Build and return the context"""
        return self.context


def build_mett_tc_from_opord(opord: Any) -> METTTCContext:
    """Build METT-TC context from an OPORD.

    Args:
        opord: OPORD object from opord_generator

    Returns:
        METTTCContext populated from OPORD

    """
    builder = METTTCBuilder()

    # Extract mission from OPORD
    builder.with_mission(
        mission_type=getattr(opord, "mission_type", "attack"),
        statement=getattr(opord, "mission", ""),
        intent=getattr(opord.execution, "commander_intent", "")
        if hasattr(opord, "execution")
        else "",
    )

    # Extract blockers from situation
    if hasattr(opord, "situation"):
        situation = opord.situation
        if hasattr(situation, "enemy"):
            blockers = situation.enemy.get("blockers", [])
            builder.with_blockers(*blockers)

    # Extract time from service support
    if hasattr(opord, "service_support"):
        ss = opord.service_support
        builder.with_time(
            timeout=getattr(ss, "time_limit_seconds", 300),
            token_budget=getattr(ss, "token_limit", 100000),
        )

    # Default compliance gates
    builder.with_compliance(
        jura_gates=[
            "legal",
            "regulatory",
            "financial",
            "security",
        ],
    )

    return builder.build()


def build_mett_tc_from_task(
    task: str, mission_type: str, context: dict[str, Any] = None,
) -> METTTCContext:
    """Build METT-TC context from a task description.

    Args:
        task: User's task description
        mission_type: Classified mission type
        context: Additional context dict

    Returns:
        METTTCContext for the task

    """
    context = context or {}

    builder = METTTCBuilder()

    builder.with_mission(
        mission_type=mission_type,
        statement=task,
    )

    # Extract blockers from context
    blockers = context.get("blockers", [])
    if blockers:
        builder.with_blockers(*blockers)

    # Extract terrain from context
    builder.with_terrain(
        files=context.get("files", []),
        dependencies=context.get("dependencies", []),
        summary=context.get("codebase_summary", ""),
    )

    # Set time constraints
    builder.with_time(
        timeout=context.get("timeout", 300),
        token_budget=context.get("token_budget", 100000),
        priority=context.get("priority", "normal"),
    )

    # Set compliance
    builder.with_compliance(
        user_data=context.get("user_data_involved", False),
    )

    return builder.build()
