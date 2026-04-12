"""
Pnkln Orchestrator - Execution engine for ultrathink framework
Version: 1.0.0

Philosophy: Steve Jobs mode - beautiful, inevitable, ruthlessly simple
Design: KERNEL framework - Keep simple, Easy verify, Reproducible, Narrow, Explicit, Logical
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class RiskLevel(Enum):
    """ATP 5-19 risk stratification"""

    RA_1 = "Routine operations, minimal oversight"
    RA_2 = "Low impact, standard review"
    RA_3 = "Moderate impact, mission-critical, senior review recommended"
    RA_4 = "High impact, executive approval required"


class ReasoningFramework(Enum):
    """Available reasoning frameworks"""

    COT = "Chain of Thought"
    TOT = "Tree of Thoughts"
    RCR = "Reflect-Critique-Refine"
    MAD = "Multi-Agent Debate"
    DTE = "Debate-Train-Evolve"


@dataclass
class MonetizationMetrics:
    """Track financial impact of every execution"""

    time_saved_hours: float = 0.0
    revenue_identified_usd: float = 0.0
    revenue_generated_usd: float = 0.0

    @property
    def leverage_ratio(self) -> float:
        """Output/effort ratio"""
        if self.time_saved_hours == 0:
            return 0.0
        total_value = self.revenue_identified_usd + self.revenue_generated_usd
        return total_value / self.time_saved_hours


@dataclass
class AuditEntry:
    """Boy Scout Rule audit trail"""

    timestamp: datetime
    action: str
    skills_activated: list[str]
    before_state: str | None = None
    after_state: str | None = None
    improvements_made: list[str] = field(default_factory=list)
    metrics: MonetizationMetrics = field(default_factory=MonetizationMetrics)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "skills_activated": self.skills_activated,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "improvements_made": self.improvements_made,
            "metrics": {
                "time_saved_hours": self.metrics.time_saved_hours,
                "revenue_identified_usd": self.metrics.revenue_identified_usd,
                "revenue_generated_usd": self.metrics.revenue_generated_usd,
                "leverage_ratio": self.metrics.leverage_ratio,
            },
        }


@dataclass
class Skill:
    """Reusable capability"""

    id: str
    name: str
    category: str
    description: str
    triggers: list[str]
    frameworks: list[str]
    risk_level: str
    activation_prompt: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Skill":
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            description=data["description"],
            triggers=data["triggers"],
            frameworks=data["frameworks"],
            risk_level=data["risk_level"],
            activation_prompt=data["activation_prompt"],
        )


@dataclass
class Agent:
    """Persona with curated skills"""

    id: str
    name: str
    persona: str
    iq_baseline: int
    description: str
    skills: list[str]
    activation_triggers: list[str]
    system_prompt: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Agent":
        return cls(
            id=data["id"],
            name=data["name"],
            persona=data["persona"],
            iq_baseline=data["iq_baseline"],
            description=data["description"],
            skills=data["skills"],
            activation_triggers=data["activation_triggers"],
            system_prompt=data["system_prompt"],
        )


class PnklnOrchestrator:
    """
    Execution engine for pnkln ultrathink framework.

    Responsibilities:
    - Load and manage skills/agents registries
    - Auto-detect intent and route to appropriate skills
    - Execute skills with appropriate LLM backend
    - Maintain Boy Scout Rule audit trail
    - Track monetization metrics

    Design: Ruthlessly simple, obsessively detailed, beautifully inevitable
    """

    def __init__(
        self,
        skills_registry_path: str = "/mnt/project/skills/registry.yaml",
        agents_registry_path: str = "/mnt/project/agents/registry.yaml",
        audit_trail_path: str | None = None,
    ):
        self.skills_registry_path = Path(skills_registry_path)
        self.agents_registry_path = Path(agents_registry_path)
        self.audit_trail_path = Path(audit_trail_path) if audit_trail_path else None

        self.skills: dict[str, Skill] = {}
        self.agents: dict[str, Agent] = {}
        self.audit_trail: list[AuditEntry] = []

        self._load_registries()

    def _load_registries(self) -> None:
        """Load skills and agents from YAML registries"""
        # Load skills
        if self.skills_registry_path.exists():
            with open(self.skills_registry_path) as f:
                skills_data = yaml.safe_load(f)
                for skill_data in skills_data.get("skills", []):
                    skill = Skill.from_dict(skill_data)
                    self.skills[skill.id] = skill

        # Load agents
        if self.agents_registry_path.exists():
            with open(self.agents_registry_path) as f:
                agents_data = yaml.safe_load(f)
                for agent_data in agents_data.get("agents", []):
                    agent = Agent.from_dict(agent_data)
                    self.agents[agent.id] = agent

    def detect_skills(self, user_input: str) -> list[Skill]:
        """
        Auto-detect which skills to activate based on user input.

        Uses trigger keyword matching with Jobs-mode intelligence:
        - Question assumptions about keyword matching
        - Prefer multi-skill activation over single skill
        - Consider context, not just keywords
        """
        user_lower = user_input.lower()
        activated_skills = []

        for skill in self.skills.values():
            for trigger in skill.triggers:
                if trigger.lower() in user_lower:
                    activated_skills.append(skill)
                    break  # Don't double-activate on multiple triggers

        # If no skills match, this is a cue to ultrathink harder
        # Default to research_explorer for open-ended queries
        if not activated_skills and "research_explorer_v1" in self.skills:
            activated_skills.append(self.skills["research_explorer_v1"])

        return activated_skills

    def detect_agent(self, user_input: str) -> Agent | None:
        """
        Auto-detect which agent to use based on user input.

        Routing logic:
        - Design/architecture → ultrathink_designer
        - Revenue/business → wealth_accelerator
        - General → pnkln_orchestrator_meta
        """
        user_lower = user_input.lower()

        for agent in self.agents.values():
            for trigger in agent.activation_triggers:
                if trigger == "*":  # Meta-orchestrator catches all
                    continue
                if trigger.lower() in user_lower:
                    return agent

        # Fallback to meta-orchestrator
        return self.agents.get("pnkln_orchestrator_meta")

    async def execute_skill(
        self, skill: Skill, user_input: str, _llm_backend: Any | None = None
    ) -> str:
        """
        Execute a single skill.

        In production, this would integrate with Claude Agent SDK or similar.
        For now, returns the activation prompt (demonstrating the routing logic).
        """
        # TODO: Integrate with actual LLM backend
        # For now, return structured response showing what WOULD execute

        result = f"""
[SKILL ACTIVATED: {skill.name}]
Category: {skill.category}
Frameworks: {", ".join(skill.frameworks)}
Risk Level: {skill.risk_level}

User Input: {user_input}

Activation Prompt:
{skill.activation_prompt}

[This would execute against LLM backend in production]
"""
        return result

    async def execute(
        self,
        user_input: str,
        agent_id: str | None = None,
        _track_metrics: bool = True,
    ) -> dict[str, Any]:
        """
        Main execution method.

        Flow:
        1. Detect intent (skills/agent)
        2. Execute skills sequentially or in parallel
        3. Synthesize results
        4. Create audit entry
        5. Return structured response

        Design: Simple, verifiable, reproducible
        """
        start_time = datetime.now()

        # 1. Intent detection
        if agent_id:
            agent = self.agents.get(agent_id)
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            # Use agent's skills
            activated_skills = [self.skills[sid] for sid in agent.skills if sid in self.skills]
        else:
            agent = self.detect_agent(user_input)
            activated_skills = self.detect_skills(user_input)

        # 2. Execute skills
        skill_results = []
        for skill in activated_skills:
            result = await self.execute_skill(skill, user_input)
            skill_results.append({"skill_id": skill.id, "skill_name": skill.name, "result": result})

        # 3. Synthesize
        synthesis = self._synthesize_results(skill_results, user_input)

        # 4. Create audit entry
        execution_time = (datetime.now() - start_time).total_seconds()
        audit_entry = AuditEntry(
            timestamp=start_time,
            action=user_input,
            skills_activated=[s.id for s in activated_skills],
            before_state=None,  # TODO: Implement state tracking
            after_state=None,
            improvements_made=["Orchestration executed successfully"],
            metrics=MonetizationMetrics(
                time_saved_hours=execution_time / 3600,  # Convert to hours
                revenue_identified_usd=0.0,  # TODO: Extract from skill results
                revenue_generated_usd=0.0,
            ),
        )
        self.audit_trail.append(audit_entry)

        # 5. Return structured response
        return {
            "status": "success",
            "agent": agent.id if agent else None,
            "skills_activated": [s.id for s in activated_skills],
            "synthesis": synthesis,
            "audit": audit_entry.to_dict(),
            "execution_time_seconds": execution_time,
        }

    def _synthesize_results(self, skill_results: list[dict[str, Any]], user_input: str) -> str:
        """
        Synthesize multiple skill results into coherent response.

        Jobs mode: Make it feel inevitable, not assembled.
        """
        if not skill_results:
            return "No skills activated. Consider refining the request."

        synthesis = f"# Response to: {user_input}\n\n"

        for result in skill_results:
            synthesis += f"## {result['skill_name']}\n\n"
            synthesis += f"{result['result']}\n\n"

        return synthesis

    def get_audit_summary(self) -> dict[str, Any]:
        """
        Get Boy Scout Rule audit summary.

        Shows compound effect of all executions:
        - Total time saved
        - Total revenue identified/generated
        - Leverage ratio
        """
        total_time_saved = sum(e.metrics.time_saved_hours for e in self.audit_trail)
        total_revenue_identified = sum(e.metrics.revenue_identified_usd for e in self.audit_trail)
        total_revenue_generated = sum(e.metrics.revenue_generated_usd for e in self.audit_trail)

        return {
            "total_executions": len(self.audit_trail),
            "total_time_saved_hours": total_time_saved,
            "total_revenue_identified_usd": total_revenue_identified,
            "total_revenue_generated_usd": total_revenue_generated,
            "average_leverage_ratio": (
                (total_revenue_identified + total_revenue_generated) / total_time_saved
                if total_time_saved > 0
                else 0.0
            ),
            "executions": [e.to_dict() for e in self.audit_trail],
        }

    def __repr__(self) -> str:
        return (
            f"PnklnOrchestrator("
            f"skills={len(self.skills)}, "
            f"agents={len(self.agents)}, "
            f"executions={len(self.audit_trail)})"
        )


# Convenience factory
def create_orchestrator(
    skills_path: str | None = None, agents_path: str | None = None
) -> PnklnOrchestrator:
    """
    Create orchestrator with default or custom registry paths.

    Jobs mode: Make the common case trivial.
    """
    return PnklnOrchestrator(
        skills_registry_path=skills_path or "/mnt/project/skills/registry.yaml",
        agents_registry_path=agents_path or "/mnt/project/agents/registry.yaml",
    )


if __name__ == "__main__":
    # Self-test: Load registries and show what we've got
    orchestrator = create_orchestrator()
    print(orchestrator)
    print(f"\nSkills available: {list(orchestrator.skills.keys())}")
    print(f"Agents available: {list(orchestrator.agents.keys())}")

    # Demo intent detection
    test_inputs = [
        "Research edge AI compute market",
        "Design a beautiful API for authentication",
        "How can I monetize this open source project?",
    ]

    print("\n" + "=" * 60)
    print("INTENT DETECTION DEMO")
    print("=" * 60)

    for test_input in test_inputs:
        print(f"\nInput: {test_input}")
        skills = orchestrator.detect_skills(test_input)
        agent = orchestrator.detect_agent(test_input)
        print(f"Skills: {[s.name for s in skills]}")
        print(f"Agent: {agent.name if agent else 'None'}")
