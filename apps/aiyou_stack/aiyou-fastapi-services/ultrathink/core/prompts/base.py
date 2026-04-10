"""
Base prompt class for all prompting techniques.

Design principle: Every prompt technique should be:
1. Self-documenting (the structure explains the intent)
2. Composable (can be chained or nested)
3. Traceable (we know exactly what was sent to the model)
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class PromptResult(BaseModel):
    """Result of a prompt execution."""

    prompt: str = Field(description="The formatted prompt sent to the model")
    response: str | None = Field(default=None, description="Model response")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Tracking data (tokens, cost, timing)"
    )


class BasePrompt(ABC):
    """
    Base class for all prompting techniques.

    Philosophy: A prompt is a contract between human intent and machine execution.
    Make that contract crystal clear.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with technique-specific parameters."""
        self.params = kwargs

    @abstractmethod
    def format(self, user_input: str) -> str:
        """
        Format the user input into a structured prompt.

        Args:
            user_input: The raw user query or content

        Returns:
            Formatted prompt ready for the model

        Example:
            >>> prompt = SomePromptTechnique(role="expert")
            >>> prompt.format("Analyze this data")
            "You are an expert. Analyze this data..."
        """
        pass

    def execute(
        self,
        user_input: str,
        model: Any | None = None,
        **execution_kwargs: Any,
    ) -> PromptResult:
        """
        Format and execute the prompt against a model.

        Args:
            user_input: The raw user query
            model: Optional model instance (defaults to configured default)
            **execution_kwargs: Model-specific parameters (temperature, max_tokens, etc.)

        Returns:
            PromptResult with prompt, response, and metadata

        Note:
            Override this in subclasses for custom execution logic.
        """
        formatted_prompt = self.format(user_input)

        # Execute with LLM if available
        try:
            from ultrathink.llm import LLMExecutor

            executor = model if model else LLMExecutor()
            llm_response = executor.execute(formatted_prompt, **execution_kwargs)

            result = PromptResult(
                prompt=formatted_prompt,
                response=llm_response.content,
                metadata={
                    "technique": self.__class__.__name__,
                    "params": self.params,
                    "model": llm_response.model,
                    "tokens_input": llm_response.tokens_input,
                    "tokens_output": llm_response.tokens_output,
                    "cost_usd": llm_response.cost_usd,
                    "latency_ms": llm_response.latency_ms,
                    **execution_kwargs,
                },
            )

        except Exception as e:
            # Fallback to placeholder if LLM fails
            result = PromptResult(
                prompt=formatted_prompt,
                response=f"[Error executing LLM: {e}]",
                metadata={
                    "technique": self.__class__.__name__,
                    "params": self.params,
                    "error": str(e),
                    **execution_kwargs,
                },
            )

        return result

    def __repr__(self) -> str:
        """Clean representation for debugging."""
        params_str = ", ".join(f"{k}={v!r}" for k, v in self.params.items())
        return f"{self.__class__.__name__}({params_str})"
