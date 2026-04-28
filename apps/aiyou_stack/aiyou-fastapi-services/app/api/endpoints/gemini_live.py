# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini Live API Endpoints

Exposes a WebSocket endpoint for real-time multimodal interaction.
"""

import contextlib
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.services.gemini_live_service import GeminiLiveService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/gemini-live")
async def gemini_live_websocket(websocket: WebSocket):
    """WebSocket proxy for Gemini Live API.

    Handles:
    1. Client connection
    2. Starting Gemini Live session in Vertex AI
    3. Bidirectional streaming of media and text
    """
    await websocket.accept()
    logger.info("Client connected to Gemini Live WebSocket")

    # Initialize service
    # Project ID is handled by ADC or env var in the service __init__
    service = GeminiLiveService(
        location=settings.GEMINI_LIVE_LOCATION,
        model_id=settings.GEMINI_LIVE_MODEL,
    )

    try:
        # Start the generative session
        async with await service.start_session() as session:
            logger.info("Gemini Live session started")

            # Proxy messages
            # Note: run_proxy handles the bidirectional loop
            await service.run_proxy(websocket, session)

    except WebSocketDisconnect:
        logger.info("Client disconnected from Gemini Live WebSocket")
    except Exception as e:
        logger.error(f"Error in Gemini Live WebSocket: {e}", exc_info=True)
        with contextlib.suppress(BaseException):
            await websocket.close(code=1011, reason=str(e))
