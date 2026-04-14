"""MAD (Multi-Agent Debate) Orchestrator

Implements multi-agent debate pattern (PanelGPT) for reaching consensus
through structured argumentation between 3-5 specialized agents.

Key Features:
- 3-5 agent debates: Multiple perspectives on problem
- Consensus scoring: Agreement measurement across agents
- 3-5 debate rounds: Iterative refinement with critique
- Glicko-2 integration: Track agent performance over time
- Per-round latency: ~2-5s (depending on agent count)
- Total debate time: ~10-25s
- Consensus confidence: ≥80% target

References:
- "Improving Factuality and Reasoning in Language Models through Multiagent Debate"
- "PanelGPT: A Generative AI Ensemble Framework"
- "Constitutional AI: Harmlessness from AI Feedback"

"""

import asyncio
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pnkln.core.glicko_rating import GlickoEngine, GlickoRating, MatchOutcome


class AgentRole(Enum):
    """Agent roles in debate."""

    PROPOSER = "proposer"  # Proposes initial solution
    CRITIC = "critic"  # Critiques proposals
    SYNTHESIZER = "synthesizer"  # Synthesizes consensus
    SPECIALIST = "specialist"  # Domain-specific expert
    MODERATOR = "moderator"  # Guides debate flow


@dataclass
class AgentProfile:
    """Agent profile for debate participation.

    Attributes:
        agent_id: Unique agent identifier
        role: Agent role in debate
        expertise: Domain expertise description
        glicko_rating: Glicko-2 rating (optional)
        persona: Persona description for prompting
        debate_count: Total debates participated in

    """

    agent_id: str
    role: AgentRole
    expertise: str
    glicko_rating: GlickoRating | None = None
    persona: str = ""
    debate_count: int = 0


@dataclass
class DebatePosition:
    """Single agent's position in debate.

    Attributes:
        agent_id: Agent identifier
        round_number: Debate round (1-indexed)
        position: Position statement
        reasoning: Supporting reasoning
        confidence: Confidence score (0.0-1.0)
        critiques: Critiques of other positions
        timestamp: Position timestamp

    """

    agent_id: str
    round_number: int
    position: str
    reasoning: str
    confidence: float
    critiques: list[tuple[str, str]] = field(default_factory=list)  # (target_agent_id, critique)
    timestamp: float = field(default_factory=time.time)


@dataclass
class DebateRound:
    """Single debate round results.

    Attributes:
        round_number: Round number (1-indexed)
        positions: All positions in this round
        consensus_score: Consensus level (0.0-1.0)
        avg_confidence: Average agent confidence
        disagreements: Major disagreement points
        execution_time_ms: Round execution time

    """

    round_number: int
    positions: list[DebatePosition]
    consensus_score: float
    avg_confidence: float
    disagreements: list[str] = field(default_factory=list)
    execution_time_ms: float = 0.0


@dataclass
class DebateResult:
    """Complete debate result.

    Attributes:
        topic: Debate topic/question
        participating_agents: List of agent IDs
        rounds: All debate rounds
        final_consensus: Final consensus statement
        final_confidence: Final consensus confidence
        consensus_reached: Whether consensus threshold was met
        total_execution_time_ms: Total debate time
        winning_agent_id: Agent with best-rated position (optional)

    """

    topic: str
    participating_agents: list[str]
    rounds: list[DebateRound]
    final_consensus: str
    final_confidence: float
    consensus_reached: bool
    total_execution_time_ms: float
    winning_agent_id: str | None = None


class MADOrchestrator:
    """Multi-Agent Debate Orchestrator.

    Performance targets:
    - Per-round latency: ~2-5s (depending on agent count)
    - Total debate time: ~10-25s (3-5 rounds)
    - Consensus confidence: ≥80%
    """

    def __init__(
        self,
        glicko_engine: GlickoEngine | None = None,
        consensus_threshold: float = 0.80,
        max_rounds: int = 5,
        min_rounds: int = 3,
    ):
        """Initialize MAD orchestrator.

        Args:
            glicko_engine: Optional Glicko-2 engine for rating tracking
            consensus_threshold: Minimum consensus to terminate early (0.80 = 80%)
            max_rounds: Maximum debate rounds
            min_rounds: Minimum debate rounds

        """
        self.glicko_engine = glicko_engine or GlickoEngine()
        self.consensus_threshold = consensus_threshold
        self.max_rounds = max_rounds
        self.min_rounds = min_rounds

        # Agent registry
        self.agents: dict[str, AgentProfile] = {}

    def register_agent(
        self, agent_id: str, role: AgentRole, expertise: str, persona: str = "",
    ) -> AgentProfile:
        """Register agent for debate participation.

        Args:
            agent_id: Unique agent identifier
            role: Agent role
            expertise: Domain expertise
            persona: Persona description

        Returns:
            Created agent profile

        """
        # Get Glicko rating from engine
        glicko_rating = self.glicko_engine.get_rating(agent_id)

        profile = AgentProfile(
            agent_id=agent_id,
            role=role,
            expertise=expertise,
            glicko_rating=glicko_rating,
            persona=persona,
        )

        self.agents[agent_id] = profile
        return profile

    def _compute_consensus_score(self, positions: list[DebatePosition]) -> float:
        """Compute consensus score from agent positions.

        Uses agreement in confidence levels and position similarity.
        In production, would use semantic similarity (embeddings).

        Args:
            positions: All positions in round

        Returns:
            Consensus score (0.0-1.0, higher = more agreement)

        """
        if len(positions) < 2:
            return 1.0  # Single agent = perfect consensus

        # Measure 1: Confidence variance (low variance = high consensus)
        confidences = [p.confidence for p in positions]
        confidence_stdev = statistics.stdev(confidences)
        confidence_consensus = max(0.0, 1.0 - confidence_stdev)

        # Measure 2: Average confidence (high confidence = strong consensus)
        avg_confidence = statistics.mean(confidences)

        # Measure 3: Critique count (fewer critiques = more agreement)
        total_critiques = sum(len(p.critiques) for p in positions)
        max_possible_critiques = len(positions) * (len(positions) - 1)
        critique_ratio = total_critiques / max(1, max_possible_critiques)
        critique_consensus = max(0.0, 1.0 - critique_ratio)

        # Weighted average
        consensus = 0.3 * confidence_consensus + 0.4 * avg_confidence + 0.3 * critique_consensus

        return min(1.0, max(0.0, consensus))

    def _find_disagreements(self, positions: list[DebatePosition]) -> list[str]:
        """Identify major disagreement points from critiques.

        Args:
            positions: All positions in round

        Returns:
            List of disagreement descriptions

        """
        disagreements = []

        # Collect all critiques
        all_critiques = []
        for pos in positions:
            for target_id, critique in pos.critiques:
                all_critiques.append((pos.agent_id, target_id, critique))

        # Group by common themes (simplified - would use clustering in production)
        if len(all_critiques) > 2:
            disagreements.append(f"{len(all_critiques)} critiques raised across positions")

        # Identify low-confidence positions
        low_confidence = [p for p in positions if p.confidence < 0.5]
        if low_confidence:
            disagreements.append(f"{len(low_confidence)} agents have low confidence (<0.5)")

        return disagreements

    async def _get_agent_position(
        self,
        agent: AgentProfile,
        topic: str,
        round_number: int,
        previous_positions: list[DebatePosition],
        position_generator: Callable[[str, str, int, list[DebatePosition]], tuple[str, str, float]],
    ) -> DebatePosition:
        """Get agent's position for current round.

        Args:
            agent: Agent profile
            topic: Debate topic
            round_number: Current round number
            previous_positions: Positions from previous rounds
            position_generator: Function to generate (position, reasoning, confidence)

        Returns:
            Agent's debate position

        """
        # Generate position
        position, reasoning, confidence = await position_generator(
            agent.agent_id, topic, round_number, previous_positions,
        )

        # Generate critiques of other agents' latest positions
        critiques = []
        if round_number > 1:
            # Get latest position from each other agent
            latest_by_agent = {}
            for prev_pos in reversed(previous_positions):
                if prev_pos.agent_id not in latest_by_agent and prev_pos.agent_id != agent.agent_id:
                    latest_by_agent[prev_pos.agent_id] = prev_pos

            # Generate critiques (simplified - would use LLM in production)
            for other_id, other_pos in latest_by_agent.items():
                if other_pos.confidence < confidence - 0.2:
                    critiques.append(
                        (
                            other_id,
                            f"Position lacks sufficient confidence (only {other_pos.confidence:.0%})",
                        ),
                    )

        return DebatePosition(
            agent_id=agent.agent_id,
            round_number=round_number,
            position=position,
            reasoning=reasoning,
            confidence=confidence,
            critiques=critiques,
        )

    async def _run_round(
        self,
        round_number: int,
        topic: str,
        agents: list[AgentProfile],
        previous_positions: list[DebatePosition],
        position_generator: Callable[[str, str, int, list[DebatePosition]], tuple[str, str, float]],
    ) -> DebateRound:
        """Run single debate round.

        Args:
            round_number: Round number
            topic: Debate topic
            agents: Participating agents
            previous_positions: All previous positions
            position_generator: Position generation function

        Returns:
            Debate round results

        """
        start_time = time.time()

        # Get positions from all agents in parallel
        position_tasks = [
            self._get_agent_position(
                agent, topic, round_number, previous_positions, position_generator,
            )
            for agent in agents
        ]
        positions = await asyncio.gather(*position_tasks)

        # Compute consensus
        consensus_score = self._compute_consensus_score(positions)
        avg_confidence = statistics.mean(p.confidence for p in positions)
        disagreements = self._find_disagreements(positions)

        execution_time_ms = (time.time() - start_time) * 1000

        return DebateRound(
            round_number=round_number,
            positions=positions,
            consensus_score=consensus_score,
            avg_confidence=avg_confidence,
            disagreements=disagreements,
            execution_time_ms=execution_time_ms,
        )

    def _synthesize_consensus(self, rounds: list[DebateRound]) -> tuple[str, float]:
        """Synthesize final consensus from all rounds.

        Args:
            rounds: All debate rounds

        Returns:
            Tuple of (consensus_statement, confidence)

        """
        if not rounds:
            return ("No consensus reached (no rounds)", 0.0)

        # Get final round positions
        final_round = rounds[-1]

        # Find highest-confidence position in final round
        best_position = max(final_round.positions, key=lambda p: p.confidence)

        # Synthesize consensus (simplified - would use LLM in production)
        consensus = f"{best_position.position}\n\nReasoning: {best_position.reasoning}"

        # Consensus confidence is weighted average of:
        # - Final round consensus score (40%)
        # - Best position confidence (40%)
        # - Average confidence across final round (20%)
        confidence = (
            0.4 * final_round.consensus_score
            + 0.4 * best_position.confidence
            + 0.2 * final_round.avg_confidence
        )

        return (consensus, confidence)

    def _update_ratings(self, rounds: list[DebateRound], winning_agent_id: str):
        """Update Glicko-2 ratings based on debate performance.

        Args:
            rounds: All debate rounds
            winning_agent_id: Agent with best final position

        """
        if not self.glicko_engine:
            return

        # Get all participating agents
        all_agents = set()
        for round_data in rounds:
            for pos in round_data.positions:
                all_agents.add(pos.agent_id)

        # Record matches: winner vs all others
        for agent_id in all_agents:
            if agent_id != winning_agent_id:
                self.glicko_engine.record_match(winning_agent_id, agent_id, MatchOutcome.WIN)

    async def debate(
        self,
        topic: str,
        agent_ids: list[str],
        position_generator: Callable[[str, str, int, list[DebatePosition]], tuple[str, str, float]],
    ) -> DebateResult:
        """Run multi-agent debate to reach consensus.

        Args:
            topic: Debate topic/question
            agent_ids: List of agent IDs to participate (3-5 agents recommended)
            position_generator: Async function that generates agent positions
                Signature: (agent_id, topic, round_number, previous_positions) -> (position, reasoning, confidence)

        Returns:
            Complete debate result

        """
        start_time = time.time()

        # Validate agents
        agents = []
        for agent_id in agent_ids:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not registered. Call register_agent() first.")
            agents.append(self.agents[agent_id])

        if len(agents) < 3:
            raise ValueError(f"Minimum 3 agents required for debate (got {len(agents)})")

        if len(agents) > 5:
            raise ValueError(f"Maximum 5 agents recommended for debate (got {len(agents)})")

        # Debate loop
        rounds: list[DebateRound] = []
        all_positions: list[DebatePosition] = []

        for round_num in range(1, self.max_rounds + 1):
            # Run round
            round_result = await self._run_round(
                round_num, topic, agents, all_positions, position_generator,
            )

            rounds.append(round_result)
            all_positions.extend(round_result.positions)

            # Check for early consensus
            if round_num >= self.min_rounds:
                if round_result.consensus_score >= self.consensus_threshold:
                    break  # Consensus reached

        # Synthesize final consensus
        final_consensus, final_confidence = self._synthesize_consensus(rounds)
        consensus_reached = final_confidence >= self.consensus_threshold

        # Determine winning agent (highest final confidence)
        final_positions = rounds[-1].positions if rounds else []
        winning_agent_id = None
        if final_positions:
            winner_position = max(final_positions, key=lambda p: p.confidence)
            winning_agent_id = winner_position.agent_id

        # Update Glicko-2 ratings
        if winning_agent_id:
            self._update_ratings(rounds, winning_agent_id)

        # Update agent debate counts
        for agent in agents:
            agent.debate_count += 1

        total_time_ms = (time.time() - start_time) * 1000

        return DebateResult(
            topic=topic,
            participating_agents=agent_ids,
            rounds=rounds,
            final_consensus=final_consensus,
            final_confidence=final_confidence,
            consensus_reached=consensus_reached,
            total_execution_time_ms=total_time_ms,
            winning_agent_id=winning_agent_id,
        )

    def get_leaderboard(
        self, top_n: int | None = None,
    ) -> list[tuple[str, AgentProfile, GlickoRating]]:
        """Get agent leaderboard based on Glicko-2 ratings.

        Args:
            top_n: Return only top N agents (None = all)

        Returns:
            List of (agent_id, profile, rating) tuples

        """
        leaderboard = []

        for agent_id, profile in self.agents.items():
            rating = self.glicko_engine.get_rating(agent_id)
            leaderboard.append((agent_id, profile, rating))

        # Sort by conservative rating (rating - 2*RD)
        leaderboard.sort(key=lambda x: x[2].rating - 2 * x[2].rd, reverse=True)

        if top_n is not None:
            leaderboard = leaderboard[:top_n]

        return leaderboard

    def get_statistics(self) -> dict[str, Any]:
        """Get orchestrator statistics.

        Returns:
            Dictionary with statistics

        """
        total_debates = sum(agent.debate_count for agent in self.agents.values())

        glicko_stats = self.glicko_engine.get_statistics()

        return {
            "total_agents": len(self.agents),
            "total_debates": total_debates,
            "consensus_threshold": self.consensus_threshold,
            "max_rounds": self.max_rounds,
            "min_rounds": self.min_rounds,
            "glicko_stats": glicko_stats,
        }
