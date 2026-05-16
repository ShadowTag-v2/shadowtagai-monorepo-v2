# Vertex AI Live API Integration Guide

The **Gemini Live API** enables low-latency, two-way real-time voice and video interactions with Gemini. It supports continuous streaming of audio, video, and text inputs and returns audio and text responses.

## Quick References



- [WebSocket Guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/get-started-websocket)


- [SDK Guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/get-started-sdk)


- [API Overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## Connecting to the API

### Option 1: Using the Google Gen AI SDK (Recommended)

The SDK simplifies connection management and session handling.

**Prerequisites:**


- Python 3.10+


- `google-genai` package: `pip install google-genai`


- Google Cloud Project with Vertex AI API enabled.

**Basic Usage:**

```python
from google import genai
import asyncio

client = genai.Client(http_options={"api_version": "v1alpha"})
config = {"response_modalities": ["AUDIO"]}

async def main():
    async with client.aio.live.connect(model="gemini-3.1-flash-exp", config=config) as session:
        # interact with session
        pass

```

### Option 2: Using WebSockets

Direct WebSocket connections allow for broader platform support (e.g., direct from browser or non-SDK languages).

**Endpoint:**
`wss://us-central1-aiplatform.googleapis.com/ws/google.cloud.aiplatform.v1beta1.LlmService/StreamGenerateContent`

**Handshake:**
Must include a Bearer token in the `Authorization` header or query parameter (be careful with query params in logs).

## Implementation Details

### Audio Formats



- Input: PCM 16-bit, 16kHz or 24kHz (typically).


- Output: The API returns audio chunks that can be played back immediately.

### Tool Use during Live Sessions

You can register function calls (tools) that the model can invoke during the conversation. The client must execute the tool and send the result back to the model within the session.

## Demo

A complete example script is available at: `examples/vertex_live_api_demo.py`
