"""
Gemini Live Service - Real-time Multimodal Interaction

Implements the Gemini Live API (WebSocket-based) for low-latency audio/video streaming.
Uses the unified google-genai SDK.
"""

import asyncio
import logging
import os
from contextlib import suppress
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

logger = logging.getLogger(__name__)


class GeminiLiveService:
    """
    Manager for Gemini Live sessions.
    Handles persistent WebSocket connections to Gemini 2.0 Flash in Vertex AI.
    """

    def __init__(
        self,
        project_id: str | None = None,
        location: str = "us-central1",
        model_id: str = "gemini-2.0-flash-exp",
    ):
        """Initialize Gemini Live client"""
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "acquired-jet-478701-b3")
        self.location = location
        self.model_id = model_id
        self.knowledge_context: str | None = None

        if genai:
            self.client = genai.Client(
                vertexai=True, project=self.project_id, location=self.location
            )
        else:
            self.client = None
            logger.error("google-genai SDK not installed. Gemini Live will be unavailable.")

    def set_knowledge(self, knowledge: str):
        """Inject enterprise knowledge for Proactive Advisor mode."""
        self.knowledge_context = knowledge
        logger.info("Knowledge context injected into GeminiLiveService")

    async def start_session(self, config: dict[str, Any] | None = None) -> Any:
        """
        Starts a new Live session.
        Returns a session object that can be used for send/receive loop.
        """
        if not self.client:
            raise RuntimeError("Gemini Client not initialized")

        system_instruction = "You are a specialized Antigravity Proactive Advisor."
        if self.knowledge_context:
            system_instruction += (
                f"\n\nCONTEXT FOR DYNAMIC KNOWLEDGE INJECTION:\n{self.knowledge_context}"
            )

        live_config = {
            "generation_config": {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {"prebuilt_voice_config": {"voice_name": "Puck"}}
                },
            },
            "system_instruction": system_instruction,
        }

        if config:
            live_config.update(config)

        # Cast to Any to satisfy Pyright/Mypy for dynamic dict update
        from typing import cast

        typed_config = cast(Any, live_config)

        # Note: In a real FastAPI context, the caller will manage the context manager
        return self.client.aio.live.connect(model=self.model_id, config=typed_config)

    async def run_proxy(self, client_ws, gemini_session):
        """
        Proxy messages between the client (WebSocket) and Gemini (Live session).
        """

        async def send_to_gemini():
            try:
                async for message in client_ws:
                    # Message from client (base64 audio/video or text)
                    # For now, expecting JSON from client: {"realtime_input": {"media_chunks": [{"data": "...", "mime_type": "audio/pcm"}]}}
                    await gemini_session.send(message)
            except Exception as e:
                logger.error(f"Error in Gemini Live WebSocket (send_to_gemini): {e}", exc_info=True)
                with suppress(Exception):
                    await client_ws.close(code=1011, reason=str(e))

        async def receive_from_gemini():
            try:
                async for response in gemini_session.receive():
                    # Response from Gemini (base64 audio or text)
                    # Send back to client WebSocket
                    await client_ws.send_json(response.model_dump())
            except Exception as e:
                logger.error(
                    f"Error in Gemini Live WebSocket (receive_from_gemini): {e}", exc_info=True
                )
                with suppress(Exception):
                    await client_ws.close(code=1011, reason=str(e))

        await asyncio.gather(send_to_gemini(), receive_from_gemini())
