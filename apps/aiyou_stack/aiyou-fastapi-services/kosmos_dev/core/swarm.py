"""Swarm Manager: Spawn and orchestrate hundreds of IQ-160 agents.

Implements Kosmos paper patterns:
- Two core agent types: Data Analysis + Literature Search
- Structured world model sharing between agents
- 200+ agent rollouts per run
- Full traceability of all findings
- Linear scaling with cycles
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from kosmos_dev.core.whiteboard import Finding, Vote, Whiteboard


class AgentType(Enum):
    """Core agent types per Kosmos paper."""

    DATA_ANALYSIS = "data_analysis"  # Generates code, executes analyses
    LITERATURE_SEARCH = "literature_search"  # Finds docs, papers, patterns


class AgentPersona(Enum):
    """Persona configurations injected into base agent types."""

    # Data Analysis personas
    CTO = "cto"  # Technical architecture
    CFO = "cfo"  # Cost modeling
    COO = "coo"  # Execution metrics

    # Literature Search personas
    CEO = "ceo"  # Market research
    COFOUNDER = "cofounder"  # Strategy validation
    GENERAL_COUNSEL = "general_counsel"  # Compliance research

    # Specialized (can be either type)
    SYNTHESIS = "synthesis"  # Aggregates findings


# Map personas to their base agent type
PERSONA_TO_TYPE = {
    AgentPersona.CTO: AgentType.DATA_ANALYSIS,
    AgentPersona.CFO: AgentType.DATA_ANALYSIS,
    AgentPersona.COO: AgentType.DATA_ANALYSIS,
    AgentPersona.CEO: AgentType.LITERATURE_SEARCH,
    AgentPersona.COFOUNDER: AgentType.LITERATURE_SEARCH,
    AgentPersona.GENERAL_COUNSEL: AgentType.LITERATURE_SEARCH,
    AgentPersona.SYNTHESIS: AgentType.DATA_ANALYSIS,
}


@dataclass
class AgentConfig:
    """Configuration for a swarm agent."""

    agent_type: AgentType
    persona: AgentPersona
    iq_level: int = 160
    model: str = "gemini-pro"
    temperature: float = 0.3
    max_tokens: int = 8192


# IQ-160 baseline prompt injected into all agents
IQ_160_BASELINE = """
You are operating at IQ 160 cognitive level with the following characteristics:

KERNEL Framework (mandatory):
- Keep simple: Prefer elegant, minimal solutions
- Easy verify: All claims must be verifiable
- Reproducible: Document steps for reproduction
- Narrow: Focus on specific problem scope
- Explicit: State assumptions clearly
- Logical: Use rigorous reasoning chains

Cognitive Enhancements (+25% vs baseline):
- Innovation Depth: Novel pattern recognition
- Risk Detection: Edge cases and systemic vulnerabilities
- Doctrine Alignment: Maximum analytical rigor

Decision Framework:
- Business Judgment Rule: Informed, reasonable, good-faith
- First principles thinking on all problems
- Scenario planning (base/best/worst analysis)
- Full traceability: Cite ALL evidence for claims
"""

# Agent type base prompts (per Kosmos paper)
AGENT_TYPE_PROMPTS = {
    AgentType.DATA_ANALYSIS: """
You are a DATA ANALYSIS AGENT (per Kosmos paper architecture).

Your role:
- Generate and execute code to analyze data
- Produce artifacts (code, tests, visualizations)
- Run statistical analyses and validations
- Create reproducible analysis pipelines

You share information with Literature Search agents via the structured world model.
All code must be fully traceable with citations to requirements and prior findings.
""",
    AgentType.LITERATURE_SEARCH: """
You are a LITERATURE SEARCH AGENT (per Kosmos paper architecture).

Your role:
- Find relevant documentation, papers, and existing code
- Synthesize information from multiple sources
- Identify patterns and best practices
- Provide context for Data Analysis agents

You share information with Data Analysis agents via the structured world model.
All findings must cite specific sources with relevance scores.
""",
}

# Persona-specific prompts
PERSONA_PROMPTS = {
    AgentPersona.CTO: """
PERSONA: Virtual CTO

Expertise:
- SaaS infrastructure at scale (millions of users)
- AI/ML content pipelines (generative, recommendation, moderation)
- Cloud platforms (AWS/GCP/Azure), Kubernetes, serverless
- Security: Zero-trust, encryption, SOC2/GDPR/HIPAA
- Petabyte-scale data management

Wisdom from: Jeff Dean (scale early), Werner Vogels (you build it, you run it),
Patrick Collison (radical customer focus), Satya Nadella (empathy as innovation driver).

Focus: Technical architecture, system design, performance optimization.
""",
    AgentPersona.COFOUNDER: """
PERSONA: Strategic Cofounder

Expertise:
- VRIO analysis, Value Stick, Blue Ocean strategy
- McKinsey Horizons (H1/H2/H3 portfolio allocation)
- Monte Carlo simulations for scenario planning
- ROI thresholds (≥3x in 18 months), 4:1 LTV:CAC gates

Frameworks: Disciplined Entrepreneurship (24-step MIT), Mochary's CEO System,
Naval Ravikant/Cold Start/7 Powers principles.

Focus: Strategic validation, competitive analysis, investment criteria.
""",
    AgentPersona.CFO: """
PERSONA: CFO

Expertise:
- SaaS metrics: CAC, LTV, churn, ARPU, ARR/MRR
- Risk quantification and financial modeling
- Runway management and budget enforcement
- Cost optimization and cloud spend analysis

Focus: Cost modeling, financial projections, budget controls.
""",
    AgentPersona.GENERAL_COUNSEL: """
PERSONA: General Counsel

Expertise:
- IP rights, DMCA, fair use, copyright law
- GDPR, CCPA, SOC2, HIPAA compliance
- EU AI Act, DSA, international regulations
- Business Judgment Rule (California law anchor)
- Risk mitigation and incident response

Focus: Compliance research, IP review, regulatory guidance.
""",
    AgentPersona.COO: """
PERSONA: COO

Expertise:
- Execution and operational efficiency
- Drag logging and bottleneck identification
- Process optimization and automation
- Team coordination and resource allocation

Focus: Execution metrics, operational analysis, process improvement.
""",
    AgentPersona.CEO: """
PERSONA: CEO

Expertise:
- Visionary strategy and market positioning
- Investor relations and storytelling
- Culture building and team leadership
- Long-term roadmap and vision

Focus: Market research, roadmap validation, stakeholder communication.
""",
    AgentPersona.SYNTHESIS: """
PERSONA: Synthesis Agent

Role:
- Aggregate findings from all other agents
- Apply consensus voting with confidence weighting
- Resolve conflicts through evidence analysis
- Produce final reports with full traceability

Target: 79.4% verification accuracy (Kosmos benchmark).
Every conclusion must cite specific code or document references.
""",
}


@dataclass
class SwarmAgent:
    """An individual agent in the swarm."""

    id: str
    config: AgentConfig
    whiteboard: Whiteboard
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Metrics
    findings_posted: int = 0
    votes_cast: int = 0
    tokens_used: int = 0

    def get_system_prompt(self) -> str:
        """Generate full system prompt: IQ-160 + agent type + persona."""
        return f"""
{IQ_160_BASELINE}

{AGENT_TYPE_PROMPTS.get(self.config.agent_type, "")}

{PERSONA_PROMPTS.get(self.config.persona, "")}

Session ID: {self.whiteboard.session_id}
Agent ID: {self.id}
Agent Type: {self.config.agent_type.value}
Persona: {self.config.persona.value}
IQ Level: {self.config.iq_level}

CRITICAL: Every finding MUST include:
1. Specific evidence (file paths, code lines, document references)
2. Confidence score with justification
3. Methodology used
4. Citation to source material
"""

    async def post_finding(self, finding: Finding) -> None:
        """Post a finding to the whiteboard."""
        finding.discovered_by = self.id
        await self.whiteboard.post_finding(finding)
        self.findings_posted += 1

    async def vote_on_finding(
        self,
        finding_id: str,
        agrees: bool,
        confidence: float,
        reasoning: str,
    ) -> None:
        """Vote on another agent's finding."""
        vote = Vote(
            agent_id=self.id,
            agent_persona=self.config.persona.value,
            agrees=agrees,
            confidence=confidence,
            reasoning=reasoning,
        )
        await self.whiteboard.add_vote(finding_id, vote)
        self.votes_cast += 1


class SwarmManager:
    """Manages the agent swarm for Kosmos Dev.

    Implements Kosmos paper pattern:
    - Data Analysis agents + Literature Search agents
    - Structured world model sharing
    - 200+ agent rollouts per run
    - Linear scaling of discoveries with cycles
    """

    def __init__(
        self,
        whiteboard: Whiteboard,
        max_agents: int = 200,
        default_model: str = "gemini-pro",
    ):
        self.whiteboard = whiteboard
        self.max_agents = max_agents
        self.default_model = default_model

        self._agents: dict[str, SwarmAgent] = {}

        # Metrics (Kosmos-style)
        self.total_rollouts = 0
        self.total_tokens = 0
        self.cycle_count = 0

    def spawn_agent(
        self,
        persona: AgentPersona,
        iq_level: int = 160,
        model: str | None = None,
    ) -> SwarmAgent:
        """Spawn a new agent with specified persona."""
        if len(self._agents) >= self.max_agents:
            raise RuntimeError(f"Max agents ({self.max_agents}) reached")

        agent_id = f"{persona.value}_{uuid.uuid4().hex[:8]}"

        # Get base agent type for this persona
        agent_type = PERSONA_TO_TYPE.get(persona, AgentType.DATA_ANALYSIS)

        config = AgentConfig(
            agent_type=agent_type,
            persona=persona,
            iq_level=iq_level,
            model=model or self.default_model,
        )

        agent = SwarmAgent(
            id=agent_id,
            config=config,
            whiteboard=self.whiteboard,
        )

        self._agents[agent_id] = agent
        return agent

    def spawn_core_agents(self) -> list[SwarmAgent]:
        """Spawn the core agent set per Kosmos paper."""
        agents = []

        # Data Analysis agents
        for persona in [AgentPersona.CTO, AgentPersona.CFO, AgentPersona.COO]:
            agent = self.spawn_agent(persona)
            agents.append(agent)

        # Literature Search agents
        for persona in [AgentPersona.CEO, AgentPersona.COFOUNDER, AgentPersona.GENERAL_COUNSEL]:
            agent = self.spawn_agent(persona, model="gemini-flash")  # Faster for search
            agents.append(agent)

        # Synthesis agent
        synthesis = self.spawn_agent(AgentPersona.SYNTHESIS)
        agents.append(synthesis)

        return agents

    def spawn_swarm(
        self,
        additional_data_analysis: int = 0,
        additional_literature: int = 0,
    ) -> list[SwarmAgent]:
        """Spawn full swarm with additional agents for scale."""
        agents = self.spawn_core_agents()

        # Additional Data Analysis agents
        data_personas = [AgentPersona.CTO, AgentPersona.CFO, AgentPersona.COO]
        for i in range(additional_data_analysis):
            persona = data_personas[i % len(data_personas)]
            agent = self.spawn_agent(persona)
            agents.append(agent)

        # Additional Literature Search agents
        lit_personas = [AgentPersona.CEO, AgentPersona.COFOUNDER, AgentPersona.GENERAL_COUNSEL]
        for i in range(additional_literature):
            persona = lit_personas[i % len(lit_personas)]
            agent = self.spawn_agent(persona, model="gemini-flash")
            agents.append(agent)

        return agents

    def get_agent(self, agent_id: str) -> SwarmAgent | None:
        """Get an agent by ID."""
        return self._agents.get(agent_id)

    def get_agents_by_type(self, agent_type: AgentType) -> list[SwarmAgent]:
        """Get all agents of a specific type."""
        return [a for a in self._agents.values() if a.config.agent_type == agent_type]

    def get_data_analysis_agents(self) -> list[SwarmAgent]:
        """Get all Data Analysis agents."""
        return self.get_agents_by_type(AgentType.DATA_ANALYSIS)

    def get_literature_agents(self) -> list[SwarmAgent]:
        """Get all Literature Search agents."""
        return self.get_agents_by_type(AgentType.LITERATURE_SEARCH)

    def get_all_agents(self) -> list[SwarmAgent]:
        """Get all active agents."""
        return list(self._agents.values())

    def terminate_agent(self, agent_id: str) -> None:
        """Terminate an agent."""
        if agent_id in self._agents:
            del self._agents[agent_id]

    def terminate_all(self) -> None:
        """Terminate all agents."""
        self._agents.clear()

    def increment_cycle(self) -> int:
        """Increment cycle count (Kosmos linear scaling pattern)."""
        self.cycle_count += 1
        return self.cycle_count

    def get_metrics(self) -> dict[str, Any]:
        """Get swarm metrics."""
        return {
            "active_agents": len(self._agents),
            "max_agents": self.max_agents,
            "total_rollouts": self.total_rollouts,
            "total_tokens": self.total_tokens,
            "cycle_count": self.cycle_count,
            "data_analysis_agents": len(self.get_data_analysis_agents()),
            "literature_agents": len(self.get_literature_agents()),
            "total_findings": sum(a.findings_posted for a in self._agents.values()),
            "total_votes": sum(a.votes_cast for a in self._agents.values()),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize swarm state."""
        return {
            "session_id": self.whiteboard.session_id,
            "max_agents": self.max_agents,
            "default_model": self.default_model,
            "metrics": self.get_metrics(),
            "agents": {
                aid: {
                    "id": a.id,
                    "agent_type": a.config.agent_type.value,
                    "persona": a.config.persona.value,
                    "iq_level": a.config.iq_level,
                    "model": a.config.model,
                    "findings_posted": a.findings_posted,
                    "votes_cast": a.votes_cast,
                    "tokens_used": a.tokens_used,
                }
                for aid, a in self._agents.items()
            },
        }
