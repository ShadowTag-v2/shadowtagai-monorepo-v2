#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Claude Agent SDK with Custom Tools Example

This example shows how to create and use custom tools with the Claude Agent SDK.
"""

import asyncio
import os
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, query, tool


@tool
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.

    Args:
        n: The position in the Fibonacci sequence (must be >= 0)

    Returns:
        The nth Fibonacci number

    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


@tool
def get_weather(city: str) -> dict[str, Any]:
    """Get weather information for a city.

    Args:
        city: The name of the city

    Returns:
        Mock weather data for the city

    """
    # This is a mock implementation
    return {"city": city, "temperature": 72, "condition": "Sunny", "humidity": 45, "wind_speed": 10}


async def custom_tools_example():
    """Example using custom tools"""
    print("=" * 50)
    print("Custom Tools Example")
    print("=" * 50)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Create options with custom tools
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant with access to custom tools.",
        max_tokens=2048,
        api_key=api_key,
        # Tools will be automatically discovered from decorated functions
    )

    prompt = "What is the 10th Fibonacci number? Also, what's the weather like in San Francisco?"
    print(f"\nPrompt: {prompt}\n")
    print("Response:")
    print("-" * 50)

    async for message in query(prompt=prompt, options=options):
        print(message, end="", flush=True)

    print("\n" + "=" * 50)


async def main():
    """Run the example"""
    await custom_tools_example()


if __name__ == "__main__":
    asyncio.run(main())
