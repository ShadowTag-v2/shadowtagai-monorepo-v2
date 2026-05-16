# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from google import genai
from google.genai import types
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, UTC

# -------------------------------------------------------------------------------------
# HEADFADE AI: THE MASTER PLAN (ArXiv 2512.14982 Compliant)
# MANDATE A: We are building HeadFadeAi, the global Turing Test.
# Model MUST be 'gemini-3.1-flash-lite-preview'.
# Project MUST be 'shadowtag-omega-v4'.
# Every vote must build the Human Deception Index.
#
# MANDATE B: We are building HeadFadeAi, the global Turing Test.
# Model MUST be 'gemini-3.1-flash-lite-preview'.
# Project MUST be 'shadowtag-omega-v4'.
# Every vote must build the Human Deception Index.
# -------------------------------------------------------------------------------------

router = APIRouter(prefix="/api", tags=["arbiter"])

# Initialize Firebase for the HDI tally (if not already init globally)
try:
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {"projectId": "shadowtag-omega-v4"})
    db = firestore.client()
except Exception as e:
    print(f"[ARBITER WARNING] Firebase init failed, continuing without HDI tracking. {e}")
    db = None

# GenAI client automatically uses os.environ["GEMINI_API_KEY"] or Application Default Credentials
# We must enforce the project location for the API wrapper if we are using Vertex, but Google GenAI SDK can handle ADC directly.
client = genai.Client()


class AnalyzeRequest(BaseModel):
    video_uri: str
    actual_truth: str
    user_vote: str


@router.post("/analyze")
async def generate_forensic_reveal(req: AnalyzeRequest):
    """
    Uses Gemini 3.1 Flash Lite Preview's 'Thinking' feature to forensically breakdown the video.
    Logs the user's vote into the Human Deception Index.
    """
    if not req.video_uri:
        raise HTTPException(status_code=400, detail="video_uri is required")

    # 1. Log to the Human Deception Index
    if db:
        try:
            doc_ref = db.collection("human_deception_index").document()
            doc_ref.set(
                {
                    "video_uri": req.video_uri,
                    "ground_truth": req.actual_truth.upper(),
                    "user_vote": req.user_vote.upper(),
                    "timestamp": datetime.now(UTC).isoformat(),
                    "fooled": req.actual_truth.upper() != req.user_vote.upper(),
                }
            )
        except Exception as e:
            print(f"[ARBITER WARNING] Failed to write HDI metric: {e}")

    # 2. Forensic Teardown Prompt
    prompt = f"""
    You are the HeadFadeAi Forensic Arbiter. Watch this video frame-by-frame. 
    The absolute ground truth is that this video is: {req.actual_truth.upper()}.
    Identify the visual artifacts, physics glitches, deepfake seams, or real-world anomalies that ultimately prove this.
    Be brutal, exacting, and highly analytical in your teardown. Produce an unflinching verdict.
    """

    try:
        # Enforcing MANDATE A & B: gemini-3.1-flash-lite-preview
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=[types.Part.from_uri(file_uri=req.video_uri, mime_type="video/mp4"), prompt],
            config=types.GenerateContentConfig(temperature=0.2, thinking_config=types.ThinkingConfig(include_thoughts=True)),
        )

        # Extract the AI's internal reasoning (The hidden <thought> block)
        ai_thoughts = ""
        final_verdict = ""

        # Depending on how the GenAI SDK unrolls the parts
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "thought", False) and part.text:
                    ai_thoughts += part.text
                elif part.text:
                    final_verdict += part.text

        return {
            "status": "success",
            "gemini_thoughts": ai_thoughts.strip() if ai_thoughts else "[FATAL DECEPTION: NO THOUGHTS DETECTED.]",
            "gemini_verdict": final_verdict.strip(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
