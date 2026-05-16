# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
MAD (Multi-Agent Debates) Consensus System.

Implements multi-agent decision-making with Glicko-weighted voting for
critical decisions where single-provider risk is unacceptable.

Process:
1. Query all providers in parallel (Gemini, Claude, GPT-5)
2. Check for unanimous consensus (fast path)
3. If split, run debate round (agents argue for their positions)
4. Weight votes by Glicko-2 ratings
5. Return majority decision with combined reasoning

Use cases:
- Production deployments (high risk)
- Security approvals (critical)
- Financial transactions (regulated)
- Any decision flagged as "multi_agent_review" by user

This provides:
- Reduced single-provider bias
- Higher confidence through consensus
- Transparency (all reasoning visible)
- Glicko-weighted expertise (best providers matter more)
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionType(Enum):
  """Types of decisions that can be made."""

  APPROVE = "approve"
  REJECT = "reject"
  ESCALATE = "escalate"
  DEFER = "defer"


@dataclass
class AgentVote:
  """A single agent's vote in the MAD process."""

  agent_id: str
  decision: DecisionType
  confidence: float  # 0.0 to 1.0
  reasoning: str
  glicko_rating: float
  latency_ms: float


@dataclass
class DebateRound:
  """Record of a debate round where agents argue for their positions."""

  round_number: int
  initial_votes: list[AgentVote]
  debate_arguments: dict[str, str]  # agent_id -> argument
  concessions: list[str]  # agent_ids that conceded
  final_votes: list[AgentVote]


@dataclass
class MADConsensus:
  """Final consensus result from MAD process."""

  decision: DecisionType
  confidence: float  # Weighted by Glicko ratings
  reasoning: str  # Combined from all agents
  unanimous: bool
  weighted_votes: dict[DecisionType, float]  # Decision -> Glicko-weighted vote count
  individual_votes: list[AgentVote]
  debate_rounds: list[DebateRound]
  total_latency_ms: float


class MADEngine:
  """
  Multi-Agent Debates (MAD) engine for consensus decision-making.

  Orchestrates parallel queries to multiple LLM providers, facilitates
  debate rounds when consensus isn't immediate, and computes Glicko-weighted
  final decisions.
  """

  def __init__(
    self,
    agents: dict[str, Any],  # agent_id -> agent instance
    glicko_ratings: dict[str, float],  # agent_id -> Glicko rating
    max_debate_rounds: int = 2,
    require_unanimity: bool = False,
  ):
    """
    Initialize MAD engine.

    Args:
        agents: Dict mapping agent_id to agent instance (e.g., LLM client)
        glicko_ratings: Dict mapping agent_id to Glicko-2 rating
        max_debate_rounds: Maximum debate rounds before forced consensus
        require_unanimity: If True, continue debating until unanimous
    """
    self.agents = agents
    self.glicko_ratings = glicko_ratings
    self.max_debate_rounds = max_debate_rounds
    self.require_unanimity = require_unanimity

  def reach_consensus(
    self, context: dict[str, Any], timeout_per_agent: float = 2.0
  ) -> MADConsensus:
    """
    Reach consensus on a decision through MAD process.

    Args:
        context: Decision context (user request, policies, etc.)
        timeout_per_agent: Max time per agent query in seconds

    Returns:
        MADConsensus with final decision and reasoning
    """
    start_time = time.time()

    logger.info(f"MAD: Starting consensus process with {len(self.agents)} agents")

    # Round 1: Initial parallel queries
    initial_votes = self._query_agents_parallel(context, timeout_per_agent)

    # Check for unanimous consensus (fast path)
    if self._is_unanimous(initial_votes):
      logger.info("MAD: Unanimous consensus reached immediately")
      return self._build_consensus(
        votes=initial_votes, debate_rounds=[], unanimous=True, start_time=start_time
      )

    # Not unanimous - start debate rounds
    logger.info("MAD: Split decision - starting debate rounds")

    debate_rounds = []
    current_votes = initial_votes

    for round_num in range(1, self.max_debate_rounds + 1):
      logger.info(f"MAD: Debate round {round_num}/{self.max_debate_rounds}")

      # Run debate round
      debate_round = self._run_debate_round(
        round_number=round_num,
        current_votes=current_votes,
        context=context,
        timeout_per_agent=timeout_per_agent,
      )

      debate_rounds.append(debate_round)
      current_votes = debate_round.final_votes

      # Check if unanimous now
      if self._is_unanimous(current_votes):
        logger.info(f"MAD: Unanimous consensus reached after round {round_num}")
        return self._build_consensus(
          votes=current_votes,
          debate_rounds=debate_rounds,
          unanimous=True,
          start_time=start_time,
        )

      # If not requiring unanimity, we can exit early
      if not self.require_unanimity:
        logger.info("MAD: Proceeding with weighted majority (not unanimous)")
        break

    # No unanimity - use Glicko-weighted voting
    logger.info("MAD: Computing Glicko-weighted majority decision")

    return self._build_consensus(
      votes=current_votes,
      debate_rounds=debate_rounds,
      unanimous=False,
      start_time=start_time,
    )

  def _query_agents_parallel(
    self, context: dict[str, Any], timeout: float
  ) -> list[AgentVote]:
    """
    Query all agents in parallel for their initial votes.

    Args:
        context: Decision context
        timeout: Max time per agent in seconds

    Returns:
        List of AgentVote objects
    """
    votes = []

    with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
      # Submit all agent queries
      futures = {}
      for agent_id, agent in self.agents.items():
        future = executor.submit(
          self._query_single_agent, agent_id, agent, context, timeout
        )
        futures[future] = agent_id

      # Collect results
      for future in as_completed(futures):
        agent_id = futures[future]
        try:
          vote = future.result()
          votes.append(vote)
        except Exception as e:
          logger.error(f"MAD: Agent {agent_id} failed: {e}")
          # Create a fallback vote
          votes.append(
            AgentVote(
              agent_id=agent_id,
              decision=DecisionType.DEFER,
              confidence=0.0,
              reasoning=f"Agent failed: {str(e)}",
              glicko_rating=self.glicko_ratings.get(agent_id, 1500),
              latency_ms=timeout * 1000,
            )
          )

    return votes

  def _query_single_agent(
    self, agent_id: str, agent: Any, context: dict[str, Any], timeout: float
  ) -> AgentVote:
    """
    Query a single agent for its decision.

    Args:
        agent_id: Agent identifier
        agent: Agent instance (LLM client)
        context: Decision context
        timeout: Max execution time

    Returns:
        AgentVote
    """
    start = time.time()

    # TODO: Replace with actual agent query
    # For now, simulate agent decision
    import random

    time.sleep(random.uniform(0.05, 0.15))  # Simulate API latency

    # Simulated decision
    decisions = [DecisionType.APPROVE, DecisionType.REJECT, DecisionType.ESCALATE]
    decision = random.choice(decisions)
    confidence = random.uniform(0.7, 0.95)
    reasoning = f"{agent_id} analysis: [simulated reasoning for {decision.value}]"

    latency_ms = (time.time() - start) * 1000

    return AgentVote(
      agent_id=agent_id,
      decision=decision,
      confidence=confidence,
      reasoning=reasoning,
      glicko_rating=self.glicko_ratings.get(agent_id, 1500),
      latency_ms=latency_ms,
    )

  def _is_unanimous(self, votes: list[AgentVote]) -> bool:
    """Check if all votes agree on the same decision."""
    if not votes:
      return False

    first_decision = votes[0].decision
    return all(vote.decision == first_decision for vote in votes)

  def _run_debate_round(
    self,
    round_number: int,
    current_votes: list[AgentVote],
    context: dict[str, Any],
    timeout_per_agent: float,
  ) -> DebateRound:
    """
    Run a single debate round where agents argue for their positions.

    Args:
        round_number: Current round number
        current_votes: Current votes from agents
        context: Original decision context
        timeout_per_agent: Max time per agent

    Returns:
        DebateRound with arguments and updated votes
    """
    logger.info(f"Debate round {round_number}: Agents presenting arguments")

    # Build debate context showing all current positions
    debate_context = {
      **context,
      "debate_round": round_number,
      "current_votes": [
        {
          "agent": vote.agent_id,
          "decision": vote.decision.value,
          "confidence": vote.confidence,
          "reasoning": vote.reasoning,
        }
        for vote in current_votes
      ],
    }

    # Each agent argues for its position or concedes
    debate_arguments = {}
    concessions = []

    for vote in current_votes:
      argument = self._get_agent_argument(
        agent_id=vote.agent_id,
        current_vote=vote,
        other_votes=[v for v in current_votes if v.agent_id != vote.agent_id],
        context=debate_context,
        timeout=timeout_per_agent,
      )

      debate_arguments[vote.agent_id] = argument

      # Check if agent conceded
      if "concede" in argument.lower() or "agree with" in argument.lower():
        concessions.append(vote.agent_id)
        logger.info(f"Debate: {vote.agent_id} conceded")

    # Get updated votes after debate
    final_votes = self._query_agents_parallel(debate_context, timeout_per_agent)

    return DebateRound(
      round_number=round_number,
      initial_votes=current_votes,
      debate_arguments=debate_arguments,
      concessions=concessions,
      final_votes=final_votes,
    )

  def _get_agent_argument(
    self,
    agent_id: str,
    current_vote: AgentVote,
    other_votes: list[AgentVote],
    context: dict[str, Any],
    timeout: float,
  ) -> str:
    """
    Get agent's argument for its position in debate.

    Args:
        agent_id: Agent making argument
        current_vote: Agent's current vote
        other_votes: Other agents' votes
        context: Debate context
        timeout: Max execution time

    Returns:
        Argument string
    """
    # TODO: Replace with actual LLM debate prompt
    # For now, simulate argument

    other_decisions = ", ".join(
      [f"{v.agent_id}={v.decision.value}" for v in other_votes]
    )

    # Simulated argument
    if len(other_votes) == 0:
      return f"{agent_id}: I stand by my decision: {current_vote.decision.value}"

    # Simple logic: if isolated, maybe concede to majority
    majority_decision = max(
      set(v.decision for v in other_votes),
      key=lambda d: sum(1 for v in other_votes if v.decision == d),
    )

    if current_vote.decision != majority_decision:
      # Agent is in minority
      import random

      if random.random() < 0.3:  # 30% chance to concede
        return f"{agent_id}: After reviewing {other_decisions}, I concede to {majority_decision.value}. The majority reasoning is compelling."

    return (
      f"{agent_id}: I maintain my position of {current_vote.decision.value}. "
      f"While I see {other_decisions}, my analysis shows {current_vote.reasoning}"
    )

  def _build_consensus(
    self,
    votes: list[AgentVote],
    debate_rounds: list[DebateRound],
    unanimous: bool,
    start_time: float,
  ) -> MADConsensus:
    """
    Build final MADConsensus from votes and debate history.

    Args:
        votes: Final votes from all agents
        debate_rounds: History of debate rounds
        unanimous: Whether consensus is unanimous
        start_time: Start time of MAD process

    Returns:
        MADConsensus
    """
    # Compute Glicko-weighted votes
    weighted_votes = {}

    for vote in votes:
      decision = vote.decision
      weight = vote.glicko_rating / 1500.0  # Normalize to ~1.0

      if decision not in weighted_votes:
        weighted_votes[decision] = 0.0

      weighted_votes[decision] += weight

    # Winner is decision with highest weight
    winner = max(weighted_votes.items(), key=lambda x: x[1])
    winning_decision = winner[0]
    winning_weight = winner[1]

    # Compute confidence (winning weight / total weight)
    total_weight = sum(weighted_votes.values())
    confidence = winning_weight / total_weight if total_weight > 0 else 0.0

    # Combine reasoning from all agents
    if unanimous:
      # If unanimous, use first agent's reasoning
      reasoning = f"UNANIMOUS: {votes[0].reasoning}"
    else:
      # If not unanimous, show all reasoning
      reasoning = f"WEIGHTED MAJORITY: {winning_decision.value}\n\n"
      reasoning += "Votes:\n"
      for decision, weight in sorted(
        weighted_votes.items(), key=lambda x: x[1], reverse=True
      ):
        reasoning += f"  {decision.value}: {weight:.2f} weight\n"

      reasoning += "\nIndividual reasoning:\n"
      for vote in votes:
        reasoning += f"  {vote.agent_id} ({vote.decision.value}): {vote.reasoning}\n"

    # Total latency
    total_latency_ms = (time.time() - start_time) * 1000

    return MADConsensus(
      decision=winning_decision,
      confidence=confidence,
      reasoning=reasoning,
      unanimous=unanimous,
      weighted_votes=weighted_votes,
      individual_votes=votes,
      debate_rounds=debate_rounds,
      total_latency_ms=total_latency_ms,
    )


# Example usage
if __name__ == "__main__":
  # Simulate 3 agents with different Glicko ratings
  class MockAgent:
    def __init__(self, name):
      self.name = name

  agents = {
    "gemini": MockAgent("Gemini"),
    "claude": MockAgent("Claude"),
    "gpt5": MockAgent("GPT-5"),
  }

  glicko_ratings = {
    "gemini": 1620,  # Highest rated
    "claude": 1580,
    "gpt5": 1540,
  }

  # Create MAD engine
  mad = MADEngine(
    agents=agents,
    glicko_ratings=glicko_ratings,
    max_debate_rounds=2,
    require_unanimity=False,
  )

  # Test scenario: Production deployment decision
  context = {
    "decision_type": "production_deployment",
    "user_request": "Deploy feature X to production",
    "risk_level": "high",
    "tests_passed": True,
    "security_scan": False,  # This will cause split decision
  }

  # Reach consensus
  consensus = mad.reach_consensus(context, timeout_per_agent=1.0)

  # Display results

  for decision, weight in sorted(
    consensus.weighted_votes.items(), key=lambda x: x[1], reverse=True
  ):
    pass

  for vote in consensus.individual_votes:
    pass
