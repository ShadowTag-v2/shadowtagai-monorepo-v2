from datetime import UTC, datetime

import firebase_admin
from fastapi import APIRouter, HTTPException
from firebase_admin import credentials, firestore
import os

from google import genai
from google.genai import types
from pydantic import BaseModel

# -------------------------------------------------------------------------------------
# HEADFADE: THE MASTER PLAN (ArXiv 2512.14982 Compliant)
# MANDATE A: We are building HeadFade, the global Turing Test.
# Model MUST be 'gemini-3.1-flash-lite-preview'.
# Project MUST be 'shadowtag-omega-v4'.
# Every vote must build the Human Deception Index.
#
# MANDATE B: We are building HeadFade, the global Turing Test.
# Model MUST be 'gemini-3.1-flash-lite-preview'.
# Project MUST be 'shadowtag-omega-v4'.
# Every vote must build the Human Deception Index.
# -------------------------------------------------------------------------------------

# Vertex AI project config — GCS URIs require Vertex AI, NOT AI Studio API keys
_VERTEX_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

router = APIRouter(prefix="/api", tags=["arbiter"])

# Initialize Firebase for the HDI tally (if not already init globally)
try:
  if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {"projectId": _VERTEX_PROJECT})
  db = firestore.client()
except Exception as e:
  print(f"[ARBITER WARNING] Firebase init failed, continuing without HDI tracking. {e}")
  db = None

# GenAI client: lazy-init to prevent module-level crash on Cloud Run startup
# Uses Vertex AI (ADC) for GCS URI access — API keys cannot access gs:// URIs
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


class AnalyzeRequest(BaseModel):
  video_id: str
  video_uri: str
  actual_truth: str
  user_vote: str
  vote_latency_ms: int = 0


@router.post("/analyze")
async def generate_forensic_reveal(req: AnalyzeRequest):
  """Uses Gemini 3.1 Flash Lite Preview's 'Thinking' feature to forensically breakdown the video.
  Logs the user's vote into the Human Deception Index and saves the verdict.
  """
  if not req.video_uri or not req.video_id:
    raise HTTPException(status_code=400, detail="video_uri and video_id are required")

  # 1. Log to the Human Deception Index (human_telemetry)
  if db:
    try:
      doc_ref = db.collection("human_telemetry").document()
      doc_ref.set(
        {
          "videoId": req.video_id,
          "userId": None,
          "userVote": req.user_vote.upper(),
          "actualTruth": req.actual_truth.upper(),
          "isCorrect": req.actual_truth.upper() == req.user_vote.upper(),
          "latencyMs": req.vote_latency_ms,
          "votedAt": datetime.now(UTC),
        },
      )
    except Exception as e:
      print(f"[ARBITER WARNING] Failed to write human_telemetry metric: {e}")

  # 2. Forensic Teardown Prompt
  prompt = f"""
    You are the HeadFade Forensic Arbiter. Watch this video frame-by-frame.
    The absolute ground truth is that this video is: {req.actual_truth.upper()}.
    Identify the visual artifacts, physics glitches, deepfake seams, or real-world anomalies that ultimately prove this.
    Be brutal, exacting, and highly analytical in your teardown. Produce an unflinching verdict.
    """

  try:
    start_time = datetime.now(UTC)
    # Enforcing MANDATE A & B: gemini-3.1-flash-lite-preview
    response = _get_genai_client().models.generate_content(
      model="gemini-3.1-flash-lite-preview",
      contents=[
        types.Part.from_uri(file_uri=req.video_uri, mime_type="video/mp4"),
        prompt,
      ],
      config=types.GenerateContentConfig(
        temperature=0.2,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
      ),
    )
    end_time = datetime.now(UTC)
    latency_ms = int((end_time - start_time).total_seconds() * 1000)

    # Extract the AI's internal reasoning (The hidden <thought> block)
    ai_thoughts = ""
    final_verdict = ""

    # Depending on how the GenAI SDK unrolls the parts
    if (
      response.candidates
      and response.candidates[0].content
      and response.candidates[0].content.parts
    ):
      for part in response.candidates[0].content.parts:
        if getattr(part, "thought", False) and part.text:
          ai_thoughts += part.text
        elif part.text:
          final_verdict += part.text

    gemini_thoughts = (
      ai_thoughts.strip() if ai_thoughts else "[FATAL DECEPTION: NO THOUGHTS DETECTED.]"
    )
    gemini_verdict = final_verdict.strip()

    # 3. Save forensic_verdict
    if db:
      try:
        verdict_ref = db.collection("forensic_verdicts").document()
        verdict_ref.set(
          {
            "id": verdict_ref.id,
            "videoId": req.video_id,
            "model": "gemini-3.1-flash-lite-preview",
            "geminiVerdict": gemini_verdict,
            "geminiThoughts": gemini_thoughts,
            "confidenceScore": 0.95,
            "latencyMs": latency_ms,
            "analyzedAt": datetime.now(UTC),
          }
        )
      except Exception as e:
        print(f"[ARBITER WARNING] Failed to write forensic_verdicts metric: {e}")

    return {
      "status": "success",
      "gemini_thoughts": gemini_thoughts,
      "gemini_verdict": gemini_verdict,
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # noqa: B904
