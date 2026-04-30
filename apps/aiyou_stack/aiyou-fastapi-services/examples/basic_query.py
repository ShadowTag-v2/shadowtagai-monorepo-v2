#!/usr/bin/env python3
"""Basic Claude Agent SDK Query Example

This example demonstrates how to use the Claude Agent SDK to make simple queries.
"""

import asyncio
import os

from claude_agent_sdk import ClaudeAgentOptions, query


async def basic_query_example():
    """Simple query example"""
    print("=" * 50)
    print("Basic Query Example")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Create options with custom system prompt
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful AI assistant specialized in Python programming.",
        max_tokens=1024,
        temperature=0.7,
        api_key=api_key,
    )

    # Query the agent
    prompt = "Explain what FastAPI is in 2-3 sentences."
    print(f"\nPrompt: {prompt}\n")
    print("Response:")
    print("-" * 50)

    async for message in query(prompt=prompt, options=options):
        print(message, end="", flush=True)

    print("\n" + "=" * 50)


async def claude_code_preset_example():
    """Example using Claude Code preset"""
    print("\n" + "=" * 50)
    print("Claude Code Preset Example")
    print("=" * 50)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Use Claude Code preset
    options = ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code"},
        max_tokens=2048,
        api_key=api_key,
    )

    prompt = "Write a simple Python function to calculate fibonacci numbers."
    print(f"\nPrompt: {prompt}\n")
    print("Response:")
    print("-" * 50)

    async for message in query(prompt=prompt, options=options):
        print(message, end="", flush=True)

    print("\n" + "=" * 50)


async def main():
    """Run all examples"""
    print("\nClaude Agent SDK Examples")
    print("=" * 50)

    # Run basic query
    await basic_query_example()

    # Run Claude Code preset example
    await claude_code_preset_example()

    print("\nAll examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
