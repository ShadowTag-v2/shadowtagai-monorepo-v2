# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Multi-Agent Debate (MAD)

Multiple agents debate a problem until consensus.
Reduces hallucinations, improves accuracy through critique.

Philosophy: Iron sharpens iron. Debate > monologue.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class AgentRole(StrEnum):
    """Predefined agent roles for debates."""

    OPTIMIST = "optimist"  # Sees opportunities
    SKEPTIC = "skeptic"  # Questions assumptions
    PRAGMATIST = "pragmatist"  # Balances both
    DOMAIN_EXPERT = "domain_expert"  # Deep expertise
    GENERALIST = "generalist"  # Broad perspective


class DebateRound(BaseModel):
    """Single round of multi-agent debate."""

    round_number: int
    agent_responses: dict[str, str] = Field(description="agent_id -> response")
    critiques: dict[str, list[str]] = Field(
        default_factory=dict,
        description="agent_id -> list of critiques",
    )
    consensus_reached: bool = False


class MADResult(BaseModel):
    """Result of multi-agent debate."""

    rounds: list[DebateRound]
    consensus: str
    winning_argument: str | None = None
    total_rounds: int
    agents: dict[str, str] = Field(description="agent_id -> role")
    metadata: dict = Field(default_factory=dict)


class MultiAgentDebate:
    """Multi-Agent Debate engine.

    Usage:
        >>> mad = MultiAgentDebate(agents=3, rounds=5, strategy="RCR")
        >>> result = mad.solve("Should we use microservices or monolith?")
        >>> print(result.consensus)

    Research shows:
        - 3-5 agents optimal (more = diminishing returns)
        - 5-10% accuracy boost over single model
        - Reduces sycophancy (agents blindly agreeing)
        - Best for:
          * Complex decisions with trade-offs
          * Problems with multiple valid approaches
          * Scenarios requiring diverse expertise
    """

    def __init__(
        self,
        agents: int = 3,
        rounds: int = 5,
        strategy: Literal["vanilla", "RCR", "vote"] = "RCR",
        consensus_threshold: float = 0.67,
        roles: list[AgentRole] | None = None,
    ) -> None:
        """Initialize multi-agent debate.

        Args:
            agents: Number of agents (3-5 recommended)
            rounds: Max debate rounds
            strategy: Debate strategy (RCR = reflect-critique-refine)
            consensus_threshold: Agreement level to stop (0.67 = 2/3 majority)
            roles: Optional specific roles for each agent

        """
        self.agents = agents
        self.rounds = rounds
        self.strategy = strategy
        self.consensus_threshold = consensus_threshold
        self.roles = roles or [AgentRole.GENERALIST] * agents

    def format_prompt(
        self,
        problem: str,
        agent_id: str,
        role: AgentRole,
        round_num: int,
        previous_responses: dict[str, str] | None = None,
    ) -> str:
        """Generate prompt for a single agent in the debate."""
        prompt = f"""You are Agent {agent_id} in a multi-agent debate.

Your role: {role.value}

Problem to solve:
{problem}

Debate round: {round_num}/{self.rounds}
Strategy: {self.strategy}"""

        if previous_responses and round_num > 1:
            prompt += "\n\nOther agents' responses:\n"
            for other_id, response in previous_responses.items():
                if other_id != agent_id:
                    prompt += f"\nAgent {other_id}:\n{response}\n"

            if self.strategy == "RCR":
                prompt += """
REFLECT on other agents' arguments:
- What are their strongest points?
- Where might they be wrong?

CRITIQUE:
- Specific flaws in reasoning
- Unsupported assumptions
- Missing considerations

REFINE your position:
- Build on good ideas from others
- Address the critiques
- Present your improved argument"""

        else:
            prompt += "\n\nProvide your initial analysis and recommendation."

        return prompt.strip()

    def solve(
        self,
        problem: str,
        model: any | None = None,
        temperature: float = 0.7,
    ) -> MADResult:
        """Execute multi-agent debate to solve a problem.

        Args:
            problem: The problem/question to debate
            model: Optional model instance
            temperature: Sampling temperature (higher = more diverse opinions)

        Returns:
            MADResult with consensus and debate history

        """
        try:
            from ultrathink.llm import LLMExecutor

            executor = model or LLMExecutor()

            rounds_history = []
            previous_responses = {}

            for round_num in range(1, self.rounds + 1):
                agent_responses = {}

                # Each agent generates response
                for i, role in enumerate(self.roles[: self.agents]):
                    agent_id = f"agent_{i + 1}"
                    prompt = self.format_prompt(
                        problem,
                        agent_id,
                        role,
                        round_num,
                        previous_responses,
                    )

                    llm_response = executor.execute(prompt, temperature=temperature)
                    agent_responses[agent_id] = llm_response.content

                # Check for consensus (simple majority voting)
                consensus_reached = self._check_consensus(agent_responses)

                rounds_history.append(
                    DebateRound(
                        round_number=round_num,
                        agent_responses=agent_responses,
                        consensus_reached=consensus_reached,
                    ),
                )

                previous_responses = agent_responses

                if consensus_reached:
                    break

            # Synthesize final consensus
            final_prompt = "Based on this debate:\n\n"
            for agent_id, response in agent_responses.items():
                final_prompt += f"{agent_id}: {response}\n\n"
            final_prompt += "\nProvide a synthesized consensus in 2-3 sentences:"

            consensus_response = executor.execute(final_prompt, temperature=0.3)

            result = MADResult(
                rounds=rounds_history,
                consensus=consensus_response.content,
                total_rounds=len(rounds_history),
                agents={f"agent_{i + 1}": role.value for i, role in enumerate(self.roles)},
                metadata={
                    "technique": "MAD",
                    "strategy": self.strategy,
                    "num_agents": self.agents,
                    "max_rounds": self.rounds,
                },
            )

        except Exception as e:
            result = MADResult(
                rounds=[],
                consensus=f"Error in debate: {e}",
                total_rounds=0,
                agents={},
                metadata={"error": str(e)},
            )

        return result

    def _check_consensus(self, responses: dict[str, str]) -> bool:
        """Check if agents have reached consensus (simple heuristic)."""
        if len(responses) < 2:
            return False

        # Simple check: if responses are similar in conclusion
        # In production, would use more sophisticated NLP
        values = list(responses.values())
        first = values[0].lower()

        agreements = sum(
            1 for v in values[1:] if any(word in v.lower() for word in first.split()[:10])
        )
        return agreements / len(values) >= self.consensus_threshold

    def __repr__(self) -> str:
        return (
            f"MultiAgentDebate(agents={self.agents}, rounds={self.rounds}, "
            f"strategy={self.strategy!r})"
        )
