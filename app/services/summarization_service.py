# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Summarization service using Claude API."""

import logging
from typing import List, Optional
from anthropic import AsyncAnthropic

from app.core.config import settings
from app.models import Message

logger = logging.getLogger(__name__)


class SummarizationService:
    """Service for summarizing conversations and generating memory insights."""

    def __init__(self):
        """Initialize the summarization service."""
        self.client: AsyncAnthropic | None = None
        if settings.anthropic_api_key:
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def summarize_conversation(self, messages: list[Message]) -> str:
        """
        Summarize a conversation.

        Args:
            messages: List of messages to summarize

        Returns:
            Conversation summary
        """
        if not self.client:
            logger.warning("Anthropic API key not configured, using fallback summarization")
            return self._fallback_summary(messages)

        try:
            # Format messages for Claude
            conversation_text = self._format_messages(messages)

            # Create summarization prompt
            prompt = f"""Please provide a concise summary of the following conversation.
Focus on the main topics discussed, key decisions made, and important information shared.

Conversation:
{conversation_text}

Summary:"""

            # Call Claude API
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use Haiku for faster, cheaper summaries
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            summary = response.content[0].text
            return summary

        except Exception as e:
            logger.error(f"Error summarizing conversation: {e}")
            return self._fallback_summary(messages)

    async def extract_memories(self, messages: list[Message], existing_summary: str | None = None) -> list[dict]:
        """
        Extract key insights and facts to store as memories.

        Args:
            messages: List of messages to analyze
            existing_summary: Existing conversation summary (if any)

        Returns:
            List of memory dictionaries
        """
        if not self.client:
            logger.warning("Anthropic API key not configured, skipping memory extraction")
            return []

        try:
            conversation_text = self._format_messages(messages)

            prompt = f"""Analyze the following conversation and extract key information that should be remembered.
For each piece of information, categorize it as one of: fact, preference, context, or insight.

Output format (JSON array):
[
  {{"type": "fact", "content": "...", "title": "..."}},
  {{"type": "preference", "content": "...", "title": "..."}}
]

Conversation:
{conversation_text}

Extracted memories (JSON):"""

            response = await self.client.messages.create(
                model="claude-3-haiku-20240307", max_tokens=1000, messages=[{"role": "user", "content": prompt}]
            )

            # Parse JSON response
            import json

            memories_text = response.content[0].text
            # Extract JSON from markdown code blocks if present
            if "```json" in memories_text:
                memories_text = memories_text.split("```json")[1].split("```")[0].strip()
            elif "```" in memories_text:
                memories_text = memories_text.split("```")[1].split("```")[0].strip()

            memories = json.loads(memories_text)
            return memories if isinstance(memories, list) else []

        except Exception as e:
            logger.error(f"Error extracting memories: {e}")
            return []

    async def synthesize_memories(self, memories: list[dict]) -> str:
        """
        Create a synthesis/summary from multiple memories.

        Args:
            memories: List of memory dictionaries

        Returns:
            Synthesized summary
        """
        if not self.client or not memories:
            return ""

        try:
            # Format memories
            memories_text = "\n\n".join([f"[{m.get('memory_type', 'fact')}] {m.get('title', '')}: {m.get('content', '')}" for m in memories])

            prompt = f"""Based on the following memories and facts, create a coherent synthesis
that captures the key context and information about the user.

Memories:
{memories_text}

Synthesis:"""

            response = await self.client.messages.create(
                model="claude-3-haiku-20240307", max_tokens=1000, messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error synthesizing memories: {e}")
            return ""

    def _format_messages(self, messages: list[Message]) -> str:
        """Format messages for Claude API."""
        formatted = []
        for msg in messages:
            role = msg.role.upper()
            content = msg.content
            formatted.append(f"{role}: {content}")
        return "\n\n".join(formatted)

    def _fallback_summary(self, messages: list[Message]) -> str:
        """Simple fallback summary when API is not available."""
        if not messages:
            return "Empty conversation"

        message_count = len(messages)
        user_messages = sum(1 for m in messages if m.role == "user")
        assistant_messages = sum(1 for m in messages if m.role == "assistant")

        return f"Conversation with {message_count} messages ({user_messages} from user, {assistant_messages} from assistant)"


# Global singleton instance
summarization_service = SummarizationService()
