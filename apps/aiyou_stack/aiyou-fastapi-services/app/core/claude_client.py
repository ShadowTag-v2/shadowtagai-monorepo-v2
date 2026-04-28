# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Claude client wrapper using Claude Agent SDK."""

from collections.abc import AsyncGenerator

import anthropic
from claude_agent_sdk import ClaudeAgentOptions, query

from app.config import settings


class ClaudeClient:
    """Wrapper for Claude Agent SDK."""

    def __init__(self):
        """Initialize Claude client."""
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model

    async def query_with_context(
        self,
        prompt: str,
        system_prompt: str | None = None,
        memory_context: str | None = None,
        conversation_context: list[dict] | None = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> AsyncGenerator[str, None]:
        """Query Claude with context using the Agent SDK."""
        # Build enhanced system prompt
        enhanced_system = system_prompt or "You are a helpful AI assistant."

        if memory_context:
            enhanced_system += f"\n\n## Persistent Memory\n{memory_context}"

        if conversation_context:
            context_text = "\n\n".join(
                f"**{ctx['role']}**: {ctx['content']}" for ctx in conversation_context
            )
            enhanced_system += f"\n\n## Relevant Past Context\n{context_text}"

        # Query using Claude Agent SDK
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                system_prompt=enhanced_system,
                model=self.model,
            ),
        ):
            # Extract text content from the message
            if hasattr(message, "content"):
                for block in message.content:
                    if hasattr(block, "text"):
                        yield block.text
            elif isinstance(message, str):
                yield message

    async def synthesize_memory(
        self,
        conversations: list[dict],
        existing_memory: str | None = None,
    ) -> dict:
        """Synthesize memory from conversations using Claude.

        Returns a dict with categorized memory entries.
        """
        # Build synthesis prompt
        conversations_text = ""
        for conv in conversations:
            conversations_text += f"\n### Conversation: {conv['title']}\n"
            for msg in conv.get("messages", []):
                conversations_text += f"**{msg['role']}**: {msg['content']}\n"

        synthesis_prompt = f"""
Analyze the following conversations and extract key information that should be remembered for future interactions.

Categorize your findings into:
1. **preferences**: User preferences, working style, communication patterns
2. **facts**: Project facts, technical stack, constraints, business requirements
3. **decisions**: Technical decisions, architectural choices, strategic directions
4. **patterns**: Recurring themes, common workflows, established processes

{"## Existing Memory" if existing_memory else ""}
{existing_memory or ""}

## Recent Conversations
{conversations_text}

Please provide your analysis in JSON format:
{{
  "preferences": [
    {{"content": "...", "confidence": 0.95}}
  ],
  "facts": [
    {{"content": "...", "confidence": 0.9}}
  ],
  "decisions": [
    {{"content": "...", "confidence": 0.85}}
  ],
  "patterns": [
    {{"content": "...", "confidence": 0.8}}
  ]
}}

Guidelines:
- Only include high-confidence insights (>0.7)
- Be specific and actionable
- Avoid duplicating existing memory
- Focus on information that would be valuable in future conversations
"""

        # Use anthropic client directly for structured output
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.3,  # Lower temperature for more consistent output
            messages=[{"role": "user", "content": synthesis_prompt}],
        )

        # Extract JSON from response
        content = response.content[0].text if response.content else "{}"

        # Parse JSON (in production, add better error handling)
        import json

        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            memory_data = json.loads(content)
            return memory_data
        except json.JSONDecodeError:
            # Return empty structure if parsing fails
            return {
                "preferences": [],
                "facts": [],
                "decisions": [],
                "patterns": [],
            }


# Global Claude client instance
claude_client = ClaudeClient()
