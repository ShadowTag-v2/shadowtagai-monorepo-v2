#!/usr/bin/env python3
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
import uuid
from typing import Literal, Optional

from dotenv import load_dotenv
from fastmcp import FastMCP
from google import genai
from google.genai import types


# ===== CONFIG =====
GCS_BUCKET = os.getenv("GCS_MEDIA_BUCKET", "shadowtag-omega-v4-media")
AUTHORIZED_URI = "https://storage.mtls.cloud.google.com/"
MAX_RETRIES = 5


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
    source_image_gcs_uri: Optional[str] = None,
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
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[content],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
            ),
        )

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


# ===== VIDEO GENERATION (Veo 3.1) =====
async def generate_video(
    prompt: str,
    start_frame_gcs_uri: Optional[str] = None,
    duration_seconds: int = 8,
    model: Literal["veo-3.1", "veo-3.1-fast", "veo-3.1-lite", "veo-3.0"] = "veo-3.1",
) -> dict:
    """Generate a video using Veo 3.1 (Google-native, NOT Kling).

    Args:
        prompt: Video generation prompt describing motion and atmosphere.
        start_frame_gcs_uri: Optional GCS URI of a start frame image (i2v mode).
        duration_seconds: Video duration in seconds (max 8 for Veo 3.1).
        model: Veo model tier to use.

    Returns:
        Dict with 'uri' (GCS URI of generated video) or 'error' message.
    """
    # NOTE: Veo 3.1 API is accessed via google-genai SDK (Vertex AI)
    # The exact API surface may vary — this scaffold follows the pattern from
    # the google-genai SDK documentation for video generation.
    try:
        client = genai.Client()

        generate_config = {
            "prompt": prompt,
            "duration_seconds": min(duration_seconds, 8),
        }

        if start_frame_gcs_uri:
            generate_config["image"] = {"gcs_uri": start_frame_gcs_uri}

        # Veo video generation via Vertex AI
        # Actual API call pattern depends on google-genai SDK version
        logging.info(
            f"Video generation requested: model={model}, "
            f"duration={duration_seconds}s, i2v={'yes' if start_frame_gcs_uri else 'no'}"
        )

        return {
            "status": "scaffold",
            "message": (
                f"Veo {model} video generation scaffolded. "
                f"Wire to Vertex AI API when google-genai SDK >=1.66.0 "
                f"exposes veo_generate_video()."
            ),
            "config": generate_config,
        }

    except Exception as e:
        logging.exception("Video generation failed")
        return {"error": str(e)}


# ===== MCP SERVER =====
tools = [generate_image, generate_video]
mcp = FastMCP(name="MediaGenerators", tools=tools)


if __name__ == "__main__":
    load_dotenv()
    _init_logging()
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    logging.info(f"Starting MediaGenerators MCP on {host}:{port}")
    logging.info(f"GCS bucket: {GCS_BUCKET}")
    logging.info(f"Tools: {[t.__name__ for t in tools]}")
    mcp.run(transport="http", host=host, port=port)
