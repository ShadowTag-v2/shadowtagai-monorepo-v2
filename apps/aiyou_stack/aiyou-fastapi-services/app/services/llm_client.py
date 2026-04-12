"""
LLM Client integration supporting multiple providers.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

import structlog
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.core.config import settings

logger = structlog.get_logger()


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Send a chat request and get a complete response."""
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Send a chat request and stream the response."""
        pass


class AnthropicClient(LLMClient):
    """Anthropic/Claude LLM client."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL
        self.client = AsyncAnthropic(api_key=self.api_key)
        logger.info("Anthropic client initialized", model=self.model)

    async def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Send a chat request and get a complete response."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or settings.ANTHROPIC_MAX_TOKENS,
                temperature=temperature,
                system=system_prompt or settings.DEFAULT_SYSTEM_PROMPT,
                messages=messages,
                **kwargs,
            )

            # Extract text from response
            content = response.content[0].text if response.content else ""

            logger.info(
                "Chat completion successful",
                model=self.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )

            return content
        except Exception as e:
            logger.error("Chat completion failed", error=str(e))
            raise

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Send a chat request and stream the response."""
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens or settings.ANTHROPIC_MAX_TOKENS,
                temperature=temperature,
                system=system_prompt or settings.DEFAULT_SYSTEM_PROMPT,
                messages=messages,
                **kwargs,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

            logger.info("Streaming completion successful", model=self.model)
        except Exception as e:
            logger.error("Streaming completion failed", error=str(e))
            raise


class OpenAIClient(LLMClient):
    """OpenAI LLM client."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info("OpenAI client initialized", model=self.model)

    def _convert_messages(
        self, messages: list[dict[str, str]], system_prompt: str | None = None
    ) -> list[dict[str, str]]:
        """Convert messages format and add system prompt."""
        formatted_messages = []

        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        formatted_messages.extend(messages)
        return formatted_messages

    async def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Send a chat request and get a complete response."""
        try:
            formatted_messages = self._convert_messages(messages, system_prompt)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens or settings.OPENAI_MAX_TOKENS,
                temperature=temperature,
                **kwargs,
            )

            content = response.choices[0].message.content or ""

            logger.info(
                "Chat completion successful",
                model=self.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
            )

            return content
        except Exception as e:
            logger.error("Chat completion failed", error=str(e))
            raise

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Send a chat request and stream the response."""
        try:
            formatted_messages = self._convert_messages(messages, system_prompt)

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens or settings.OPENAI_MAX_TOKENS,
                temperature=temperature,
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            logger.info("Streaming completion successful", model=self.model)
        except Exception as e:
            logger.error("Streaming completion failed", error=str(e))
            raise


class LLMClientFactory:
    """Factory for creating LLM clients."""

    @staticmethod
    def create_client(
        provider: str | None = None, api_key: str | None = None, model: str | None = None
    ) -> LLMClient:
        """Create an LLM client based on the provider."""
        provider = provider or settings.DEFAULT_LLM_PROVIDER

        if provider.lower() == "anthropic":
            return AnthropicClient(api_key=api_key, model=model)
        elif provider.lower() == "openai":
            return OpenAIClient(api_key=api_key, model=model)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
