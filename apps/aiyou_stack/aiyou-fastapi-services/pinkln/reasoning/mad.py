"""Multi-Agent Debate (MAD) reasoning framework.

MAD enables multiple agents to debate solutions, critique each other, and reach
consensus. This improves reasoning accuracy and robustness through collaborative
refinement.

Usage:
    mad = MultiAgentDebate(num_agents=3)
    result = await mad.debate("Complex problem requiring multiple perspectives")
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .rcr import CritiqueResult, ReflectCritiqueRefine, ReflectionResult


class DebateRole(Enum):
    """Roles in multi-agent debate."""

    PROPOSER = "proposer"  # Proposes initial solutions
    CRITIC = "critic"  # Challenges and critiques
    SYNTHESIZER = "synthesizer"  # Integrates perspectives
    MODERATOR = "moderator"  # Guides discussion


@dataclass
class DebateAgent:
    """An agent participating in debate."""

    id: str
    role: DebateRole
    persona: str  # e.g., "Optimist", "Skeptic", "Pragmatist"
    current_position: Any | None = None
    confidence: float = 0.5
    active: bool = True  # False if agent has "left" the debate


@dataclass
class DebateRound:
    """A single round of debate."""

    round_number: int
    agent_positions: dict[str, Any] = field(default_factory=dict)
    reflections: dict[str, ReflectionResult] = field(default_factory=dict)
    critiques: dict[str, list[CritiqueResult]] = field(default_factory=dict)
    consensus_score: float = 0.0
    summary: str = ""


class MultiAgentDebate:
    """Multi-Agent Debate framework implementation.

    This framework:
    1. Creates multiple agents with different perspectives
    2. Runs rounds of debate using RCR
    3. Tracks consensus convergence
    4. Produces final consolidated answer
    """

    def __init__(self, num_agents: int = 3, max_rounds: int = 5, consensus_threshold: float = 0.85):
        """Initialize MAD framework.

        Args:
            num_agents: Number of agents in debate
            max_rounds: Maximum debate rounds
            consensus_threshold: Threshold for reaching consensus (0-1)

        """
        self.num_agents = num_agents
        self.max_rounds = max_rounds
        self.consensus_threshold = consensus_threshold
        self.agents: list[DebateAgent] = []
        self.rounds: list[DebateRound] = []
        self.rcr = ReflectCritiqueRefine()

    async def debate(
        self,
        problem: str,
        personas: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Conduct multi-agent debate.

        Args:
            problem: Problem to debate
            personas: Optional list of agent personas
            context: Optional context

        Returns:
            Debate results with consensus answer

        """
        # Initialize agents
        self._initialize_agents(personas or ["Optimist", "Skeptic", "Pragmatist"])

        # Run debate rounds
        for round_num in range(1, self.max_rounds + 1):
            debate_round = await self._run_round(round_num, problem, context)
            self.rounds.append(debate_round)

            # Check for consensus
            if debate_round.consensus_score >= self.consensus_threshold:
                break

            # Remove agents with very low confidence (they "leave" the debate)
            self._prune_low_confidence_agents()

        # Synthesize final answer
        final_answer = await self._synthesize_consensus()

        return {
            "problem": problem,
            "num_rounds": len(self.rounds),
            "final_answer": final_answer,
            "consensus_score": self.rounds[-1].consensus_score if self.rounds else 0,
            "debate_history": [
                {
                    "round": r.round_number,
                    "positions": r.agent_positions,
                    "consensus": r.consensus_score,
                }
                for r in self.rounds
            ],
            "metadata": {
                "method": "multi_agent_debate",
                "num_agents": len([a for a in self.agents if a.active]),
                "consensus_reached": self.rounds[-1].consensus_score >= self.consensus_threshold
                if self.rounds
                else False,
            },
        }

    def _initialize_agents(self, personas: list[str]):
        """Initialize debate agents."""
        roles = [DebateRole.PROPOSER, DebateRole.CRITIC, DebateRole.SYNTHESIZER]

        for i in range(self.num_agents):
            agent = DebateAgent(
                id=f"agent_{i + 1}",
                role=roles[i % len(roles)],
                persona=personas[i] if i < len(personas) else f"Agent {i + 1}",
            )
            self.agents.append(agent)

    async def _run_round(
        self,
        round_num: int,
        problem: str,
        context: dict[str, Any] | None,
    ) -> DebateRound:
        """Run a single round of debate.

        Args:
            round_num: Round number
            problem: Problem being debated
            context: Optional context

        Returns:
            Debate round result

        """
        debate_round = DebateRound(round_number=round_num)

        active_agents = [a for a in self.agents if a.active]

        # Each agent proposes/refines their position
        for agent in active_agents:
            if round_num == 1:
                # First round: generate initial position
                position = await self._generate_initial_position(agent, problem, context)
            else:
                # Subsequent rounds: refine based on RCR
                position = await self._refine_position(agent, problem, context)

            agent.current_position = position
            debate_round.agent_positions[agent.id] = position

        # Each agent reflects on their position
        for agent in active_agents:
            reflection = await self.rcr.reflect(agent.current_position, context)
            debate_round.reflections[agent.id] = reflection
            agent.confidence = reflection.confidence

        # Each agent critiques others (up to 2 peers)
        for agent in active_agents:
            critiques = []
            peers = [a for a in active_agents if a.id != agent.id][:2]

            for peer in peers:
                critique = await self.rcr.critique(
                    {"id": peer.id, "persona": peer.persona, "solution": peer.current_position},
                    context,
                )
                critiques.append(critique)

            debate_round.critiques[agent.id] = critiques

        # Calculate consensus
        debate_round.consensus_score = self._calculate_consensus(active_agents)

        return debate_round

    async def _generate_initial_position(
        self,
        agent: DebateAgent,
        problem: str,
        context: dict[str, Any] | None,
    ) -> str:
        """Generate initial position for an agent."""
        # Placeholder - would use LLM with agent persona in production
        return f"{agent.persona}'s position on: {problem}"

    async def _refine_position(
        self,
        agent: DebateAgent,
        problem: str,
        context: dict[str, Any] | None,
    ) -> str:
        """Refine agent's position using RCR."""
        # Get last round's reflection and critiques
        if not self.rounds:
            return await self._generate_initial_position(agent, problem, context)

        last_round = self.rounds[-1]
        reflection = last_round.reflections.get(agent.id)
        critiques = last_round.critiques.get(agent.id, [])

        # Use RCR to refine
        refinement = await self.rcr.refine(agent.current_position, reflection, critiques, context)

        return refinement.refined_answer

    def _calculate_consensus(self, agents: list[DebateAgent]) -> float:
        """Calculate consensus score among agents.

        Args:
            agents: Active agents

        Returns:
            Consensus score (0-1)

        """
        if not agents:
            return 0.0

        # Simple heuristic: average confidence weighted by agreement
        # In production, would use semantic similarity of positions
        avg_confidence = sum(a.confidence for a in agents) / len(agents)

        # Penalize if agents are too far apart
        confidence_variance = sum((a.confidence - avg_confidence) ** 2 for a in agents) / len(
            agents,
        )

        consensus = avg_confidence * (1 - min(confidence_variance, 0.5))
        return consensus

    def _prune_low_confidence_agents(self, threshold: float = 0.3):
        """Remove agents with very low confidence."""
        for agent in self.agents:
            if agent.confidence < threshold:
                agent.active = False

    async def _synthesize_consensus(self) -> str:
        """Synthesize final consensus answer from all rounds."""
        if not self.rounds:
            return "No consensus reached"

        # Get final positions from active agents
        active_agents = [a for a in self.agents if a.active]
        if not active_agents:
            return "All agents dropped out"

        # Placeholder - would use LLM to synthesize in production
        final_round = self.rounds[-1]
        positions = [
            f"{agent.persona}: {final_round.agent_positions.get(agent.id, 'N/A')}"
            for agent in active_agents
        ]

        return f"Consensus from {len(active_agents)} agents:\n" + "\n".join(positions)

    def get_debate_summary(self) -> str:
        """Get a summary of the debate."""
        lines = [
            "Multi-Agent Debate Summary",
            f"Rounds: {len(self.rounds)}",
            f"Active agents: {len([a for a in self.agents if a.active])}",
            f"Final consensus: {self.rounds[-1].consensus_score:.2%}"
            if self.rounds
            else "No rounds completed",
            "",
            "Round by round:",
        ]

        for r in self.rounds:
            lines.append(f"  Round {r.round_number}: Consensus {r.consensus_score:.2%}")

        return "\n".join(lines)


class PanelGPT(MultiAgentDebate):
    """PanelGPT: Expert panel simulation.

    A specialized MAD variant where agents act as domain experts in a panel discussion.
    """

    def __init__(self, expert_domains: list[str] | None = None, **kwargs):
        """Initialize PanelGPT.

        Args:
            expert_domains: Domains for each expert
            **kwargs: Arguments for MultiAgentDebate

        """
        super().__init__(**kwargs)
        self.expert_domains = expert_domains or ["Technical", "Business", "User Experience"]

    async def debate(
        self,
        problem: str,
        personas: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Conduct expert panel discussion.

        Args:
            problem: Problem for panel to discuss
            personas: Optional personas (will use expert domains if not provided)
            context: Optional context

        Returns:
            Panel discussion results

        """
        # Use expert domains as personas if not provided
        if not personas:
            personas = [f"{domain} Expert" for domain in self.expert_domains]

        result = await super().debate(problem, personas, context)
        result["metadata"]["method"] = "panel_gpt"
        result["metadata"]["expert_domains"] = self.expert_domains

        return result
