import asyncio
import os
import sys
import traceback

# Try to import google-genai, warn if missing
try:
    from google import genai
except ImportError:
    print("Error: 'google-genai' package is required.")
    print("Run: pip install google-genai")
    sys.exit(1)

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "acquired-jet-478701-b3")
LOCATION = "us-central1"
MODEL_ID = "gemini-3.1-flash-lite-preview"  # Or appropriate model version


async def main() -> None:
    """Demonstrates a basic connection to the Gemini Live API.
    This example establishes a session and sends a text message to trigger an audio response.
    """
    print("--- Vertex AI Live API Demo ---")
    print(f"Project: {PROJECT_ID}")
    print(f"Model: {MODEL_ID}")

    # Initialize Client
    # Note: Ensure you have authenticated with `gcloud auth application-default login`
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        http_options={"api_version": "v1alpha"},
    )

    config = {"response_modalities": ["AUDIO"]}

    try:
        print(f"Connecting to {MODEL_ID}...")
        async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
            print("✅ Connected to Gemini Live Session!")

            # Example: Send a text message to start the conversation
            initial_msg = "Hello! Please introduce yourself briefly."
            print(f"Sending: {initial_msg}")

            await session.send(initial_msg, end_of_turn=True)

            print("Listening for response (audio chunks)...")
            async for response in session.receive():
                # In a real app, you would buffer and play audio here.
                # Response structure depends on the SDK version, but typically contains data chunks.
                if response.data:
                    print(f"Received data chunk: {len(response.data)} bytes")

                # Check for text transcript if enabled/available
                if hasattr(response, "text") and response.text:
                    print(f"Transcript: {response.text}")

    except Exception as e:
        print(f"\n❌ Application Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
