import asyncio
import json
import os

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types

router = APIRouter()

# Initialize the Gemini GenAI Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


@router.post("/{video_id}")
async def run_forensic_arbiter(video_id: str, vote: str):
  """Run 1: Gemini 3 Flash Thinking. Streams via AG-UI Server-Sent Events.
  Run 2: ADK Recursive sub-agents if confidence is low.
  """

  async def event_stream():
    yield f"data: {json.dumps({'type': 'STEP_STARTED', 'name': 'GEMINI_FORENSICS'})}\n\n"

    prompt = f"Ground Truth is in metadata. User voted {vote}. Forensically break down this video's physics. Be arrogant."

    try:
      # We mock the video URI for the MVP scaffold, expecting Media CDN integration
      # Note: We omit the actual file part for this scaffolding code
      # since we do not have an active GCS bucket with the asset.
      response_stream = client.models.generate_content_stream(
        model="gemini-3.1-flash-lite-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
          temperature=0.1,
          thinking_config=types.ThinkingConfig(thinking_level=1, include_thoughts=True),  # type: ignore
        ),
      )

      confidence_score = 1.0
      for chunk in response_stream:
        # We yield the thoughts as AG-UI TEXT_MESSAGE_CONTENT
        candidates = getattr(chunk, "candidates", None)
        if candidates and len(candidates) > 0:
          content = getattr(candidates[0], "content", None)
          parts = getattr(content, "parts", None) if content else None
          if parts:
            for part in parts:
              if getattr(part, "thought", False) and getattr(part, "text", None):
                yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_CONTENT', 'delta': part.text})}\n\n"

        # We use a theoretical confidence flag mapping for ADK fallback
        confidence_score = getattr(chunk, "confidence", 1.0)
        await asyncio.sleep(0.01)

      # RUN 2: The ADK Recursive Challenger (Mocked until ADK is natively imported)
      if confidence_score < 0.85:
        yield f"data: {json.dumps({'type': 'STEP_STARTED', 'name': 'ADK_DEEP_PHYSICS_ANALYSIS'})}\n\n"
        deep_results = "ADK SUB-AGENTS CONFIRM SHADOW GEOMETRY VIOLATION. USER JUKED."
        yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_CONTENT', 'delta': deep_results})}\n\n"

      yield f"data: {json.dumps({'type': 'RUN_FINISHED', 'result': 'YOU GOT JUKED.'})}\n\n"

    except Exception as e:
      yield f"data: {json.dumps({'type': 'ERROR', 'message': str(e)})}\n\n"

  return StreamingResponse(event_stream(), media_type="text/event-stream")
