"""Claude Agent SDK Service"""

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class ClaudeAgentService:
    """Service for interacting with Claude Agent SDK"""

    def __init__(self):
        """Initialize Claude Agent Service"""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set. Agent queries will fail.")

    async def query(
        self,
        prompt: str,
        system_prompt: str | None = None,
        use_claude_code_preset: bool = False,
        max_tokens: int | None = None,
        temperature: float = 1.0,
    ) -> dict[str, Any]:
        """Query Claude Agent

        Args:
            prompt: The user prompt
            system_prompt: Optional custom system prompt
            use_claude_code_preset: Use Claude Code preset
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Dict containing response content and metadata

        """
        try:
            # Import here to avoid issues if SDK not installed
            from claude_agent_sdk import ClaudeAgentOptions
            from claude_agent_sdk import query as agent_query

            # Configure system prompt
            if use_claude_code_preset:
                system_prompt_config = {"type": "preset", "preset": "claude_code"}
            elif system_prompt:
                system_prompt_config = system_prompt
            else:
                system_prompt_config = "You are a helpful AI assistant."

            # Configure options
            options = ClaudeAgentOptions(
                system_prompt=system_prompt_config,
                max_tokens=max_tokens or settings.MAX_TOKENS,
                temperature=temperature,
                api_key=settings.ANTHROPIC_API_KEY,
            )

            # Collect response
            response_content = ""
            async for message in agent_query(prompt=prompt, options=options):
                response_content += str(message)

            return {
                "content": response_content,
                "metadata": {
                    "model": settings.CLAUDE_MODEL,
                    "max_tokens": max_tokens or settings.MAX_TOKENS,
                    "temperature": temperature,
                },
            }

        except ImportError:
            logger.error("claude_agent_sdk not installed")
            raise Exception("Claude Agent SDK not installed. Run: pip install claude-agent-sdk") from None

        except Exception as e:
            logger.error(f"Error in Claude Agent query: {e}", exc_info=True)
            raise
