# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - PanelGPT Debate Circle

Multi-agent system for collaborative debate and consensus building.
"""

from typing import List, Dict, Any, Optional
from ..core.types import DebateMessage, DebateResult, AgentContext, UltrathinkConfig


class PanelGPTDebate:
    """
    PanelGPT Debate Circle

    Assembles expert personas who debate, critique, and converge on solutions.
    Best for: Strategic decisions, broad input needed, interdisciplinary problems.
    """

    def __init__(self, config: UltrathinkConfig | None = None):
        self.config = config or UltrathinkConfig()
        self.experts = self._initialize_experts()

    def _initialize_experts(self) -> list[dict[str, Any]]:
        """Initialize expert personas."""
        return [
            {"name": "Alice", "role": "Optimist", "perspective": "Sees opportunity and upside", "bias": "Positive, growth-oriented"},
            {"name": "Bob", "role": "Skeptic", "perspective": "Challenges assumptions, points out risks", "bias": "Critical, risk-aware"},
            {"name": "Carol", "role": "Pragmatist", "perspective": "Focuses on feasibility and ROI", "bias": "Practical, execution-focused"},
            {"name": "David", "role": "Moderator", "perspective": "Guides discussion and summarizes", "bias": "Neutral, synthesis-oriented"},
        ]

    async def debate(self, context: AgentContext, rounds: int = 3) -> DebateResult:
        """
        Conduct panel debate.

        Args:
            context: Problem context
            rounds: Number of debate rounds

        Returns:
            DebateResult with transcript and consensus
        """
        transcript = []
        problem = context.task

        for round_num in range(1, rounds + 1):
            # Each expert contributes
            for expert in self.experts:
                if expert["role"] == "Moderator" and round_num < rounds:
                    continue  # Moderator speaks last in final round

                message = self._generate_expert_response(expert=expert, problem=problem, round_num=round_num, previous_messages=transcript)

                transcript.append(message)

        # Final moderation
        consensus = self._synthesize_consensus(transcript)
        dissenting_views = self._identify_dissent(transcript)
        confidence = self._assess_debate_confidence(transcript, consensus)

        return DebateResult(
            transcript=transcript,
            consensus=consensus,
            dissenting_views=dissenting_views,
            confidence=confidence,
            final_solution=consensus,
            judge_assessment="Debate concluded with consensus",
        )

    def _generate_expert_response(
        self, expert: dict[str, Any], problem: str, round_num: int, previous_messages: list[DebateMessage]
    ) -> DebateMessage:
        """Generate expert's contribution to debate."""
        # In real implementation, this would use LLM with expert's system prompt
        content = f"{expert['name']} ({expert['role']}): Contributing {expert['perspective']}"

        return DebateMessage(
            agent_name=expert["name"],
            role=expert["role"],
            content=content,
            round_number=round_num,
            challenges=["Challenge point 1"],
            agreements=["Agreement point 1"],
        )

    def _synthesize_consensus(self, transcript: list[DebateMessage]) -> str:
        """Synthesize consensus from debate transcript."""
        return "Consensus solution based on panel debate"

    def _identify_dissent(self, transcript: list[DebateMessage]) -> list[str]:
        """Identify dissenting views."""
        return []  # No dissent if consensus reached

    def _assess_debate_confidence(self, transcript: list[DebateMessage], consensus: str) -> float:
        """Assess confidence in the consensus."""
        return 0.85  # High confidence if consensus reached
