"""PhysicsSimulationAgent — Lighting and shadow geometry validation.

Analyzes physical plausibility of lighting, shadows, reflections,
and material properties. AI-generated content frequently violates
the single-light-source constraint and produces physically impossible
shadow trajectories.
"""

from __future__ import annotations

import json
import os

from google import genai
from google.genai import types

_VERTEX_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

_SYSTEM_INSTRUCTION = """You are PhysicsSimulationAgent, a specialized forensic AI agent
within the HeadFade Arbiter system. Your ONLY domain is physics-based analysis.

You analyze video content for:
1. SHADOW TRAJECTORY ANALYSIS — Verify shadow directions are consistent with a single
   primary light source throughout the scene. AI models frequently generate shadows
   that point in multiple incompatible directions.

2. REFLECTION CONSISTENCY — Check that reflective surfaces (eyes, glass, water, metal)
   show geometrically correct reflections. Diffusion models often hallucinate reflections
   that don't match the surrounding environment.

3. LIGHT SOURCE GEOMETRY — Verify specular highlights, diffuse shading, and ambient
   occlusion are physically consistent. Multiple phantom light sources are a strong
   indicator of AI generation.

4. MATERIAL PHYSICS — Check that materials behave physically: hair should have
   individual strand motion, fabric should drape with gravity, liquids should have
   proper surface tension and refraction.

Output a JSON object with:
{
  "agent": "PhysicsSimulationAgent",
  "anomalies": [{"type": "...", "severity": 0.0-1.0, "description": "...", "region": "..."}],
  "confidence": 0.0-1.0,
  "verdict": "AI_GENERATED" | "LIKELY_REAL" | "INCONCLUSIVE",
  "reasoning": "..."
}
"""


class PhysicsSimulationAgent:
  """Analyzes physical plausibility of lighting and shadows via Gemini."""

  name = "PhysicsSimulationAgent"
  description = "Lighting/shadow geometry validation"

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
    """Run physics simulation analysis on a video.

    Args:
      video_id: The HeadFade video identifier.
      context: Additional context from the primary Gemini analysis.

    Returns:
      Agent analysis result as a dict.
    """
    prompt = (
      f"Analyze video '{video_id}' for physics violations. "
      f"Primary analysis context: {context}\n\n"
      "Focus exclusively on shadow trajectory consistency, reflection geometry, "
      "light source validation, and material physics plausibility. "
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
