"""HeadFade Arbiter Engine — A2UI Protocol SSE Streaming.

Implements the AG-UI (Agent-UI) lifecycle protocol for real-time
forensic analysis streaming. The A2UI standard enables the PWA
to render generative UI components (confidence meters, forensic
heatmaps, remix tree visualizations) driven by the arbiter's output.

A2UI Event Types:
  lifecycle.run.started    → Run initialization with agent metadata
  text.message.content     → Streaming text delta (thoughts + verdict)
  tool.call.started        → ADK sub-agent invocation begin
  tool.call.finished       → ADK sub-agent result
  state.snapshot           → UI component state (confidence, phase)
  lifecycle.run.finished   → Terminal event with final result
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types

from routers.agents import (
  AudioVisualSyncAgent,
  MetadataForensicsAgent,
  PhysicsSimulationAgent,
  TemporalCoherenceAgent,
)

router = APIRouter()

# -------------------------------------------------------------------------------------
# ADK Forensic Agent Fleet — instantiated once, reused across requests.
# Each agent wraps a specialized Gemini call with domain-specific system prompts.
# -------------------------------------------------------------------------------------
_agent_fleet = {
  "TemporalCoherenceAgent": TemporalCoherenceAgent(),
  "PhysicsSimulationAgent": PhysicsSimulationAgent(),
  "AudioVisualSyncAgent": AudioVisualSyncAgent(),
  "MetadataForensicsAgent": MetadataForensicsAgent(),
}

# -------------------------------------------------------------------------------------
# Vertex AI Client — uses ADC (Application Default Credentials), NOT API keys.
# API keys cannot access GCS URIs (gs://) and violate Secrets Manager Doctrine.
# -------------------------------------------------------------------------------------
_VERTEX_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

_client = None


def _get_genai_client() -> genai.Client:
  global _client
  if _client is None:
    _client = genai.Client(
      vertexai=True,
      project=_VERTEX_PROJECT,
      location=_VERTEX_LOCATION,
    )
  return _client


def _a2ui_event(event_type: str, **payload) -> str:
  """Format an A2UI-compliant SSE event."""
  data = {"type": event_type, **payload}
  return f"data: {json.dumps(data)}\n\n"


@router.post("/{video_id}")
async def run_forensic_arbiter(video_id: str, vote: str):
  """A2UI-compliant forensic analysis pipeline.

  Run 1: Gemini 3.1 Flash Lite Thinking — multimodal forensic teardown.
  Run 2: ADK Recursive sub-agents if confidence is below threshold.

  All events conform to the A2UI lifecycle protocol:
    lifecycle.run.started → text.message.content → state.snapshot →
    tool.call.started → tool.call.finished → lifecycle.run.finished
  """
  run_id = str(uuid.uuid4())

  async def event_stream():
    # ── A2UI: Run Start ──────────────────────────────────────────────
    yield _a2ui_event(
      "lifecycle.run.started",
      runId=run_id,
      agentName="forensic-arbiter",
      metadata={"videoId": video_id, "userVote": vote},
    )

    # ── A2UI: State Snapshot — Initial Phase ─────────────────────────
    yield _a2ui_event(
      "state.snapshot",
      runId=run_id,
      state={
        "phase": "GEMINI_FORENSICS",
        "confidence": 0.0,
        "agentsInvoked": 0,
        "videoId": video_id,
      },
    )

    prompt = (
      f"Ground Truth is in metadata. User voted {vote}. "
      "Forensically break down this video's physics. Be arrogant."
    )

    try:
      # We mock the video URI for the MVP scaffold, expecting Media CDN integration.
      # Note: We omit the actual file part for this scaffolding code
      # since we do not have an active GCS bucket with the asset.
      response_stream = _get_genai_client().models.generate_content_stream(
        model="gemini-3.1-flash-lite-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
          temperature=0.1,
          thinking_config=types.ThinkingConfig(include_thoughts=True),
        ),
      )

      confidence_score = 1.0
      for chunk in response_stream:
        # A2UI: text.message.content — streaming thoughts as deltas
        candidates = getattr(chunk, "candidates", None)
        if candidates and len(candidates) > 0:
          content = getattr(candidates[0], "content", None)
          parts = getattr(content, "parts", None) if content else None
          if parts:
            for part in parts:
              if getattr(part, "thought", False) and getattr(part, "text", None):
                yield _a2ui_event(
                  "text.message.content",
                  runId=run_id,
                  delta=part.text,
                  messageType="thought",
                )
              elif getattr(part, "text", None):
                yield _a2ui_event(
                  "text.message.content",
                  runId=run_id,
                  delta=part.text,
                  messageType="verdict",
                )

        # Theoretical confidence flag mapping for ADK fallback
        confidence_score = getattr(chunk, "confidence", 1.0)
        await asyncio.sleep(0.01)

      # ── A2UI: State Snapshot — Post-Gemini ───────────────────────────
      yield _a2ui_event(
        "state.snapshot",
        runId=run_id,
        state={
          "phase": "GEMINI_COMPLETE",
          "confidence": confidence_score,
          "agentsInvoked": 1,
        },
      )

      # ── Run 2: ADK Recursive Challenger ────────────────────────────
      # Invoked when Gemini's confidence is below the juke threshold.
      # Each sub-agent is tracked with tool.call.started/finished events.
      if confidence_score < 0.85:
        # Emit tool.call.started for all agents
        agent_calls = {}
        for agent_name, agent_instance in _agent_fleet.items():
          tool_call_id = str(uuid.uuid4())
          agent_calls[agent_name] = {
            "tool_call_id": tool_call_id,
            "instance": agent_instance,
          }
          yield _a2ui_event(
            "tool.call.started",
            runId=run_id,
            toolCallId=tool_call_id,
            toolName=agent_name,
            toolDescription=agent_instance.description,
          )

        # Execute all 4 agents concurrently
        agent_tasks = {
          name: info["instance"].analyze(
            video_id, context=f"Primary arbiter confidence: {confidence_score}"
          )
          for name, info in agent_calls.items()
        }
        results = await asyncio.gather(*agent_tasks.values(), return_exceptions=True)
        agent_results = dict(zip(agent_tasks.keys(), results))

        # Stream results and fuse confidence
        fused_confidences = []
        for agent_name, result in agent_results.items():
          tool_call_id = agent_calls[agent_name]["tool_call_id"]

          if isinstance(result, Exception):
            result = {
              "agent": agent_name,
              "confidence": 0.0,
              "verdict": "ERROR",
              "reasoning": str(result),
            }

          agent_confidence = result.get("confidence", 0.5)
          fused_confidences.append(agent_confidence)

          yield _a2ui_event(
            "tool.call.finished",
            runId=run_id,
            toolCallId=tool_call_id,
            toolName=agent_name,
            result=result,
          )

        # Weighted average fusion — all agents equally weighted for now
        fused_confidence = (
          sum(fused_confidences) / len(fused_confidences)
          if fused_confidences
          else confidence_score
        )

        # ── A2UI: State Snapshot — Post-ADK ──────────────────────────
        yield _a2ui_event(
          "state.snapshot",
          runId=run_id,
          state={
            "phase": "ADK_COMPLETE",
            "confidence": fused_confidence,
            "agentsInvoked": 1 + len(_agent_fleet),
            "agentResults": {
              name: {
                "verdict": r.get("verdict", "UNKNOWN")
                if isinstance(r, dict)
                else "ERROR",
                "confidence": r.get("confidence", 0.0) if isinstance(r, dict) else 0.0,
              }
              for name, r in agent_results.items()
            },
          },
        )

      # ── A2UI: Run Finished ─────────────────────────────────────────
      yield _a2ui_event(
        "lifecycle.run.finished",
        runId=run_id,
        result="YOU GOT JUKED.",
        finalConfidence=confidence_score,
      )

    except Exception as e:
      yield _a2ui_event(
        "lifecycle.run.finished",
        runId=run_id,
        result="ERROR",
        error=str(e),
      )

  return StreamingResponse(event_stream(), media_type="text/event-stream")
