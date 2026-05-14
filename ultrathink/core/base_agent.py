# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - Base Agent

Foundation class for all agents in the ULTRATHINK framework.
Embodies Steve Jobs' philosophy: design-first, ruthless simplification, insanely great execution.
"""

from abc import ABC, abstractmethod
from typing import Any
from .types import AgentContext, AgentResponse, AgentRole, ReasoningPath, ReasoningMethod, UltrathinkConfig


class BaseAgent(ABC):
    """
    Base class for all ULTRATHINK agents.

    Core Principles:
    1. Design-First Thinking: Scrutinize elegance before functionality
    2. Boy Scout Rule: Leave everything cleaner than found
    3. Assumption Interrogation: Question every "why"
    4. Pinkln Elegance: Remove until nothing left to remove
    5. Reality Distortion Field: When impossible, ultrathink harder
    """

    def __init__(self, role: AgentRole, system_prompt: str, config: UltrathinkConfig | None = None):
        self.role = role
        self.system_prompt = system_prompt
        self.config = config or UltrathinkConfig()
        self._execution_history: list[AgentResponse] = []

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResponse:
        """
        Execute the agent's primary task.

        Args:
            context: The execution context

        Returns:
            AgentResponse with results and reasoning
        """
        pass

    def get_system_prompt(self) -> str:
        """
        Get the agent's system prompt.

        The system prompt embeds the ULTRATHINK philosophy into the agent's DNA.
        """
        return self.system_prompt

    def validate_security(self, context: AgentContext) -> bool:
        """
        Validate security constraints.

        If security is compromised, this becomes the ONLY priority.
        Returns False if security checks fail.
        """
        if not self.config.security_mode:
            return True

        # Security validation logic
        # In a real implementation, this would check for:
        # - Input sanitization
        # - Sensitive data exposure
        # - Unauthorized access patterns
        # - Malicious code patterns

        return True

    def apply_boy_scout_rule(self, content: str) -> str:
        """
        Apply the Boy Scout Rule: leave code cleaner than found.

        This is a philosophical commitment to continuous improvement.
        """
        # In practice, this would apply formatting, remove redundancy,
        # improve naming, etc. For now, it's a placeholder for the principle.
        return content

    def interrogate_assumptions(self, problem: str) -> list[str]:
        """
        Question every assumption in the problem statement.

        Returns a list of questions to challenge the status quo.
        """
        questions = [
            f"Why must {problem} work this way?",
            f"What if we started from zero on {problem}?",
            f"What is the ONE thing that matters most in {problem}?",
            "Would a simpler solution be more elegant?",
            "What are we taking for granted?",
        ]
        return questions

    def assess_elegance(self, solution: str) -> dict[str, Any]:
        """
        Assess a solution against pinkln elegance criteria.

        Pinkln elegance: achieved not by what remains to add,
        but by what can be removed without losing power.
        """
        criteria = {
            "simplicity": "Can a novice understand it?",
            "clarity": "Is the intent clear?",
            "natural_flow": "Does it feel intuitive?",
            "minimalism": "Can anything be removed?",
            "functionality_preserved": "Does it still solve the problem?",
        }

        # In a real implementation, this would analyze the solution
        # against each criterion. For now, return the framework.
        assessment = {criterion: {"question": question, "score": 0.0} for criterion, question in criteria.items()}

        return assessment

    def create_reasoning_path(self, method: ReasoningMethod, steps: list[str], confidence: float = 0.0) -> ReasoningPath:
        """
        Create a reasoning path documenting the thought process.

        Transparency is key: show the work, make it auditable.
        """
        return ReasoningPath(
            method=method, steps=steps, confidence=confidence, alternatives_considered=[], risks=[], metadata={"agent_role": self.role.value}
        )

    def record_execution(self, response: AgentResponse) -> None:
        """Record an execution in history for learning and audit."""
        self._execution_history.append(response)

    def get_execution_history(self) -> list[AgentResponse]:
        """Get the agent's execution history."""
        return self._execution_history.copy()

    def self_reflect(self) -> dict[str, Any]:
        """
        Self-reflection gate before finalizing major deliverables.

        Ask:
        - What assumptions did we make?
        - What could be wrong?
        - What are we blind to?
        """
        reflection = {
            "assumptions_made": [],
            "potential_errors": [],
            "blind_spots": [],
            "confidence_level": 0.0,
            "recommendation": "proceed",  # or "review" or "abort"
        }

        # In a real implementation, analyze execution history
        # and identify patterns, risks, and uncertainties

        return reflection
