# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Basic usage example for Vertex AI Agents
Demonstrates how to load and use agents with Vertex AI
"""

import os
import sys

from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

# Add parent directory to path to import agent_registry
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_registry import get_agent, get_agents_by_category, search_agents


def setup_vertex_ai():
    """Initialize Vertex AI"""
    aiplatform.init(
        project=os.getenv("VERTEX_AI_PROJECT_ID", "your-project-id"),
        location=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
    )


def example_use_single_agent():
    """Example: Using a single agent"""
    print("=" * 60)
    print("Example 1: Using a single agent")
    print("=" * 60)

    # Get the System Architect agent
    agent = get_agent("system-architect")

    print(f"\nAgent: {agent.name}")
    print(f"Description: {agent.description}")
    print("\nCapabilities:")
    for cap in agent.capabilities:
        print(f"  - {cap}")

    # Create a Gemini model with the agent's system prompt
    model = GenerativeModel(agent.model, system_instruction=agent.system_prompt)

    # Generate a response
    user_prompt = "Analyze our codebase architecture and suggest improvements"

    response = model.generate_content(
        user_prompt,
        generation_config={
            "temperature": agent.temperature,
            "max_output_tokens": agent.max_tokens,
        },
    )

    print(f"\nUser: {user_prompt}")
    print(f"\nAgent Response:\n{response.text}")


def example_search_agents():
    """Example: Searching for agents"""
    print("\n" + "=" * 60)
    print("Example 2: Searching for agents")
    print("=" * 60)

    # Search for agents related to "API"
    results = search_agents("API")

    print(f"\nFound {len(results)} agents related to 'API':")
    for agent in results:
        print(f"\n  {agent.icon} {agent.name}")
        print(f"     {agent.description}")
        print(f"     Category: {agent.category}")


def example_browse_by_category():
    """Example: Browse agents by category"""
    print("\n" + "=" * 60)
    print("Example 3: Browse agents by category")
    print("=" * 60)

    # Get all development agents
    dev_agents = get_agents_by_category("development")

    print(f"\nDevelopment Category ({len(dev_agents)} agents):")
    for agent in dev_agents:
        print(f"\n  {agent.icon} {agent.name}")
        print(f"     {agent.description}")
        print(f"     Example: {agent.example_prompts[0]}")


def example_multi_agent_workflow():
    """Example: Multi-agent workflow"""
    print("\n" + "=" * 60)
    print("Example 4: Multi-agent workflow")
    print("=" * 60)

    # Step 1: Use System Architect to design
    architect = get_agent("system-architect")
    print(f"\n1. {architect.name}: Designing system architecture...")

    # Step 2: Use Code Refactorer to clean code
    refactorer = get_agent("code-refactorer")
    print(f"2. {refactorer.name}: Refactoring code...")

    # Step 3: Use Test Generator to add tests
    tester = get_agent("test-generator")
    print(f"3. {tester.name}: Generating tests...")

    # Step 4: Use Security Scanner to audit
    security = get_agent("security-scanner")
    print(f"4. {security.name}: Scanning for vulnerabilities...")

    print("\nMulti-agent workflow completed!")


def example_agent_with_context():
    """Example: Using an agent with conversation context"""
    print("\n" + "=" * 60)
    print("Example 5: Using an agent with conversation context")
    print("=" * 60)

    # Get the Code Mentor agent
    mentor = get_agent("code-mentor")

    # Create model with system instruction
    model = GenerativeModel(mentor.model, system_instruction=mentor.system_prompt)

    # Start a chat session
    chat = model.start_chat()

    # Multi-turn conversation
    conversations = [
        "What are SOLID principles?",
        "Can you give me an example of the Single Responsibility Principle?",
        "How would I refactor this code to follow SRP?",
    ]

    print(f"\n{mentor.icon} {mentor.name} - Teaching Session\n")

    for user_message in conversations:
        response = chat.send_message(
            user_message,
            generation_config={
                "temperature": mentor.temperature,
                "max_output_tokens": mentor.max_tokens,
            },
        )

        print(f"Student: {user_message}")
        print(f"Mentor: {response.text}\n")


def main():
    """Run all examples"""
    # Setup
    setup_vertex_ai()

    # Run examples
    try:
        example_use_single_agent()
        example_search_agents()
        example_browse_by_category()
        example_multi_agent_workflow()
        example_agent_with_context()
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have:")
        print("  1. Set up VERTEX_AI_PROJECT_ID environment variable")
        print("  2. Authenticated with Google Cloud")
        print("  3. Installed required dependencies")


if __name__ == "__main__":
    main()
