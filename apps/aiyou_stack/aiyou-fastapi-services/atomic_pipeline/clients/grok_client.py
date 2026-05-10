"""Grok Code Fast 1 API Client
============================
xAI's agentic coding model optimized for rapid code generation.

Specs:
- Model: grok-3-fast-latest (314B MoE)
- Context: 256K tokens
- Pricing: $0.15/M input, $0.60/M output
- Strengths: Real-time X trends, rapid coding, business insights
"""

import json
import logging
import os
from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Any

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GrokModel(StrEnum):
    """Available Grok models"""

    GROK_3_FAST = "grok-3-fast-latest"
    GROK_3 = "grok-3-latest"
    GROK_3_MINI_FAST = "grok-3-mini-fast-latest"


class GrokConfig(BaseModel):
    """Configuration for Grok API client"""

    api_key: str = Field(default_factory=lambda: os.getenv("XAI_API_KEY", ""))
    base_url: str = "https://api.x.ai/v1"
    model: GrokModel = GrokModel.GROK_3_FAST
    max_tokens: int = 8192
    temperature: float = 0.7
    timeout: float = 120.0

    # Agentic coding optimizations
    enable_x_context: bool = True  # Include X/Twitter context
    enable_realtime: bool = True  # Real-time information access


class GrokResponse(BaseModel):
    """Structured response from Grok"""

    content: str
    model: str
    usage: dict[str, int]
    x_context: list[dict[str, Any]] | None = None
    finish_reason: str = "stop"


class GrokClient:
    """Grok Code Fast 1 API Client.

    Used in the atomic pipeline for:
    - Real-time trend analysis from X
    - Rapid code generation
    - Business context and insights
    """

    def __init__(self, config: GrokConfig | None = None):
        self.config = config or GrokConfig()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.config.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._client

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> GrokResponse:
        """Generate a completion from Grok.

        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            GrokResponse with content and metadata

        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model.value,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
        }

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        choice = data["choices"][0]

        return GrokResponse(
            content=choice["message"]["content"],
            model=data["model"],
            usage=data["usage"],
            finish_reason=choice.get("finish_reason", "stop"),
        )

    async def analyze_trends(
        self,
        topic: str,
        context: str | None = None,
    ) -> GrokResponse:
        """Analyze current X/Twitter trends for a topic.

        Args:
            topic: Topic to analyze trends for
            context: Additional context for analysis

        Returns:
            GrokResponse with trend analysis

        """
        system_prompt = """You are a trend analyst with real-time access to X (Twitter).
Analyze current discussions, trending topics, and sentiment around the given topic.
Provide actionable insights for software development decisions."""

        prompt = f"""Analyze current trends and discussions on X for: {topic}

{f"Additional context: {context}" if context else ""}

Provide:
1. Top 3-5 current trends/discussions
2. Sentiment analysis
3. Key influencer opinions
4. Technical recommendations based on community preferences
5. Potential risks or concerns being discussed"""

        return await self.generate(prompt, system_prompt=system_prompt)

    async def generate_code(
        self,
        task: str,
        language: str = "python",
        style_guide: str | None = None,
        test_requirements: bool = True,
    ) -> GrokResponse:
        """Generate code rapidly with Grok Code Fast.

        Args:
            task: Code generation task description
            language: Target programming language
            style_guide: Optional style guidelines
            test_requirements: Include test code

        Returns:
            GrokResponse with generated code

        """
        system_prompt = f"""You are an expert {language} developer optimized for rapid, accurate code generation.
Generate production-ready code that follows best practices.
{f"Style guide: {style_guide}" if style_guide else ""}"""

        prompt = f"""Generate {language} code for:
{task}

Requirements:
- Production-ready quality
- Clear documentation
- Error handling
- Type hints (if applicable)
{"- Include comprehensive tests" if test_requirements else ""}

Output format: Code blocks with explanations."""

        return await self.generate(prompt, system_prompt=system_prompt, temperature=0.3)

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream a completion from Grok.

        Args:
            prompt: User prompt
            system_prompt: Optional system instructions

        Yields:
            Content chunks as they arrive

        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model.value,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": True,
        }

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if chunk["choices"][0].get("delta", {}).get("content"):
                            yield chunk["choices"][0]["delta"]["content"]
                    except json.JSONDecodeError:
                        continue
