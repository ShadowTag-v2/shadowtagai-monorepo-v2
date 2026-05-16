"""TemporalCoherenceAgent — Frame-to-frame motion consistency analysis.

Analyzes optical flow vectors, temporal flicker, motion interpolation
artifacts, and frame boundary discontinuities. Specialized for detecting
AI-generated video that exhibits unnaturally smooth or jerky transitions.
"""

from __future__ import annotations

import json
import os

from google import genai
from google.genai import types

_VERTEX_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

_SYSTEM_INSTRUCTION = """You are TemporalCoherenceAgent, a specialized forensic AI agent
within the HeadFade Arbiter system. Your ONLY domain is temporal coherence analysis.

You analyze video content for:
1. OPTICAL FLOW DISCONTINUITY — Detect inconsistent motion vectors between consecutive
   frames. AI-generated content often has abrupt direction changes mid-motion that violate
   physical inertia. Report frame ranges with anomalous flow magnitude changes >2σ.

2. TEMPORAL FLICKER — Detect luminance/chrominance oscillations at frame boundaries.
   Diffusion model artifacts often produce micro-flicker at 2-4 frame intervals that
   are invisible to human perception but measurable via histogram analysis.

3. MOTION INTERPOLATION ARTIFACTS — Detect "floaty" motion characteristic of AI frame
   interpolation. Natural motion has micro-jitter from hand-held cameras and subject
   breathing. AI content is pathologically smooth.

4. FRAME BOUNDARY COHERENCE — Detect temporal seams where AI-generated segments are
   spliced into real footage. Look for abrupt changes in noise floor, color temperature,
   or motion blur characteristics.

Output a JSON object with:
{
  "agent": "TemporalCoherenceAgent",
  "anomalies": [{"type": "...", "severity": 0.0-1.0, "description": "...", "frame_range": "..."}],
  "confidence": 0.0-1.0,
  "verdict": "AI_GENERATED" | "LIKELY_REAL" | "INCONCLUSIVE",
  "reasoning": "..."
}
"""


class TemporalCoherenceAgent:
  """Analyzes temporal coherence of video frames via Gemini."""

  name = "TemporalCoherenceAgent"
  description = "Frame-to-frame consistency analysis"

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
    """Run temporal coherence analysis on a video.

    Args:
      video_id: The HeadFade video identifier.
      context: Additional context from the primary Gemini analysis.

    Returns:
      Agent analysis result as a dict.
    """
    prompt = (
      f"Analyze video '{video_id}' for temporal coherence anomalies. "
      f"Primary analysis context: {context}\n\n"
      "Focus exclusively on frame-to-frame motion consistency, optical flow "
      "discontinuities, temporal flicker, and motion interpolation artifacts. "
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
