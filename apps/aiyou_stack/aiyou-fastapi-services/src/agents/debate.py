"""PanelGPT/MAD (Multi-Agent Debate) framework.

Multiple agents debate a problem, refining solutions through iteration.
Inspired by "Improving Factuality and Reasoning in LLMs with Multi-Agent Debate".
"""

from pydantic import BaseModel, Field

from app.agents.base import Agent, AgentConfig


class DebateRound(BaseModel):
    """Single round of multi-agent debate."""

    round_number: int
    agents: list[str]  # Agent names participating
    arguments: dict[str, str]  # agent_name -> argument
    consensus_score: float = Field(ge=0.0, le=1.0)


class DebateResult(BaseModel):
    """Result of multi-agent debate."""

    question: str
    rounds: list[DebateRound]
    final_answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    participants: list[str]


class DebateAgent(Agent):
    """Agent capable of participating in multi-agent debates.

    Uses MAD (Multi-Agent Debate) framework:
    1. Each agent proposes initial answer
    2. Agents read others' answers and revise
    3. Iterate until consensus or max rounds
    4. Aggregate final answers
    """

    def __init__(self, config: AgentConfig, persona: str | None = None):
        super().__init__(config)
        self.persona = persona or "A critical thinker who challenges assumptions"

    async def propose_initial_answer(self, question: str) -> str:
        """Propose initial answer to question."""
        # In production, this would call LLM
        return f"[{self.config.name}] Initial answer to: {question}"

    async def revise_answer(
        self,
        question: str,
        own_answer: str,
        others_answers: list[str],
    ) -> str:
        """Revise answer based on others' arguments."""
        # In production, this would call LLM with all answers as context
        return f"[{self.config.name}] Revised after seeing: {len(others_answers)} other views"

    async def execute(self, question: str) -> str:
        """Execute debate participation (single agent view)."""
        return await self.propose_initial_answer(question)


class DebateOrchestrator:
    """Orchestrates multi-agent debates using MAD framework.

    Process:
    1. Round 1: Each agent proposes initial answer
    2. Round 2-N: Agents revise based on others' answers
    3. Final: Aggregate answers (voting, consensus, or best-rated)
    """

    def __init__(
        self,
        agents: list[DebateAgent],
        max_rounds: int = 3,
        consensus_threshold: float = 0.8,
    ):
        self.agents = agents
        self.max_rounds = max_rounds
        self.consensus_threshold = consensus_threshold

    async def run_debate(self, question: str) -> DebateResult:
        """Run full multi-agent debate.

        Args:
            question: Question to debate

        Returns:
            DebateResult with rounds and final answer

        """
        rounds: list[DebateRound] = []
        current_answers: dict[str, str] = {}

        # Round 1: Initial proposals
        for agent in self.agents:
            answer = await agent.propose_initial_answer(question)
            current_answers[agent.config.name] = answer

        rounds.append(
            DebateRound(
                round_number=1,
                agents=[a.config.name for a in self.agents],
                arguments=current_answers.copy(),
                consensus_score=self._calculate_consensus(list(current_answers.values())),
            ),
        )

        # Rounds 2-N: Revisions
        for round_num in range(2, self.max_rounds + 1):
            new_answers: dict[str, str] = {}

            for agent in self.agents:
                own_answer = current_answers[agent.config.name]
                others = [ans for name, ans in current_answers.items() if name != agent.config.name]

                revised = await agent.revise_answer(question, own_answer, others)
                new_answers[agent.config.name] = revised

            consensus = self._calculate_consensus(list(new_answers.values()))

            rounds.append(
                DebateRound(
                    round_number=round_num,
                    agents=[a.config.name for a in self.agents],
                    arguments=new_answers.copy(),
                    consensus_score=consensus,
                ),
            )

            current_answers = new_answers

            # Early stopping if consensus reached
            if consensus >= self.consensus_threshold:
                break

        # Aggregate final answer
        final_answer = self._aggregate_answers(current_answers)
        confidence = rounds[-1].consensus_score

        return DebateResult(
            question=question,
            rounds=rounds,
            final_answer=final_answer,
            confidence=confidence,
            participants=[a.config.name for a in self.agents],
        )

    def _calculate_consensus(self, answers: list[str]) -> float:
        """Calculate consensus score among answers.

        In production, use semantic similarity or agreement metrics.
        """
        # Placeholder: would use embeddings similarity in production
        if not answers:
            return 0.0

        # Simple heuristic: if all answers similar length, assume some consensus
        lengths = [len(a) for a in answers]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)

        # Normalize variance to [0, 1] score
        consensus = max(0.0, min(1.0, 1.0 - variance / (avg_len**2 + 1)))
        return consensus

    def _aggregate_answers(self, answers: dict[str, str]) -> str:
        """Aggregate final answers from all agents.

        Strategies:
        - Voting (if multiple choice)
        - Consensus (if high agreement)
        - Best-rated agent's answer (using Glicko-2)
        """
        # Strategy: Return highest-rated agent's answer
        best_agent = max(
            self.agents,
            key=lambda a: a.performance.rating.get_rating(),
        )

        return answers.get(best_agent.config.name, list(answers.values())[0])
