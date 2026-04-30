from pydantic import BaseModel

from src.ultrathink.agents.roster import AgentProfile


class DebateTurn(BaseModel):
    agent_name: str
    content: str
    round: int


class DebateResult(BaseModel):
    topic: str
    rounds: int
    transcript: list[DebateTurn]
    consensus: str


class MultiAgentDebate:
    """Orchestrates a debate between multiple agents to reach a consensus or refined answer."""

    def __init__(self, agents: list[AgentProfile]):
        self.agents = agents
        self.transcript: list[DebateTurn] = []

    def run_debate(self, topic: str, rounds: int = 3) -> DebateResult:
        """Simulates a debate execution.
        Note: In a real system, this would call the LLM for each agent turn.
        For this v0 logic implementation, it constructs the structure.
        """
        self.transcript = []

        # Initial Round
        for agent in self.agents:
            # Context for the agent would include the topic and previous turns
            # response = llm_call(agent.system_prompt, topic, history)

            # MOCK RESPONSE for scaffolding
            mock_content = f"[{agent.name}] Analysis of '{topic}': ..."
            self.transcript.append(DebateTurn(agent_name=agent.name, content=mock_content, round=1))

        # Subsequent Rounds
        for r in range(2, rounds + 1):
            for agent in self.agents:
                # Agents criticize previous round
                mock_content = f"[{agent.name}] Critique of Round {r - 1}: ..."
                self.transcript.append(
                    DebateTurn(agent_name=agent.name, content=mock_content, round=r),
                )

        return DebateResult(
            topic=topic,
            rounds=rounds,
            transcript=self.transcript,
            consensus="[Synthesized Consensus from all rounds]",
        )
