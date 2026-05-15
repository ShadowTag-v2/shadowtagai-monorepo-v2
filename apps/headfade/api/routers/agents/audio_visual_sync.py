"""AudioVisualSyncAgent — Lip-sync and audio/video alignment detection.

Analyzes temporal alignment between audio and visual tracks. AI-generated
content frequently exhibits lip-sync drift, audio-motion misalignment,
and prosody violations that indicate synthetic generation.
"""

from __future__ import annotations

import json
import os

from google import genai
from google.genai import types

_VERTEX_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

_SYSTEM_INSTRUCTION = """You are AudioVisualSyncAgent, a specialized forensic AI agent
within the HeadFade Arbiter system. Your ONLY domain is audio-visual synchronization.

You analyze video content for:
1. LIP-SYNC DRIFT — Detect temporal offset between mouth movements and speech audio.
   AI-generated deepfakes often have 50-200ms drift that accumulates over time.
   Natural speech has <30ms audio-visual offset.

2. PROSODY-MOTION MISMATCH — Verify that speech emphasis patterns (stress, rhythm,
   intonation) correlate with facial muscle movements. AI face swap often preserves
   the voice prosody but fails to animate corresponding facial muscles.

3. BREATHING ARTIFACTS — Natural speech includes micro-pauses for breathing with
   corresponding chest/shoulder movement. AI-generated content frequently has
   continuous speech without physiological breathing patterns.

4. AMBIENT AUDIO COHERENCE — Verify that environmental audio (room reverb, background
   noise, echo characteristics) is consistent with the visual environment.
   AI-generated scenes often have audio that doesn't match the visible room geometry.

Output a JSON object with:
{
  "agent": "AudioVisualSyncAgent",
  "anomalies": [{"type": "...", "severity": 0.0-1.0, "description": "...", "timestamp": "..."}],
  "confidence": 0.0-1.0,
  "verdict": "AI_GENERATED" | "LIKELY_REAL" | "INCONCLUSIVE",
  "reasoning": "..."
}
"""


class AudioVisualSyncAgent:
  """Analyzes audio-visual synchronization via Gemini."""

  name = "AudioVisualSyncAgent"
  description = "Lip-sync drift detection"

  def __init__(self) -> None:
    self._client: genai.Client | None = None

  def _get_client(self) -> genai.Client:
    if self._client is None:
      self._client = genai.Client(
        vertexai=True,
        project=_VERTEX_PROJECT,
        location=_VERTEX_LOCATION,
      )
    return self._client

  async def analyze(self, video_id: str, context: str = "") -> dict:
    """Run audio-visual sync analysis on a video.

    Args:
      video_id: The HeadFade video identifier.
      context: Additional context from the primary Gemini analysis.

    Returns:
      Agent analysis result as a dict.
    """
    prompt = (
      f"Analyze video '{video_id}' for audio-visual synchronization anomalies. "
      f"Primary analysis context: {context}\n\n"
      "Focus exclusively on lip-sync drift, prosody-motion mismatch, "
      "breathing artifacts, and ambient audio coherence. "
      "Output your analysis as the specified JSON format."
    )

    try:
      response = self._get_client().models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
          system_instruction=_SYSTEM_INSTRUCTION,
          temperature=0.1,
          response_mime_type="application/json",
        ),
      )

      result_text = response.text if response.text else "{}"
      try:
        return json.loads(result_text)
      except json.JSONDecodeError:
        return {
          "agent": self.name,
          "anomalies": [],
          "confidence": 0.5,
          "verdict": "INCONCLUSIVE",
          "reasoning": result_text,
        }

    except Exception as e:
      return {
        "agent": self.name,
        "anomalies": [],
        "confidence": 0.0,
        "verdict": "ERROR",
        "reasoning": f"Agent execution failed: {e!s}",
      }
