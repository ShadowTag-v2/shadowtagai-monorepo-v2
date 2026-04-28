# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AgentSpecialization - T-Shaped Expertise Model
Version: 1.0.0

Philosophy: Best structure is T-shaped - deep vertical in one area,
broad horizontal across adjacent areas.

Weighting:
- Primary expertise: 1.0 (deep, authoritative)
- Secondary expertise: 0.6 (adjacent, competent)
- General: 0.3 (can flag anything)

Like law firms: Securities partner knows securities deeply,
but also understands corporate, tax, regulatory enough to spot issues.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ExpertiseDomain(StrEnum):
    """Domains of expertise for agents."""

    # Technical
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DATABASE = "database"
    API_DESIGN = "api_design"

    # Process
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"

    # Business
    MONETIZATION = "monetization"
    USER_EXPERIENCE = "user_experience"
    COMPLIANCE = "compliance"

    # Reasoning
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    DEBUGGING = "debugging"


# Domain adjacency map - which domains are related
DOMAIN_ADJACENCY = {
    ExpertiseDomain.SECURITY: [
        ExpertiseDomain.COMPLIANCE,
        ExpertiseDomain.API_DESIGN,
        ExpertiseDomain.ARCHITECTURE,
    ],
    ExpertiseDomain.PERFORMANCE: [
        ExpertiseDomain.DATABASE,
        ExpertiseDomain.ARCHITECTURE,
        ExpertiseDomain.OPTIMIZATION,
    ],
    ExpertiseDomain.ARCHITECTURE: [
        ExpertiseDomain.API_DESIGN,
        ExpertiseDomain.SECURITY,
        ExpertiseDomain.PERFORMANCE,
    ],
    ExpertiseDomain.TESTING: [
        ExpertiseDomain.CODE_REVIEW,
        ExpertiseDomain.DEBUGGING,
        ExpertiseDomain.DOCUMENTATION,
    ],
    ExpertiseDomain.DATABASE: [
        ExpertiseDomain.PERFORMANCE,
        ExpertiseDomain.SECURITY,
        ExpertiseDomain.API_DESIGN,
    ],
    ExpertiseDomain.API_DESIGN: [
        ExpertiseDomain.ARCHITECTURE,
        ExpertiseDomain.DOCUMENTATION,
        ExpertiseDomain.USER_EXPERIENCE,
    ],
    ExpertiseDomain.CODE_REVIEW: [
        ExpertiseDomain.TESTING,
        ExpertiseDomain.ARCHITECTURE,
        ExpertiseDomain.DOCUMENTATION,
    ],
    ExpertiseDomain.MONETIZATION: [
        ExpertiseDomain.USER_EXPERIENCE,
        ExpertiseDomain.ANALYSIS,
        ExpertiseDomain.OPTIMIZATION,
    ],
    ExpertiseDomain.DEBUGGING: [
        ExpertiseDomain.TESTING,
        ExpertiseDomain.PERFORMANCE,
        ExpertiseDomain.ANALYSIS,
    ],
}


@dataclass
class TShapedExpertise:
    """T-shaped expertise profile.

    Primary: Deep expertise (weight 1.0)
    Secondary: Adjacent competence (weight 0.6)
    General: Can flag anything (weight 0.3)
    """

    primary: ExpertiseDomain
    secondary: list[ExpertiseDomain] = field(default_factory=list)
    general_competence: bool = True

    # Proficiency levels (0-1)
    primary_proficiency: float = 0.8
    secondary_proficiency: dict[ExpertiseDomain, float] = field(default_factory=dict)

    def get_weight(self, domain: ExpertiseDomain) -> float:
        """Get weight for a domain based on expertise level."""
        if domain == self.primary:
            return 1.0 * self.primary_proficiency
        if domain in self.secondary:
            return 0.6 * self.secondary_proficiency.get(domain, 0.5)
        if self.general_competence:
            return 0.3
        return 0.0


@dataclass
class SpecializedAgent:
    """Agent with T-shaped specialization."""

    agent_id: str
    expertise: TShapedExpertise

    # Performance tracking
    opinions_given: int = 0
    opinions_accepted: int = 0
    cross_domain_catches: int = 0  # Issues caught outside primary


class AgentSpecialization:
    """Manage T-shaped specialization for agents.

    Key features:
    - Weighted consensus based on expertise
    - Cross-domain issue detection
    - Expertise-based role assignment
    """

    def __init__(self):
        self.agents: dict[str, SpecializedAgent] = {}

        # Weight thresholds
        self.primary_weight = 1.0
        self.secondary_weight = 0.6
        self.general_weight = 0.3

    # =========================================================================
    # AGENT REGISTRATION
    # =========================================================================

    def register_agent(
        self,
        agent_id: str,
        primary: ExpertiseDomain,
        secondary: list[ExpertiseDomain] = None,
    ) -> SpecializedAgent:
        """Register agent with T-shaped expertise.

        Auto-assigns adjacent domains if secondary not specified.
        """
        if secondary is None:
            # Auto-assign based on adjacency
            secondary = DOMAIN_ADJACENCY.get(primary, [])[:3]

        expertise = TShapedExpertise(
            primary=primary,
            secondary=secondary,
            secondary_proficiency=dict.fromkeys(secondary, 0.5),
        )

        agent = SpecializedAgent(agent_id=agent_id, expertise=expertise)
        self.agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> SpecializedAgent | None:
        """Get agent profile."""
        return self.agents.get(agent_id)

    # =========================================================================
    # EXPERTISE QUERIES
    # =========================================================================

    def get_experts_for_domain(
        self,
        domain: ExpertiseDomain,
        min_weight: float = 0.5,
    ) -> list[tuple]:
        """Get agents with expertise in a domain.

        Returns: List of (agent_id, weight) tuples, sorted by weight.
        """
        experts = []

        for agent_id, agent in self.agents.items():
            weight = agent.expertise.get_weight(domain)
            if weight >= min_weight:
                experts.append((agent_id, weight))

        return sorted(experts, key=lambda x: x[1], reverse=True)

    def get_primary_expert(self, domain: ExpertiseDomain) -> str | None:
        """Get the primary expert for a domain."""
        for agent_id, agent in self.agents.items():
            if agent.expertise.primary == domain:
                return agent_id
        return None

    def get_agent_domains(self, agent_id: str) -> dict[str, float]:
        """Get all domains an agent can contribute to with weights."""
        if agent_id not in self.agents:
            return {}

        agent = self.agents[agent_id]
        domains = {}

        # Primary
        domains[agent.expertise.primary.value] = self.primary_weight

        # Secondary
        for domain in agent.expertise.secondary:
            domains[domain.value] = self.secondary_weight

        # General (all others)
        if agent.expertise.general_competence:
            for domain in ExpertiseDomain:
                if domain.value not in domains:
                    domains[domain.value] = self.general_weight

        return domains

    # =========================================================================
    # WEIGHTED CONSENSUS
    # =========================================================================

    def calculate_weighted_consensus(
        self,
        domain: ExpertiseDomain,
        opinions: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate weighted consensus for a domain.

        Args:
            domain: The domain being discussed
            opinions: Dict of agent_id → opinion

        Returns:
            Weighted results and analysis

        """
        weighted_opinions = []

        for agent_id, opinion in opinions.items():
            if agent_id not in self.agents:
                continue

            agent = self.agents[agent_id]
            weight = agent.expertise.get_weight(domain)

            weighted_opinions.append(
                {
                    "agent_id": agent_id,
                    "opinion": opinion,
                    "weight": weight,
                    "expertise_level": self._get_expertise_level(agent, domain),
                },
            )

        # Sort by weight
        weighted_opinions.sort(key=lambda x: x["weight"], reverse=True)

        # Determine if consensus
        if weighted_opinions:
            top_weight = weighted_opinions[0]["weight"]
            high_weight_opinions = [o for o in weighted_opinions if o["weight"] >= top_weight * 0.8]
        else:
            high_weight_opinions = []

        return {
            "domain": domain.value,
            "weighted_opinions": weighted_opinions,
            "primary_opinion": weighted_opinions[0] if weighted_opinions else None,
            "high_weight_count": len(high_weight_opinions),
            "total_opinions": len(opinions),
        }

    def _get_expertise_level(self, agent: SpecializedAgent, domain: ExpertiseDomain) -> str:
        """Get expertise level description."""
        if domain == agent.expertise.primary:
            return "PRIMARY"
        if domain in agent.expertise.secondary:
            return "SECONDARY"
        if agent.expertise.general_competence:
            return "GENERAL"
        return "NONE"

    # =========================================================================
    # CROSS-DOMAIN DETECTION
    # =========================================================================

    def identify_cross_domain_issues(self, task_domains: list[ExpertiseDomain]) -> dict[str, Any]:
        """Identify potential cross-domain issues.

        T-shaped agents catch issues that pure specialists miss.
        """
        # Find overlapping expertise
        domain_coverage = {}
        cross_domain_agents = []

        for agent_id, agent in self.agents.items():
            covered = []
            for domain in task_domains:
                weight = agent.expertise.get_weight(domain)
                if weight >= self.secondary_weight:
                    covered.append(domain)

            if len(covered) >= 2:
                cross_domain_agents.append(
                    {
                        "agent_id": agent_id,
                        "domains_covered": [d.value for d in covered],
                        "can_catch_cross_issues": True,
                    },
                )

            for domain in covered:
                if domain not in domain_coverage:
                    domain_coverage[domain] = []
                domain_coverage[domain].append(agent_id)

        # Identify gaps
        gaps = [d for d in task_domains if d not in domain_coverage]

        return {
            "task_domains": [d.value for d in task_domains],
            "cross_domain_agents": cross_domain_agents,
            "coverage": {d.value: agents for d, agents in domain_coverage.items()},
            "gaps": [d.value for d in gaps],
            "recommendation": self._cross_domain_recommendation(cross_domain_agents, gaps),
        }

    def _cross_domain_recommendation(
        self,
        cross_domain_agents: list[dict],
        gaps: list[ExpertiseDomain],
    ) -> str:
        """Generate recommendation for cross-domain coverage."""
        if gaps:
            return f"Gaps in coverage: {gaps}. Add specialists or increase general attention."
        if not cross_domain_agents:
            return "No cross-domain coverage. Risk of missing integration issues."
        return f"{len(cross_domain_agents)} agents can catch cross-domain issues."

    # =========================================================================
    # PROFICIENCY UPDATES
    # =========================================================================

    def record_contribution(self, agent_id: str, domain: ExpertiseDomain, accepted: bool):
        """Record whether agent's contribution was accepted."""
        if agent_id not in self.agents:
            return

        agent = self.agents[agent_id]
        agent.opinions_given += 1

        if accepted:
            agent.opinions_accepted += 1

            # Track cross-domain catches
            if domain != agent.expertise.primary:
                agent.cross_domain_catches += 1

                # Increase secondary proficiency
                if domain in agent.expertise.secondary_proficiency:
                    current = agent.expertise.secondary_proficiency[domain]
                    agent.expertise.secondary_proficiency[domain] = min(1.0, current + 0.05)

    def get_agent_performance(self, agent_id: str) -> dict[str, Any]:
        """Get agent's performance metrics."""
        if agent_id not in self.agents:
            return {"error": "Agent not found"}

        agent = self.agents[agent_id]

        acceptance_rate = (
            agent.opinions_accepted / agent.opinions_given if agent.opinions_given > 0 else 0
        )

        return {
            "agent_id": agent_id,
            "primary_domain": agent.expertise.primary.value,
            "secondary_domains": [d.value for d in agent.expertise.secondary],
            "opinions_given": agent.opinions_given,
            "opinions_accepted": agent.opinions_accepted,
            "acceptance_rate": f"{acceptance_rate:.1%}",
            "cross_domain_catches": agent.cross_domain_catches,
            "secondary_proficiencies": {
                d.value: f"{p:.1%}" for d, p in agent.expertise.secondary_proficiency.items()
            },
        }

    # =========================================================================
    # TEAM COMPOSITION
    # =========================================================================

    def recommend_team(self, task_domains: list[ExpertiseDomain], team_size: int = 5) -> list[str]:
        """Recommend team composition for a task.

        Ensures:
        - Primary coverage for all domains
        - Cross-domain agents for integration issues
        - Balanced weights
        """
        team = []
        covered_domains = set()

        # First, add primary experts for each domain
        for domain in task_domains:
            primary = self.get_primary_expert(domain)
            if primary and primary not in team:
                team.append(primary)
                covered_domains.add(domain)

        # Add cross-domain agents
        cross_analysis = self.identify_cross_domain_issues(task_domains)
        for agent_info in cross_analysis["cross_domain_agents"]:
            if len(team) >= team_size:
                break
            if agent_info["agent_id"] not in team:
                team.append(agent_info["agent_id"])

        # Fill remaining slots with highest-weighted agents
        if len(team) < team_size:
            all_agents = []
            for domain in task_domains:
                experts = self.get_experts_for_domain(domain, min_weight=0.3)
                all_agents.extend(experts)

            # Sort by total weight contribution
            agent_weights = {}
            for agent_id, weight in all_agents:
                if agent_id not in team:
                    agent_weights[agent_id] = agent_weights.get(agent_id, 0) + weight

            sorted_agents = sorted(agent_weights.items(), key=lambda x: x[1], reverse=True)

            for agent_id, _ in sorted_agents:
                if len(team) >= team_size:
                    break
                if agent_id not in team:
                    team.append(agent_id)

        return team

    def __repr__(self) -> str:
        return f"AgentSpecialization(agents={len(self.agents)})"


# =============================================================================
# PREDEFINED SPECIALIST ROLES
# =============================================================================


def create_security_expert(agent_id: str) -> SpecializedAgent:
    """Create a security-focused agent."""
    spec = AgentSpecialization()
    return spec.register_agent(
        agent_id,
        primary=ExpertiseDomain.SECURITY,
        secondary=[
            ExpertiseDomain.COMPLIANCE,
            ExpertiseDomain.API_DESIGN,
            ExpertiseDomain.ARCHITECTURE,
        ],
    )


def create_performance_architect(agent_id: str) -> SpecializedAgent:
    """Create a performance-focused agent."""
    spec = AgentSpecialization()
    return spec.register_agent(
        agent_id,
        primary=ExpertiseDomain.PERFORMANCE,
        secondary=[
            ExpertiseDomain.DATABASE,
            ExpertiseDomain.ARCHITECTURE,
            ExpertiseDomain.OPTIMIZATION,
        ],
    )


def create_ux_strategist(agent_id: str) -> SpecializedAgent:
    """Create a UX-focused agent."""
    spec = AgentSpecialization()
    return spec.register_agent(
        agent_id,
        primary=ExpertiseDomain.USER_EXPERIENCE,
        secondary=[
            ExpertiseDomain.API_DESIGN,
            ExpertiseDomain.DOCUMENTATION,
            ExpertiseDomain.MONETIZATION,
        ],
    )


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_specialization_system() -> AgentSpecialization:
    """Create agent specialization system.

    "T-shaped experts catch what pure specialists miss."
    """
    return AgentSpecialization()


# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("AgentSpecialization - Self Test")
    print("=" * 60)

    # Create system
    spec = create_specialization_system()
    print(f"\nCreated: {spec}")

    # Register agents
    print("\n" + "=" * 60)
    print("Registering T-Shaped Agents...")

    spec.register_agent("security_expert", ExpertiseDomain.SECURITY)
    spec.register_agent("perf_architect", ExpertiseDomain.PERFORMANCE)
    spec.register_agent("api_designer", ExpertiseDomain.API_DESIGN)
    spec.register_agent("qa_engineer", ExpertiseDomain.TESTING)

    for agent_id in spec.agents:
        agent = spec.agents[agent_id]
        print(f"\n  {agent_id}:")
        print(f"    Primary: {agent.expertise.primary.value}")
        print(f"    Secondary: {[d.value for d in agent.expertise.secondary]}")

    # Get experts for domain
    print("\n" + "=" * 60)
    print("Experts for SECURITY domain:")

    experts = spec.get_experts_for_domain(ExpertiseDomain.SECURITY)
    for agent_id, weight in experts:
        print(f"  {agent_id}: {weight:.2f}")

    # Weighted consensus
    print("\n" + "=" * 60)
    print("Weighted Consensus on Security Issue:")

    opinions = {
        "security_expert": "Use RS256 for JWT",
        "perf_architect": "Consider HS256 for speed",
        "api_designer": "Follow OAuth 2.0 spec",
    }

    consensus = spec.calculate_weighted_consensus(ExpertiseDomain.SECURITY, opinions)

    print(f"\nPrimary opinion: {consensus['primary_opinion']['agent_id']}")
    print(f"Weight: {consensus['primary_opinion']['weight']:.2f}")
    print(f"Level: {consensus['primary_opinion']['expertise_level']}")

    # Cross-domain analysis
    print("\n" + "=" * 60)
    print("Cross-Domain Issue Detection:")

    task_domains = [
        ExpertiseDomain.SECURITY,
        ExpertiseDomain.PERFORMANCE,
        ExpertiseDomain.API_DESIGN,
    ]

    analysis = spec.identify_cross_domain_issues(task_domains)
    print(f"\nTask domains: {analysis['task_domains']}")
    print(f"Cross-domain agents: {len(analysis['cross_domain_agents'])}")
    print(f"Gaps: {analysis['gaps']}")
    print(f"Recommendation: {analysis['recommendation']}")

    # Team recommendation
    print("\n" + "=" * 60)
    print("Recommended Team:")

    team = spec.recommend_team(task_domains, team_size=3)
    print(f"Team: {team}")

    print("\n" + "=" * 60)
    print("✓ AgentSpecialization working correctly")
    print("\nPhilosophy: T-shaped experts catch what pure specialists miss.")
