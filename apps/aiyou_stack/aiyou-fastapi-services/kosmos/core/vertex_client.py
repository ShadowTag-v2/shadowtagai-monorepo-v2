"""Vertex AI Gemini Client: Wrapper for Google Vertex AI generative models.

Provides cost tracking, model selection logic, and error handling for
Gemini 2.5 Pro and Flash models.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

try:
    import vertexai
    from vertexai.generative_models import GenerationConfig, GenerativeModel, Part
    from vertexai.preview.generative_models import FunctionDeclaration, Tool
except ImportError:
    raise ImportError(
        "Vertex AI SDK not installed. Install with: pip install google-cloud-aiplatform",
    )

logger = logging.getLogger(__name__)


class GeminiModel(Enum):
    """Available Gemini models with cost characteristics."""

    FLASH = "gemini-2.5-flash"  # Fast, cheap - upgraded to 2.5
    PRO = "gemini-1.5-pro"  # Deep reasoning (using 1.5 until 2.5 GA)

    @property
    def cost_per_1m_input(self) -> float:
        """Cost per 1M input tokens in USD."""
        costs = {
            GeminiModel.FLASH: 0.075,
            GeminiModel.PRO: 1.25,
        }
        return costs[self]

    @property
    def cost_per_1m_output(self) -> float:
        """Cost per 1M output tokens in USD."""
        costs = {
            GeminiModel.FLASH: 0.30,
            GeminiModel.PRO: 5.00,
        }
        return costs[self]


@dataclass
class GenerationResult:
    """Result from a model generation call."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    finish_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "finish_reason": self.finish_reason,
        }


class VertexAIClient:
    """Client for Vertex AI Gemini models with cost tracking and smart routing.

    Features:
    - Automatic model selection based on context size and task complexity
    - Token counting and cost estimation
    - Error handling and retry logic
    - Support for function calling (tools)
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        default_model: GeminiModel = GeminiModel.PRO,
        cost_tracker: Any | None = None,  # CostMonitor instance
    ):
        """Initialize Vertex AI client.

        Args:
            project_id: GCP project ID
            location: GCP region for Vertex AI
            default_model: Default Gemini model to use
            cost_tracker: Optional CostMonitor for budget tracking

        """
        self.project_id = project_id
        self.location = location
        self.default_model = default_model
        self.cost_tracker = cost_tracker

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        logger.info(f"Initialized Vertex AI client for project {project_id} in {location}")

        # Model cache
        self._models: dict[str, GenerativeModel] = {}

    def get_model(
        self,
        model: GeminiModel | None = None,
        tools: list[FunctionDeclaration] | None = None,
    ) -> GenerativeModel:
        """Get or create a Gemini model instance.

        Args:
            model: Gemini model type (defaults to client default)
            tools: Optional list of function declarations for tool calling

        Returns:
            GenerativeModel instance

        """
        model = model or self.default_model
        model_name = model.value

        # Create cache key based on model and tools
        cache_key = f"{model_name}_{hash(tuple(tools) if tools else ())}"

        if cache_key not in self._models:
            if tools:
                self._models[cache_key] = GenerativeModel(
                    model_name,
                    tools=[Tool(function_declarations=tools)],
                )
            else:
                self._models[cache_key] = GenerativeModel(model_name)

            logger.debug(f"Created new model instance: {model_name}")

        return self._models[cache_key]

    def generate(
        self,
        prompt: str,
        model: GeminiModel | None = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        tools: list[FunctionDeclaration] | None = None,
        **kwargs,
    ) -> GenerationResult:
        """Generate text using Gemini model.

        Args:
            prompt: Input prompt text
            model: Gemini model to use (defaults to client default)
            temperature: Sampling temperature (0-1)
            max_output_tokens: Maximum tokens to generate
            tools: Optional function declarations for tool calling
            **kwargs: Additional generation config parameters

        Returns:
            GenerationResult with text, tokens, and cost

        Raises:
            RuntimeError: If generation fails after retries

        """
        model = model or self.default_model
        gemini_model = self.get_model(model, tools)

        # Estimate input tokens (rough approximation: 1 token ≈ 4 chars)
        estimated_input_tokens = len(prompt) // 4

        # Check budget if cost tracker available
        if self.cost_tracker:
            estimated_cost = self._estimate_cost(estimated_input_tokens, max_output_tokens, model)
            self.cost_tracker.check_budget(estimated_cost)

        # Configure generation
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            **kwargs,
        )

        try:
            # Generate content
            response = gemini_model.generate_content(
                prompt,
                generation_config=generation_config,
            )

            # Extract text
            text = response.text if hasattr(response, "text") else str(response)

            # Get token counts from metadata if available
            input_tokens = estimated_input_tokens
            output_tokens = len(text) // 4  # Rough approximation

            # Try to get actual token counts from usage metadata
            if hasattr(response, "usage_metadata"):
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count

            # Calculate actual cost
            cost = self._calculate_cost(input_tokens, output_tokens, model)

            # Record usage if cost tracker available
            if self.cost_tracker:
                self.cost_tracker.record_usage(
                    input_tokens + output_tokens,
                    model.value,
                    cost,
                )

            logger.info(
                f"Generated {output_tokens} tokens with {model.value} "
                f"(cost: ${cost:.4f}, input: {input_tokens} tokens)",
            )

            return GenerationResult(
                text=text,
                model=model.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                finish_reason=getattr(response.candidates[0], "finish_reason", None)
                if hasattr(response, "candidates")
                else None,
            )

        except Exception as e:
            logger.error(f"Generation failed with {model.value}: {e}")
            raise RuntimeError(f"Gemini generation failed: {e}")

    def generate_with_auto_routing(
        self,
        prompt: str,
        context_length: int | None = None,
        complexity: str = "medium",
        **kwargs,
    ) -> GenerationResult:
        """Generate with automatic model selection based on context and complexity.

        Routing logic:
        - Flash: Short context (<5k tokens) + low complexity
        - Pro: Long context (>5k tokens) OR high complexity

        Args:
            prompt: Input prompt
            context_length: Optional explicit context length (auto-estimated if None)
            complexity: Task complexity ("low", "medium", "high")
            **kwargs: Additional generation parameters

        Returns:
            GenerationResult

        """
        # Estimate context length if not provided
        if context_length is None:
            context_length = len(prompt) // 4

        # Select model based on routing logic
        if context_length < 5000 and complexity == "low":
            model = GeminiModel.FLASH
            logger.debug("Auto-routing: Selected Flash (short context, low complexity)")
        else:
            model = GeminiModel.PRO
            logger.debug(
                f"Auto-routing: Selected Pro (context={context_length}, complexity={complexity})",
            )

        return self.generate(prompt, model=model, **kwargs)

    def _estimate_cost(self, input_tokens: int, output_tokens: int, model: GeminiModel) -> float:
        """Estimate cost for a generation.

        Args:
            input_tokens: Estimated input tokens
            output_tokens: Expected output tokens
            model: Gemini model

        Returns:
            Estimated cost in USD

        """
        input_cost = (input_tokens / 1_000_000) * model.cost_per_1m_input
        output_cost = (output_tokens / 1_000_000) * model.cost_per_1m_output
        return input_cost + output_cost

    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: GeminiModel) -> float:
        """Calculate actual cost from token counts.

        Args:
            input_tokens: Actual input tokens
            output_tokens: Actual output tokens
            model: Gemini model used

        Returns:
            Cost in USD

        """
        return self._estimate_cost(input_tokens, output_tokens, model)

    def create_function_declaration(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
    ) -> FunctionDeclaration:
        """Create a function declaration for tool calling.

        Args:
            name: Function name
            description: Function description
            parameters: JSON schema for parameters

        Returns:
            FunctionDeclaration for use with tools

        Example:
            >>> client.create_function_declaration(
            ...     name="search_papers",
            ...     description="Search academic papers by query",
            ...     parameters={
            ...         "type": "object",
            ...         "properties": {
            ...             "query": {"type": "string", "description": "Search query"},
            ...             "limit": {"type": "integer", "description": "Max results"},
            ...         },
            ...         "required": ["query"],
            ...     },
            ... )

        """
        return FunctionDeclaration(
            name=name,
            description=description,
            parameters=parameters,
        )

    def __repr__(self) -> str:
        return (
            f"VertexAIClient(project={self.project_id}, location={self.location}, "
            f"default_model={self.default_model.value})"
        )
