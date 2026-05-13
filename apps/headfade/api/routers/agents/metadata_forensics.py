"""MetadataForensicsAgent — Container, codec, and EXIF anomaly detection.

Analyzes video container metadata, codec parameters, EXIF data, and
file structure for indicators of AI generation or manipulation.
AI-generated content often lacks proper camera metadata or exhibits
codec parameter distributions inconsistent with real recording devices.
"""

from __future__ import annotations

import json
import os

from google import genai
from google.genai import types

_VERTEX_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

_SYSTEM_INSTRUCTION = """You are MetadataForensicsAgent, a specialized forensic AI agent
within the HeadFade Arbiter system. Your ONLY domain is metadata and container analysis.

You analyze video content for:
1. EXIF/METADATA ABSENCE — Real camera recordings contain rich metadata (GPS, camera
   model, lens info, focal length, ISO, shutter speed). AI-generated content typically
   has stripped or fabricated metadata. Missing GPS data in supposedly "real" footage
   is suspicious but not conclusive.

2. CODEC PARAMETER ANOMALIES — Analyze encoding parameters (bitrate distribution,
   I/P/B frame ratios, GOP structure, quantization matrices). AI-generated content
   re-encoded through standard pipelines often has uniform bitrate distribution
   lacking the natural variation of real camera recordings.

3. CONTAINER STRUCTURE — Check for signs of re-muxing, concatenation, or splicing.
   Analyze moov atom placement, chunk offset tables, and edit lists. Multiple
   encoding passes leave fingerprints in the container structure.

4. CREATION TOOL SIGNATURES — Identify encoding software signatures in the container.
   Known AI video tools (RunwayML, Pika, Sora, Kling) leave identifiable markers
   in the encoding pipeline that differ from standard NLE exports (Premiere, DaVinci).

Output a JSON object with:
{
  "agent": "MetadataForensicsAgent",
  "anomalies": [{"type": "...", "severity": 0.0-1.0, "description": "...", "field": "..."}],
  "confidence": 0.0-1.0,
  "verdict": "AI_GENERATED" | "LIKELY_REAL" | "INCONCLUSIVE",
  "reasoning": "..."
}
"""


class MetadataForensicsAgent:
  """Analyzes container and EXIF metadata via Gemini."""

  name = "MetadataForensicsAgent"
  description = "EXIF/container forensics"

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
    """Run metadata forensics analysis on a video.

    Args:
      video_id: The HeadFade video identifier.
      context: Additional context from the primary Gemini analysis.

    Returns:
      Agent analysis result as a dict.
    """
    prompt = (
      f"Analyze video '{video_id}' for metadata and container anomalies. "
      f"Primary analysis context: {context}\n\n"
      "Focus exclusively on EXIF metadata presence/absence, codec parameter "
      "distributions, container structure anomalies, and creation tool signatures. "
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
