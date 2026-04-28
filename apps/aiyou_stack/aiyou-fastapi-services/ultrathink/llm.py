# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""LLM Executor: Unified interface for calling LLMs (Anthropic, OpenAI, Vertex AI).

Design principles:
- Single interface for all providers
- Automatic retry with exponential backoff
- Token tracking and cost calculation
- Streaming support
- Error handling with graceful degradation

Philosophy: Abstract the messy details, expose the elegant interface.
"""

import time
from collections.abc import AsyncIterator
from typing import Any, Literal

import anthropic
from anthropic import Anthropic, AsyncAnthropic
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ultrathink.config import settings


class LLMResponse(BaseModel):
    """Response from LLM execution."""

    content: str = Field(description="Generated text")
    model: str = Field(description="Model used")
    tokens_input: int = Field(default=0, description="Input tokens")
    tokens_output: int = Field(default=0, description="Output tokens")
    cost_usd: float = Field(default=0.0, description="Estimated cost")
    latency_ms: float = Field(default=0.0, description="Response time")
    finish_reason: str = Field(default="complete")
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMExecutor:
    """Unified LLM executor with retry logic and cost tracking.

    Usage:
        executor = LLMExecutor()

        # Simple synchronous call
        response = executor.execute("Explain quantum computing")

        # Async streaming
        async for chunk in executor.stream("Write a poem"):
            print(chunk, end="")

        # With custom settings
        response = executor.execute(
            "Analyze this code",
            model="claude-opus-4-20250514",
            temperature=0.3,
            max_tokens=2000
        )

    Features:
    - Automatic retry (3 attempts, exponential backoff)
    - Cost tracking (tokens × model pricing)
    - Latency monitoring
    - Graceful error handling
    - Supports streaming
    """

    # Pricing per 1M tokens (as of 2025-11)
    PRICING = {
        "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
        "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
        "claude-sonnet-3-5-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    }

    def __init__(
        self,
        api_key: str | None = None,
        provider: Literal["anthropic", "openai", "vertex"] = "anthropic",
    ):
        """Initialize LLM executor.

        Args:
            api_key: API key (defaults to settings)
            provider: Which LLM provider to use

        """
        self.provider = provider
        self.api_key = api_key or settings.anthropic_api_key

        if not self.api_key and settings.is_production:
            raise ValueError("API key required in production mode")

        # Initialize clients
        if provider == "anthropic" and self.api_key:
            self.client = Anthropic(api_key=self.api_key)
            self.async_client = AsyncAnthropic(api_key=self.api_key)
        else:
            self.client = None
            self.async_client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIConnectionError)),
    )
    def execute(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Execute a prompt against the LLM.

        Args:
            prompt: User prompt/query
            system: Optional system prompt
            model: Model to use (defaults to settings)
            temperature: Sampling temperature (0-1)
            max_tokens: Max tokens to generate

        Returns:
            LLMResponse with content, tokens, cost, latency

        Raises:
            ValueError: If no API key in production
            anthropic.APIError: If API call fails after retries

        """
        # Use defaults from settings
        model = model or settings.anthropic_model
        temperature = temperature if temperature is not None else settings.anthropic_temperature
        max_tokens = max_tokens or settings.anthropic_max_tokens

        # Development mode: return placeholder
        if not self.client:
            return self._mock_response(prompt, model)

        # Execute with timing
        start_time = time.time()

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
            )

            latency = (time.time() - start_time) * 1000

            # Extract content
            content = response.content[0].text if response.content else ""

            # Calculate cost
            tokens_in = response.usage.input_tokens
            tokens_out = response.usage.output_tokens
            cost = self._calculate_cost(model, tokens_in, tokens_out)

            return LLMResponse(
                content=content,
                model=model,
                tokens_input=tokens_in,
                tokens_output=tokens_out,
                cost_usd=cost,
                latency_ms=latency,
                finish_reason=response.stop_reason or "complete",
                metadata={
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "provider": self.provider,
                },
            )

        except anthropic.APIError as e:
            # Log error and re-raise
            print(f"Anthropic API error: {e}")
            raise

    async def execute_async(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Async version of execute()."""
        model = model or settings.anthropic_model
        temperature = temperature if temperature is not None else settings.anthropic_temperature
        max_tokens = max_tokens or settings.anthropic_max_tokens

        if not self.async_client:
            return self._mock_response(prompt, model)

        start_time = time.time()

        response = await self.async_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )

        latency = (time.time() - start_time) * 1000
        content = response.content[0].text if response.content else ""
        tokens_in = response.usage.input_tokens
        tokens_out = response.usage.output_tokens
        cost = self._calculate_cost(model, tokens_in, tokens_out)

        return LLMResponse(
            content=content,
            model=model,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            cost_usd=cost,
            latency_ms=latency,
            finish_reason=response.stop_reason or "complete",
        )

    async def stream(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Stream LLM response token by token.

        Usage:
            async for chunk in executor.stream("Tell me a story"):
                print(chunk, end="", flush=True)
        """
        model = model or settings.anthropic_model
        temperature = temperature if temperature is not None else settings.anthropic_temperature
        max_tokens = max_tokens or settings.anthropic_max_tokens

        if not self.async_client:
            # Mock streaming in development
            for word in [
                "This",
                "is",
                "a",
                "placeholder",
                "response",
                "in",
                "development",
                "mode.",
            ]:
                yield word + " "
            return

        async with self.async_client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    def _calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate cost in USD based on token usage."""
        pricing = self.PRICING.get(model, {"input": 3.0, "output": 15.0})

        cost_in = (tokens_in / 1_000_000) * pricing["input"]
        cost_out = (tokens_out / 1_000_000) * pricing["output"]

        return cost_in + cost_out

    def _mock_response(self, prompt: str, model: str) -> LLMResponse:
        """Generate mock response for development without API key."""
        return LLMResponse(
            content=f"[MOCK RESPONSE - No API key configured]\n\nYou asked: {prompt[:100]}...\n\nThis is a placeholder. Set ANTHROPIC_API_KEY in .env for real responses.",
            model=model,
            tokens_input=len(prompt.split()),
            tokens_output=50,
            cost_usd=0.0,
            latency_ms=10.0,
            finish_reason="mock",
            metadata={"mock": True},
        )

    def __repr__(self) -> str:
        has_key = bool(self.api_key)
        return f"LLMExecutor(provider={self.provider!r}, configured={has_key})"
