"""Example usage of the chat API endpoints."""

import asyncio

import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def simple_chat():
    """Simple chat completion example."""
    print("\n=== Simple Chat Example ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat/completions",
            json={
                "message": "What is FastAPI and why is it popular?",
                "temperature": 0.7,
                "model_provider": "anthropic",
            },
            timeout=30.0,
        )

        result = response.json()
        print(f"Session ID: {result['session_id']}")
        print(f"Response: {result['message']}")
        print(f"Model: {result['model']}")

        return result["session_id"]


async def conversation_with_context(session_id: str):
    """Continue a conversation using context."""
    print("\n=== Conversation with Context ===")

    async with httpx.AsyncClient() as client:
        # Ask a follow-up question that requires context
        response = await client.post(
            f"{BASE_URL}/chat/completions",
            json={
                "message": "Can you give me a code example?",
                "session_id": session_id,
                "temperature": 0.7,
            },
            timeout=30.0,
        )

        result = response.json()
        print(f"Follow-up Response: {result['message'][:200]}...")


async def streaming_chat():
    """Streaming chat example."""
    print("\n=== Streaming Chat Example ===")

    async with (
        httpx.AsyncClient() as client,
        client.stream(
            "POST",
            f"{BASE_URL}/chat/stream",
            json={
                "message": "Tell me a short story about a robot learning to code",
                "temperature": 0.9,
                "stream": True,
            },
            timeout=60.0,
        ) as response,
    ):
        print("Streaming response: ", end="", flush=True)
        async for chunk in response.aiter_text():
            print(chunk, end="", flush=True)
        print()


async def create_custom_conversation():
    """Create a conversation with custom settings."""
    print("\n=== Custom Conversation ===")

    async with httpx.AsyncClient() as client:
        # Create conversation with custom system prompt
        create_response = await client.post(
            f"{BASE_URL}/chat/conversations",
            json={
                "title": "Python Expert Session",
                "system_prompt": "You are an expert Python developer who specializes in clean code and best practices.",
                "model_provider": "anthropic",
            },
        )

        conversation = create_response.json()
        session_id = conversation["session_id"]
        print(f"Created conversation: {conversation['title']}")
        print(f"Session ID: {session_id}")

        # Send a message in this conversation
        chat_response = await client.post(
            f"{BASE_URL}/chat/completions",
            json={
                "message": "How should I structure a large Python project?",
                "session_id": session_id,
            },
            timeout=30.0,
        )

        result = chat_response.json()
        print(f"Response: {result['message'][:200]}...")

        return session_id


async def get_conversation_history(session_id: str):
    """Retrieve conversation history."""
    print("\n=== Conversation History ===")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/chat/conversations/{session_id}/messages")

        messages = response.json()
        print(f"Total messages: {len(messages)}")

        for i, msg in enumerate(messages, 1):
            print(f"\n{i}. [{msg['role']}]: {msg['content'][:100]}...")


async def main():
    """Run all examples."""
    try:
        # Simple chat
        session_id = await simple_chat()

        # Continue conversation
        await conversation_with_context(session_id)

        # Streaming chat
        await streaming_chat()

        # Custom conversation
        custom_session_id = await create_custom_conversation()

        # View history
        await get_conversation_history(custom_session_id)

        print("\n✅ All examples completed successfully!")

    except httpx.ConnectError:
        print("❌ Error: Could not connect to the API server.")
        print("   Make sure the server is running: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
