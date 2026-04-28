#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""media_mcp_server.py — Media Generation MCP Server.

Wraps Nano Banana Pro (Gemini 3 Pro Image) + Veo 3.1 video generation
into a FastMCP server for use by ADK agents and Antigravity.

Based on: devrel-demos/ai-ml/agent-factory-antigravity-nano-banana-pro/mcp/

Pipeline:
  Agent → MCP Tool Call → generate_image / generate_video → GCS → URI back

Requirements:
  pip install fastmcp google-genai google-cloud-storage python-dotenv
"""

import logging
import mimetypes
import os
import sys
import time
import uuid
from collections import defaultdict
from typing import Literal

from dotenv import load_dotenv
from fastmcp import FastMCP
from google import genai
from google.genai import types


# ===== CONFIG =====
GCS_BUCKET = os.getenv("GCS_MEDIA_BUCKET", "shadowtag-omega-v4-media")
AUTHORIZED_URI = "https://storage.mtls.cloud.google.com/"
MAX_RETRIES = 5
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8888,http://localhost:3000,https://shadowtagai.web.app,https://kovelai.web.app",
).split(",")

# Rate limiting: max requests per minute per IP
RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "30"))
_rate_limiter: dict[str, list[float]] = defaultdict(list)


# ===== LOGGING =====
def _init_logging(min_level: int = logging.INFO) -> None:
    """Split stdout/stderr logging."""
    h_info = logging.StreamHandler(sys.stdout)
    h_info.setLevel(logging.DEBUG)
    h_info.addFilter(lambda r: r.levelno <= logging.INFO)
    h_warn = logging.StreamHandler(sys.stderr)
    h_warn.setLevel(logging.WARNING)
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(message)s",
        level=min_level,
        handlers=[h_info, h_warn],
        force=True,
    )


# ===== SECURITY: Input Validation =====
def _validate_prompt(prompt: str, max_length: int = 2000) -> str:
    """Validate and sanitize prompt input."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    prompt = prompt.strip()
    if len(prompt) > max_length:
        raise ValueError(f"Prompt exceeds max length of {max_length} characters")
    return prompt


def _validate_gcs_uri(uri: str) -> str:
    """Validate GCS URI format."""
    if not uri.startswith("gs://"):
        raise ValueError(f"Invalid GCS URI format: {uri}")
    if ".." in uri or "\n" in uri:
        raise ValueError(f"GCS URI contains invalid characters: {uri}")
    return uri


def _check_rate_limit(client_id: str = "default") -> None:
    """Simple in-memory rate limiter."""
    now = time.time()
    window = 60.0  # 1 minute
    _rate_limiter[client_id] = [t for t in _rate_limiter[client_id] if now - t < window]
    if len(_rate_limiter[client_id]) >= RATE_LIMIT_RPM:
        raise ValueError(f"Rate limit exceeded: {RATE_LIMIT_RPM} requests per minute")
    _rate_limiter[client_id].append(now)


# ===== STORAGE =====
async def upload_to_gcs(
    prefix: str,
    data: bytes,
    mime_type: str,
) -> str:
    """Upload binary data to GCS and return the gs:// URI.

    Args:
        prefix: GCS path prefix (e.g., 'mcp-tools').
        data: Raw bytes to upload.
        mime_type: MIME type of the data.

    Returns:
        GCS URI string (gs://bucket/path).
    """
    from google.cloud import storage as gcs_storage

    client = gcs_storage.Client()
    bucket = client.bucket(GCS_BUCKET)

    ext = mimetypes.guess_extension(mime_type) or ".bin"
    blob_name = f"{prefix}/{uuid.uuid4().hex}{ext}"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data, content_type=mime_type)

    uri = f"gs://{GCS_BUCKET}/{blob_name}"
    logging.info(f"Uploaded to GCS: {uri}")
    return uri


# ===== IMAGE GENERATION (Nano Banana Pro) =====
async def generate_image(
    prompt: str,
    source_image_gcs_uri: str | None = None,
    aspect_ratio: Literal["16:9", "9:16"] = "16:9",
) -> dict:
    """Generate an image using Gemini 3 Pro Image (Nano Banana Pro).

    Args:
        prompt: Image generation prompt. May reference the source image.
        source_image_gcs_uri: Optional GCS URI of a source/reference image.
        aspect_ratio: Output aspect ratio. '16:9' or '9:16'.

    Returns:
        Dict with 'uri' (GCS URI of generated image) or 'error' message.
    """
    _check_rate_limit()
    prompt = _validate_prompt(prompt)

    if source_image_gcs_uri:
        source_image_gcs_uri = _validate_gcs_uri(source_image_gcs_uri)

    client = genai.Client()

    content = types.Content(
        parts=[types.Part.from_text(text=prompt)],
        role="user",
    )

    if source_image_gcs_uri:
        guessed_mime, _ = mimetypes.guess_type(source_image_gcs_uri)
        if not guessed_mime:
            return {"error": f"Cannot determine MIME type for {source_image_gcs_uri}"}
        content.parts.insert(
            0,
            types.Part(
                file_data=types.FileData(
                    file_uri=source_image_gcs_uri,
                    mime_type=guessed_mime,
                )
            ),
        )

    uri = ""
    response_text = ""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[content],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
                ),
            )
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == MAX_RETRIES - 1:
                return {"error": f"Image generation failed after {MAX_RETRIES} attempts: {e}"}
            continue

        if response and response.parts:
            for part in response.parts:
                if part.text and not part.thought:
                    response_text += part.text
                if part.file_data and part.file_data.file_uri:
                    uri = part.file_data.file_uri
                    break
                if part.inline_data and part.inline_data.data:
                    uri = await upload_to_gcs(
                        "mcp-images",
                        part.inline_data.data,
                        part.inline_data.mime_type,
                    )
                    break

        if uri:
            break
        if response_text:
            logging.warning(f"Attempt {attempt + 1}: {response_text}")

    if not uri:
        return {"error": "No image was generated after retries.", "model_response": response_text}

    # Convert gs:// to authenticated HTTPS URL
    public_uri = uri.replace("gs://", AUTHORIZED_URI)
    logging.info(f"Generated image: {public_uri}")
    return {"uri": public_uri, "gcs_uri": uri}


# ===== VIDEO GENERATION (Veo 3.1) — LIVE API =====
async def generate_video(
    prompt: str,
    start_frame_gcs_uri: str | None = None,
    duration_seconds: int = 8,
    model: Literal["veo-3.1", "veo-3.1-fast", "veo-3.1-lite", "veo-3.0"] = "veo-3.1",
    aspect_ratio: Literal["16:9", "9:16"] = "16:9",
) -> dict:
    """Generate a video using Veo 3.1 via Vertex AI (google-genai SDK).

    Args:
        prompt: Video generation prompt describing motion and atmosphere.
        start_frame_gcs_uri: Optional GCS URI of a start frame image (i2v mode).
        duration_seconds: Video duration in seconds (max 8 for Veo 3.1).
        model: Veo model tier to use.
        aspect_ratio: Output aspect ratio.

    Returns:
        Dict with 'uri' (GCS URI of generated video) or 'error' message.
    """
    _check_rate_limit()
    prompt = _validate_prompt(prompt, max_length=3000)

    if start_frame_gcs_uri:
        start_frame_gcs_uri = _validate_gcs_uri(start_frame_gcs_uri)

    # Map friendly names to API model IDs
    model_map = {
        "veo-3.1": "veo-3.1-generate-preview",
        "veo-3.1-fast": "veo-3.1-fast-generate-preview",
        "veo-3.1-lite": "veo-3.1-lite-generate-preview",
        "veo-3.0": "veo-3.0-generate-001",
    }
    api_model = model_map.get(model, "veo-3.1-generate-preview")

    try:
        client = genai.Client()

        # Build generation config
        generate_config = types.GenerateVideoConfig(
            aspect_ratio=aspect_ratio,
            output_gcs_uri=f"gs://{GCS_BUCKET}/mcp-videos/",
        )

        # Build content parts
        parts = [types.Part.from_text(text=prompt)]

        if start_frame_gcs_uri:
            guessed_mime, _ = mimetypes.guess_type(start_frame_gcs_uri)
            parts.insert(
                0,
                types.Part(
                    file_data=types.FileData(
                        file_uri=start_frame_gcs_uri,
                        mime_type=guessed_mime or "image/png",
                    )
                ),
            )

        logging.info(
            f"Video generation: model={api_model}, "
            f"duration={min(duration_seconds, 8)}s, "
            f"i2v={'yes' if start_frame_gcs_uri else 'no'}, "
            f"ratio={aspect_ratio}"
        )

        # Generate video (async operation)
        operation = client.models.generate_video(
            model=api_model,
            contents=parts,
            config=generate_config,
        )

        # Poll for completion
        import asyncio

        max_polls = 120  # 10 minutes max
        for poll in range(max_polls):
            result = client.operations.get(operation)
            if result.done:
                break
            logging.info(f"Video generation polling... ({poll + 1}/{max_polls})")
            await asyncio.sleep(5)

        if not result.done:
            return {"error": "Video generation timed out after 10 minutes"}

        # Extract video URI from result
        if result.response and result.response.generated_videos:
            video = result.response.generated_videos[0]
            video_uri = video.video.uri if video.video else None
            if video_uri:
                public_uri = video_uri.replace("gs://", AUTHORIZED_URI)
                logging.info(f"Generated video: {public_uri}")
                return {
                    "uri": public_uri,
                    "gcs_uri": video_uri,
                    "model": api_model,
                    "duration": min(duration_seconds, 8),
                }

        return {"error": "Video generation completed but no video was returned"}

    except Exception as e:
        logging.exception("Video generation failed")
        return {"error": str(e)}


# ===== GCS SIGNED URL GENERATION =====
async def get_signed_url(
    gcs_uri: str,
    expiration_minutes: int = 60,
) -> dict:
    """Generate a signed URL for a GCS object.

    Args:
        gcs_uri: GCS URI (gs://bucket/path).
        expiration_minutes: URL expiration time in minutes (max 7 days).

    Returns:
        Dict with 'signed_url' or 'error'.
    """
    import datetime

    from google.cloud import storage as gcs_storage

    gcs_uri = _validate_gcs_uri(gcs_uri)
    expiration_minutes = min(expiration_minutes, 10080)  # Max 7 days

    try:
        client = gcs_storage.Client()
        # Parse gs://bucket/path
        path = gcs_uri.replace("gs://", "")
        bucket_name, blob_name = path.split("/", 1)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            expiration=datetime.timedelta(minutes=expiration_minutes),
            method="GET",
        )
        return {"signed_url": url, "expires_in_minutes": expiration_minutes}

    except Exception as e:
        logging.exception("Signed URL generation failed")
        return {"error": str(e)}


# ===== MCP SERVER =====
tools = [generate_image, generate_video, get_signed_url]
mcp = FastMCP(name="MediaGenerators", tools=tools)


if __name__ == "__main__":
    load_dotenv()
    _init_logging()
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    logging.info(f"Starting MediaGenerators MCP on {host}:{port}")
    logging.info(f"GCS bucket: {GCS_BUCKET}")
    logging.info(f"CORS origins: {ALLOWED_ORIGINS}")
    logging.info(f"Rate limit: {RATE_LIMIT_RPM} RPM")
    logging.info(f"Tools: {[t.__name__ for t in tools]}")
    mcp.run(transport="http", host=host, port=port)
