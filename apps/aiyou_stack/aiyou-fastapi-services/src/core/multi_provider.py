# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Multi-Provider LLM Support: Anthropic Claude + Google Gemini

Unified interface supporting:
- Anthropic Claude (Sonnet 4.5, Opus 4, Haiku 3.5)
- Google Gemini (2.0 Flash, 1.5 Pro)
- Automatic fallback and load balancing

Design: Best of both worlds
- Anthropic: Superior reasoning, CoT, extended thinking
- Gemini: Native function calling, 12x faster, 70% cheaper
"""

import os
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal

import anthropic
import google.generativeai as genai
from anthropic import Anthropic, AsyncAnthropic
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class Provider(StrEnum):
    """Supported LLM providers."""

    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    AUTO = "auto"  # Automatic selection based on task


@dataclass
class LLMResponse:
    """Unified response from any provider."""

    content: str
    provider: Provider
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    finish_reason: str = "complete"
    metadata: dict[str, Any] = field(default_factory=dict)


class MultiProviderExecutor:
    """Unified LLM executor supporting Anthropic + Gemini.

    Automatic provider selection based on task type:
    - Function calling → Gemini (12x faster)
    - Deep reasoning → Anthropic (superior CoT)
    - Cost-sensitive → Gemini (70% cheaper)
    - Quality-critical → Anthropic (best accuracy)

    Usage:
        executor = MultiProviderExecutor()

        # Explicit provider
        response = executor.execute("Explain quantum physics", provider="anthropic")

        # Auto-select based on task
        response = executor.execute(
            "Research this topic",
            provider="auto",
            task_type="function_calling"  # → Gemini
        )

        # With fallback
        response = executor.execute(
            "Generate code",
            provider="anthropic",
            fallback_provider="gemini"
        )
    """

    # Pricing per 1M tokens (as of 2025-11)
    PRICING = {
        "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
        "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
        "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        "gemini-3.1-flash-lite-preview": {"input": 0.075, "output": 0.30},
    }

    def __init__(
        self,
        anthropic_api_key: str | None = None,
        gemini_api_key: str | None = None,
        default_provider: Provider = Provider.AUTO,
    ):
        """Initialize multi-provider executor.

        Args:
            anthropic_api_key: Anthropic API key (or from ANTHROPIC_API_KEY env)
            gemini_api_key: Google API key (or from GOOGLE_API_KEY env)
            default_provider: Default provider when not specified

        """
        self.default_provider = default_provider

        # Initialize Anthropic
        self.anthropic_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.anthropic_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_key)
            self.anthropic_async = AsyncAnthropic(api_key=self.anthropic_key)
        else:
            self.anthropic_client = None
            self.anthropic_async = None

        # Initialize Gemini
        self.gemini_key = gemini_api_key or os.getenv("GOOGLE_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_available = True
        else:
            self.gemini_available = False

    def _select_provider(
        self,
        provider: Provider | str,
        task_type: Literal["function_calling", "reasoning", "general"] | None = None,
        fallback_provider: Provider | str | None = None,
    ) -> Provider:
        """Select the best provider for the task."""
        if isinstance(provider, str):
            provider = Provider(provider)

        if provider == Provider.AUTO:
            # Auto-select based on task
            if task_type == "function_calling":
                return Provider.GEMINI if self.gemini_available else Provider.ANTHROPIC
            if task_type == "reasoning":
                return Provider.ANTHROPIC if self.anthropic_client else Provider.GEMINI
            # Default: Gemini for cost/speed
            return Provider.GEMINI if self.gemini_available else Provider.ANTHROPIC

        return provider

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIConnectionError)),
    )
    def execute(
        self,
        prompt: str,
        provider: Provider | str = Provider.AUTO,
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        task_type: Literal["function_calling", "reasoning", "general"] | None = None,
        fallback_provider: Provider | str | None = None,
    ) -> LLMResponse:
        """Execute prompt with automatic provider selection.

        Args:
            prompt: User query
            provider: Which provider ("anthropic", "gemini", "auto")
            system: Optional system prompt
            model: Specific model (or provider default)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            task_type: Type of task (for auto-selection)
            fallback_provider: Fallback if primary fails

        Returns:
            LLMResponse with content, tokens, cost, latency

        """
        selected_provider = self._select_provider(provider, task_type, fallback_provider)

        try:
            if selected_provider == Provider.ANTHROPIC:
                return self._execute_anthropic(prompt, system, model, temperature, max_tokens)
            return self._execute_gemini(prompt, system, model, temperature, max_tokens)

        except Exception:
            # Try fallback if specified
            if fallback_provider:
                fallback = (
                    Provider(fallback_provider)
                    if isinstance(fallback_provider, str)
                    else fallback_provider
                )
                if fallback == Provider.ANTHROPIC:
                    return self._execute_anthropic(prompt, system, model, temperature, max_tokens)
                return self._execute_gemini(prompt, system, model, temperature, max_tokens)
            raise

    def _execute_anthropic(
        self,
        prompt: str,
        system: str | None,
        model: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> LLMResponse:
        """Execute with Anthropic Claude."""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")

        model = model or "claude-sonnet-4-5-20250929"
        temperature = temperature if temperature is not None else 0.7
        max_tokens = max_tokens or 4096

        start_time = time.time()

        response = self.anthropic_client.messages.create(
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
            provider=Provider.ANTHROPIC,
            model=model,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            cost_usd=cost,
            latency_ms=latency,
            finish_reason=response.stop_reason or "complete",
        )

    def _execute_gemini(
        self,
        prompt: str,
        system: str | None,
        model: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> LLMResponse:
        """Execute with Google Gemini."""
        if not self.gemini_available:
            raise ValueError("Gemini API key not configured")

        model_name = model or "gemini-3.1-flash-lite-preview"
        temperature = temperature if temperature is not None else 0.7

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens or 8192,
        }

        model_instance = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system,
        )

        start_time = time.time()
        response = model_instance.generate_content(prompt)
        latency = (time.time() - start_time) * 1000

        content = response.text or ""

        # Gemini usage metadata
        tokens_in = (
            response.usage_metadata.prompt_token_count if hasattr(response, "usage_metadata") else 0
        )
        tokens_out = (
            response.usage_metadata.candidates_token_count
            if hasattr(response, "usage_metadata")
            else 0
        )
        cost = self._calculate_cost(model_name, tokens_in, tokens_out)

        return LLMResponse(
            content=content,
            provider=Provider.GEMINI,
            model=model_name,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            cost_usd=cost,
            latency_ms=latency,
            finish_reason="complete",
        )

    def _calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate cost in USD."""
        pricing = self.PRICING.get(model, {"input": 3.0, "output": 15.0})
        cost_in = (tokens_in / 1_000_000) * pricing["input"]
        cost_out = (tokens_out / 1_000_000) * pricing["output"]
        return cost_in + cost_out

    def __repr__(self) -> str:
        providers = []
        if self.anthropic_client:
            providers.append("Anthropic")
        if self.gemini_available:
            providers.append("Gemini")
        return f"MultiProviderExecutor(providers={providers})"
