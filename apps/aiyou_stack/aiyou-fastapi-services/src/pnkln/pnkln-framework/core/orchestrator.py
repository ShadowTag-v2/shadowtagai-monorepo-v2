#!/usr/bin/env python3
"""═══════════════════════════════════════════════════════════════════════════════
PNKLN ORCHESTRATOR
Production-grade AI orchestration with auto-activation and execution

"Simplicity is the ultimate sophistication." — Steve Jobs
═══════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path("/mnt/project")
SKILLS_REGISTRY = PROJECT_ROOT / "skills" / "registry.yaml"
AGENTS_REGISTRY = PROJECT_ROOT / "agents" / "registry.yaml"
AUDIT_LOG_DIR = PROJECT_ROOT / "audit"

# Blake3 → WASM → SHA256 fallback for hashing
HASH_ALGORITHM = "sha256"  # Fallback for now (blake3 requires native/wasm)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


class RiskLevel(Enum):
    """ATP 5-19 Risk Stratification"""

    RA_1 = "RA-1"  # Routine
    RA_2 = "RA-2"  # Low impact
    RA_3 = "RA-3"  # Moderate (mission-critical starts here)
    RA_4 = "RA-4"  # High (requires senior review)


class ReasoningMethod(Enum):
    """Reasoning frameworks for agent execution"""

    COT = "CoT"  # Chain of Thought (linear)
    TOT = "ToT"  # Tree of Thoughts (branching)
    RCR = "RCR"  # Reflect-Critique-Refine (self-correction)
    MAD = "MAD"  # Multi-Agent Debate (adversarial consensus)
    DTE = "DTE"  # Debate-Train-Evolve (policy improvement)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Metrics:
    """Monetization tracking for every skill/agent execution"""

    time_saved_hours: float = 0.0
    revenue_identified_usd: float = 0.0
    revenue_generated_usd: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "time_saved_hours": self.time_saved_hours,
            "revenue_identified_usd": self.revenue_identified_usd,
            "revenue_generated_usd": self.revenue_generated_usd,
        }


@dataclass
class Skill:
    """Reusable capability with auto-activation triggers"""

    id: str
    name: str
    version: str
    description: str
    triggers: list[str]
    activation_prompt: str
    reasoning_methods: list[str]
    risk_level: str
    metrics: Metrics = field(default_factory=Metrics)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Skill":
        """Elegant factory: YAML dict → Skill instance"""
        metrics_data = data.get("metrics", {})
        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            description=data["description"],
            triggers=data["triggers"],
            activation_prompt=data["activation_prompt"],
            reasoning_methods=data["reasoning_methods"],
            risk_level=data["risk_level"],
            metrics=Metrics(**metrics_data),
        )

    def matches_trigger(self, text: str) -> bool:
        """Check if skill should activate based on trigger keywords"""
        text_lower = text.lower()
        return any(trigger.lower() in text_lower for trigger in self.triggers)


@dataclass
class Agent:
    """Persona-driven agent with skill composition"""

    id: str
    name: str
    version: str
    persona: str
    description: str
    iq: int
    skills: list[str]  # Skill IDs
    system_prompt: str
    reasoning_methods: list[str]
    risk_tolerance: str
    metrics: Metrics = field(default_factory=Metrics)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Agent":
        """Elegant factory: YAML dict → Agent instance"""
        metrics_data = data.get("metrics", {})
        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            persona=data["persona"],
            description=data["description"],
            iq=data["iq"],
            skills=data["skills"],
            system_prompt=data["system_prompt"],
            reasoning_methods=data["reasoning_methods"],
            risk_tolerance=data["risk_tolerance"],
            metrics=Metrics(**metrics_data),
        )


@dataclass
class AtomicThread:
    """JR decomposition unit for mission analysis"""

    purpose: str
    reasons: list[str]
    brakes: list[str]  # Risks/constraints
    risk_level: RiskLevel


@dataclass
class ExecutionResult:
    """Result of orchestrator execution"""

    agent_id: str
    activated_skills: list[str]
    reasoning_chain: list[str]
    output: str
    metrics: Metrics
    audit_hash: str
    timestamp: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


class PnklnOrchestrator:
    """Main execution engine for pnkln agent framework.

    Responsibilities:
    - Load skills/agents from YAML registries
    - Auto-activate skills based on triggers
    - Execute agent personas with skill compositions
    - Track metrics (time saved, revenue identified/generated)
    - Boy Scout Rule audit trail
    """

    def __init__(
        self,
        skills_registry_path: Path = SKILLS_REGISTRY,
        agents_registry_path: Path = AGENTS_REGISTRY,
        audit_log_dir: Path = AUDIT_LOG_DIR,
    ):
        self.skills_registry_path = skills_registry_path
        self.agents_registry_path = agents_registry_path
        self.audit_log_dir = audit_log_dir

        # Registries
        self.skills: dict[str, Skill] = {}
        self.agents: dict[str, Agent] = {}

        # Execution state
        self.current_agent: Agent | None = None
        self.execution_history: list[ExecutionResult] = []

        # Logging
        self._setup_logging()

        # Initialize
        self._load_registries()

    def _setup_logging(self) -> None:
        """Configure elegant logging (Jobs would approve)"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def _load_registries(self) -> None:
        """Load skills and agents from YAML registries"""
        try:
            # Load skills
            with open(self.skills_registry_path) as f:
                skills_data = yaml.safe_load(f)
                for skill_dict in skills_data["skills"]:
                    skill = Skill.from_dict(skill_dict)
                    self.skills[skill.id] = skill

            self.logger.info(f"✓ Loaded {len(self.skills)} skills")

            # Load agents
            with open(self.agents_registry_path) as f:
                agents_data = yaml.safe_load(f)
                for agent_dict in agents_data["agents"]:
                    agent = Agent.from_dict(agent_dict)
                    self.agents[agent.id] = agent

            self.logger.info(f"✓ Loaded {len(self.agents)} agents")

        except Exception as e:
            self.logger.error(f"✗ Failed to load registries: {e}")
            raise

    def activate_skills(self, prompt: str) -> list[Skill]:
        """Auto-activate skills based on trigger keywords.

        Returns list of skills that should activate for this prompt.
        Elegant pattern matching. No regex complexity.
        """
        activated = []

        for skill in self.skills.values():
            if skill.matches_trigger(prompt):
                activated.append(skill)
                self.logger.info(f"✓ Activated skill: {skill.name}")

        return activated

    def select_agent(self, agent_id: str | None = None) -> Agent:
        """Select agent for execution (defaults to ultrathink_designer)"""
        if agent_id is None:
            agent_id = "ultrathink_designer"  # Default Steve Jobs persona

        if agent_id not in self.agents:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent = self.agents[agent_id]
        self.current_agent = agent
        self.logger.info(f"✓ Selected agent: {agent.name} ({agent.persona})")

        return agent

    def execute(
        self,
        prompt: str,
        agent_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """Main execution method.

        1. Select agent (or use default)
        2. Auto-activate relevant skills
        3. Build execution context
        4. Generate reasoning chain
        5. Track metrics
        6. Audit trail (Boy Scout Rule)

        Returns ExecutionResult with full audit trail.
        """
        # Select agent
        agent = self.select_agent(agent_id)

        # Activate skills based on triggers
        activated_skills = self.activate_skills(prompt)

        # Filter to only skills this agent has access to
        agent_skills = [s for s in activated_skills if s.id in agent.skills]

        if not agent_skills:
            self.logger.warning(
                f"No matching skills for agent {agent.name}. Available: {agent.skills}",
            )

        # Build execution context
        self._build_context(prompt, agent, agent_skills, context)

        # Generate reasoning chain (placeholder - would integrate with LLM here)
        reasoning_chain = self._generate_reasoning_chain(agent, agent_skills, prompt)

        # Generate output (placeholder - would integrate with LLM here)
        output = self._generate_output(agent, agent_skills, prompt, reasoning_chain)

        # Track metrics (placeholder - would be populated by actual execution)
        metrics = Metrics(
            time_saved_hours=0.0,  # Would be calculated based on execution
            revenue_identified_usd=0.0,  # Would be extracted from monetization_architect
            revenue_generated_usd=0.0,  # Would be tracked over time
        )

        # Create audit trail
        audit_hash = self._create_audit_hash(agent, agent_skills, prompt, output)

        # Build result
        result = ExecutionResult(
            agent_id=agent.id,
            activated_skills=[s.id for s in agent_skills],
            reasoning_chain=reasoning_chain,
            output=output,
            metrics=metrics,
            audit_hash=audit_hash,
            timestamp=datetime.utcnow(),
        )

        # Save to execution history
        self.execution_history.append(result)

        # Boy Scout Rule: Write audit log
        self._write_audit_log(result)

        return result

    def _build_context(
        self,
        prompt: str,
        agent: Agent,
        skills: list[Skill],
        extra_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Build execution context with all relevant data"""
        return {
            "prompt": prompt,
            "agent": {
                "id": agent.id,
                "name": agent.name,
                "persona": agent.persona,
                "iq": agent.iq,
                "system_prompt": agent.system_prompt,
            },
            "activated_skills": [
                {
                    "id": s.id,
                    "name": s.name,
                    "activation_prompt": s.activation_prompt,
                    "reasoning_methods": s.reasoning_methods,
                }
                for s in skills
            ],
            "extra_context": extra_context or {},
        }

    def _generate_reasoning_chain(
        self,
        agent: Agent,
        skills: list[Skill],
        prompt: str,
    ) -> list[str]:
        """Generate reasoning chain using agent's preferred methods.

        Placeholder for now - would integrate with LLM to actually execute
        CoT, ToT, RCR, MAD, DTE reasoning.
        """
        chain = [
            f"Agent: {agent.name} ({agent.persona})",
            f"IQ: {agent.iq}",
            f"Activated skills: {[s.name for s in skills]}",
            f"Reasoning methods: {agent.reasoning_methods}",
            f"Prompt: {prompt}",
        ]

        # Add skill-specific reasoning
        for skill in skills:
            chain.append(f"→ {skill.name}: {skill.description}")

        return chain

    def _generate_output(
        self,
        agent: Agent,
        skills: list[Skill],
        prompt: str,
        reasoning_chain: list[str],
    ) -> str:
        """Generate output based on agent persona and activated skills.

        Placeholder for now - would integrate with LLM (Claude, Gemini, etc.)
        """
        output_lines = [
            f"# {agent.name} Response",
            "",
            f"**Persona**: {agent.persona}",
            f"**IQ**: {agent.iq}",
            "",
            f"**Activated Skills**: {', '.join([s.name for s in skills])}",
            "",
            "## Analysis",
            "",
            f"Your prompt: `{prompt}`",
            "",
            "## Reasoning Chain",
            "",
        ]

        output_lines.extend([f"- {step}" for step in reasoning_chain])

        output_lines.extend(
            [
                "",
                "## Output",
                "",
                "[Placeholder: Would integrate with LLM here to generate actual response]",
                "",
                "---",
                "",
                f"*Generated by {agent.name} at {datetime.utcnow().isoformat()}*",
            ],
        )

        return "\n".join(output_lines)

    def _create_audit_hash(
        self,
        agent: Agent,
        skills: list[Skill],
        prompt: str,
        output: str,
    ) -> str:
        """Create audit trail hash (Boy Scout Rule)"""
        audit_data = {
            "agent_id": agent.id,
            "skills": [s.id for s in skills],
            "prompt": prompt,
            "output": output,
            "timestamp": datetime.utcnow().isoformat(),
        }

        audit_json = json.dumps(audit_data, sort_keys=True)
        hash_obj = hashlib.new(HASH_ALGORITHM)
        hash_obj.update(audit_json.encode("utf-8"))

        return hash_obj.hexdigest()

    def _write_audit_log(self, result: ExecutionResult) -> None:
        """Write audit log to disk (Boy Scout Rule: leave cleaner than found)"""
        try:
            # Create audit log directory if it doesn't exist
            self.audit_log_dir.mkdir(parents=True, exist_ok=True)

            # Create timestamped log file
            timestamp_str = result.timestamp.strftime("%Y%m%d_%H%M%S")
            log_filename = f"execution_{timestamp_str}_{result.audit_hash[:8]}.json"
            log_path = self.audit_log_dir / log_filename

            # Write audit data
            audit_data = {
                "agent_id": result.agent_id,
                "activated_skills": result.activated_skills,
                "reasoning_chain": result.reasoning_chain,
                "output": result.output,
                "metrics": result.metrics.to_dict(),
                "audit_hash": result.audit_hash,
                "timestamp": result.timestamp.isoformat(),
            }

            with open(log_path, "w") as f:
                json.dump(audit_data, f, indent=2)

            self.logger.info(f"✓ Audit log written: {log_filename}")

        except Exception as e:
            self.logger.error(f"✗ Failed to write audit log: {e}")

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get aggregated metrics across all executions"""
        total_time_saved = sum(r.metrics.time_saved_hours for r in self.execution_history)
        total_revenue_identified = sum(
            r.metrics.revenue_identified_usd for r in self.execution_history
        )
        total_revenue_generated = sum(
            r.metrics.revenue_generated_usd for r in self.execution_history
        )

        return {
            "total_executions": len(self.execution_history),
            "total_time_saved_hours": total_time_saved,
            "total_revenue_identified_usd": total_revenue_identified,
            "total_revenue_generated_usd": total_revenue_generated,
            "agents_used": list(set(r.agent_id for r in self.execution_history)),
            "skills_activated": list(
                set(skill for r in self.execution_history for skill in r.activated_skills),
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def create_orchestrator() -> PnklnOrchestrator:
    """Factory function: Create orchestrator with default config"""
    return PnklnOrchestrator()


def execute_prompt(prompt: str, agent_id: str | None = None) -> ExecutionResult:
    """Convenience function: One-liner execution"""
    orchestrator = create_orchestrator()
    return orchestrator.execute(prompt, agent_id=agent_id)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN (for testing)
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    """Test the orchestrator"""
    print("═" * 80)
    print("PNKLN ORCHESTRATOR - Test Execution")
    print("═" * 80)
    print()

    # Create orchestrator
    orchestrator = create_orchestrator()

    # Test prompt
    test_prompt = "Research edge AI compute market and identify revenue opportunities"

    print(f"Test Prompt: {test_prompt}")
    print()

    # Execute
    result = orchestrator.execute(test_prompt)

    print("─" * 80)
    print("RESULT:")
    print("─" * 80)
    print(result.output)
    print()

    # Show metrics
    metrics = orchestrator.get_metrics_summary()
    print("─" * 80)
    print("METRICS:")
    print("─" * 80)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
