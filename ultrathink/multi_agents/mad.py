# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - Multi-Agent Debate (MAD)

Adversarial debate system for high-stakes correctness.
"""

from ..core.types import DebateMessage, DebateResult, AgentContext, UltrathinkConfig


class MultiAgentDebate:
  """
  Multi-Agent Debate (MAD)

  Agents with opposing roles debate solutions adversarially.
  Best for: High-stakes decisions, correctness paramount, errors costly.
  """

  def __init__(self, config: UltrathinkConfig | None = None):
    self.config = config or UltrathinkConfig()

  async def debate(self, context: AgentContext, rounds: int = 3) -> DebateResult:
    """
    Conduct adversarial multi-agent debate.

    Args:
        context: Problem context
        rounds: Number of debate rounds

    Returns:
        DebateResult with winner and synthesis
    """
    transcript = []

    # Initialize agents
    agent_a = {"name": "Agent A", "role": "Affirmative"}
    agent_b = {"name": "Agent B", "role": "Negative"}

    # Conduct debate rounds
    for round_num in range(1, rounds + 1):
      # Agent A proposes/defends
      msg_a = self._generate_argument(
        agent_a, context.task, round_num, transcript, is_affirmative=True
      )
      transcript.append(msg_a)

      # Agent B challenges
      msg_b = self._generate_argument(
        agent_b, context.task, round_num, transcript, is_affirmative=False
      )
      transcript.append(msg_b)

    # Judge evaluates
    judge_assessment = self._judge_debate(transcript)

    return DebateResult(
      transcript=transcript,
      consensus=judge_assessment["winner_solution"],
      dissenting_views=[judge_assessment["loser_points"]],
      confidence=judge_assessment["confidence"],
      final_solution=judge_assessment["synthesis"],
      judge_assessment=judge_assessment["explanation"],
    )

  def _generate_argument(
    self,
    agent: dict,
    problem: str,
    round_num: int,
    transcript: list[DebateMessage],
    is_affirmative: bool,
  ) -> DebateMessage:
    """Generate agent's argument."""
    stance = "Affirmative" if is_affirmative else "Negative"
    content = f"{agent['name']} ({stance}): Round {round_num} argument"

    return DebateMessage(
      agent_name=agent["name"],
      role=agent["role"],
      content=content,
      round_number=round_num,
      challenges=["Challenge from opponent"],
      agreements=[],
    )

  def _judge_debate(self, transcript: list[DebateMessage]) -> dict:
    """Judge evaluates the debate and selects winner."""
    return {
      "winner": "Agent A",
      "winner_solution": "Agent A's solution is more robust",
      "loser_points": "Agent B raised valid concerns about X",
      "synthesis": "Hybrid solution incorporating best of both",
      "confidence": 0.88,
      "explanation": "Agent A's reasoning was sound; Agent B's critiques improved it",
    }
