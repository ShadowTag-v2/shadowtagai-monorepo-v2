"""HeadFade Studio — Voice Cloning + SynthID Watermarking.

Production pipeline for content creators:
  1. Google Cloud Text-to-Speech — voice synthesis
  2. SynthID watermark embedding — provenance tracking
  3. GCS upload → Media CDN — global edge delivery
  4. Embedding index for similarity search (future)
"""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from google.cloud import storage, texttospeech
from pydantic import BaseModel, Field

router = APIRouter()

_GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_CDN_BUCKET = os.environ.get("HEADFADE_CDN_BUCKET", "headfade-cdn-origin")


class ForgeRequest(BaseModel):
  """Voice cloning request from the HeadFade Studio UI."""

  session_id: str = Field(description="Unique session identifier for tracking")
  text: str = Field(description="Text to synthesize into speech")
  voice_profile: str = Field(
    description="Google TTS voice name (e.g., 'en-US-Neural2-D')"
  )
  prompt: str = Field(description="Original creator prompt for provenance")


class ForgeResponse(BaseModel):
  """Response with the GCS URI and watermark status."""

  status: str
  uri: str | None = None
  watermarked: bool = False
  message: str | None = None


@router.post("/clone-voice", response_model=ForgeResponse)
async def export_studio_video(payload: ForgeRequest) -> ForgeResponse:
  """Real-time voice cloning via Google TTS with SynthID provenance.

  Pipeline:
    1. Synthesize speech via Cloud Text-to-Speech API
    2. Apply SynthID watermark (when enterprise keys are active)
    3. Upload to GCS CDN origin bucket
  """
  try:
    # ── Stage 1: Google Cloud TTS Voice Synthesis ───────────────────
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_response = tts_client.synthesize_speech(
      input=texttospeech.SynthesisInput(text=payload.text),
      voice=texttospeech.VoiceSelectionParams(
        name=payload.voice_profile,
        language_code=payload.voice_profile[:5]
        if len(payload.voice_profile) >= 5
        else "en-US",
      ),
      audio_config=texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=24000,
      ),
    )
    audio_content = synthesis_response.audio_content

    if not audio_content:
      raise HTTPException(status_code=500, detail="TTS returned empty audio")

    # ── Stage 2: SynthID Watermark Embedding ────────────────────────
    # SynthID is Google DeepMind's invisible watermarking technology.
    # The enterprise API endpoint is gated behind Vertex AI Enterprise.
    # When the API is unavailable, we pass through unwatermarked and flag it.
    watermarked = False
    watermarked_media = audio_content

    # TODO(headfade): Enable when Vertex AI SynthID API is GA for audio.
    # The SynthID API for text is available via google-genai; audio watermarking
    # requires the enterprise watermark service endpoint.
    #
    # from google.cloud import aiplatform
    # aiplatform.init(project=_GCP_PROJECT)
    # watermark_client = aiplatform.gapic.WatermarkServiceClient()
    # watermarked_media = watermark_client.apply_watermark(
    #     media=audio_content,
    #     watermark_config={"tier": "enterprise", "keys": "headfade-master"}
    # )
    # watermarked = True

    # ── Stage 3: Upload to GCS CDN Origin ───────────────────────────
    storage_client = storage.Client(project=_GCP_PROJECT)
    bucket = storage_client.bucket(_CDN_BUCKET)
    blob = bucket.blob(f"exports/{payload.session_id}.wav")
    blob.upload_from_string(watermarked_media, content_type="audio/wav")
    blob.metadata = {
      "x-headfade-session": payload.session_id,
      "x-headfade-voice": payload.voice_profile,
      "x-headfade-watermarked": str(watermarked).lower(),
    }
    blob.patch()

    video_uri = f"gs://{_CDN_BUCKET}/exports/{payload.session_id}.wav"

    return ForgeResponse(
      status="success",
      uri=video_uri,
      watermarked=watermarked,
    )

  except HTTPException:
    raise
  except Exception as e:
    return ForgeResponse(
      status="error",
      watermarked=False,
      message=str(e),
    )
