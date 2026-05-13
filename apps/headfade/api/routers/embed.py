"""HeadFade Embed API — Zero-CAC Distribution Engine.

Powers the <iframe> Embed Player for publishers. When NYT/BBC/Substack
writes about a viral deepfake, they embed the HeadFade player instead
of a raw X/TikTok link.

Media CDN Integration:
  - Signed URLs with time-limited HMAC tokens (anti-hotlinking)
  - Cache-Control headers for viral load handling
  - HLS manifest URL generation for adaptive bitrate streaming
  - Geographic edge routing via Cloud CDN

Endpoints:
  GET  /api/embed/{video_id}        → Embed metadata for the iframe player
  POST /api/telemetry/embed-view    → Silent impression telemetry → BigQuery
"""

from __future__ import annotations

import datetime
import hashlib
import hmac
import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from google.cloud import bigquery, firestore
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["embed"])

# ── CDN Configuration ────────────────────────────────────────────────────────
_CDN_BASE_URL = os.environ.get(
  "HEADFADE_CDN_BASE_URL",
  "https://cdn.headfade.com",
)
_CDN_SIGNING_KEY = os.environ.get("HEADFADE_CDN_SIGNING_KEY", "")
_CDN_KEY_NAME = os.environ.get("HEADFADE_CDN_KEY_NAME", "headfade-cdn-key-v1")
_CDN_TOKEN_TTL_SECONDS = int(os.environ.get("HEADFADE_CDN_TOKEN_TTL", "3600"))

# Fallback to raw GCS when CDN is not configured
_GCS_FALLBACK_URL = "https://storage.googleapis.com/headfade-cdn-origin"

_db = None
_bq = None


def _get_db():
  global _db
  if _db is None:
    _db = firestore.Client(project="shadowtag-omega-v4")
  return _db


def _get_bq():
  global _bq
  if _bq is None:
    _bq = bigquery.Client(project="shadowtag-omega-v4")
  return _bq


def _generate_signed_cdn_url(video_id: str, *, fmt: str = "mp4") -> str:
  """Generate a time-limited signed Cloud CDN URL.

  Uses HMAC-SHA1 URL signing per Google Cloud CDN docs:
  https://cloud.google.com/cdn/docs/using-signed-urls

  Falls back to raw GCS URL when CDN signing key is not configured.
  """
  if not _CDN_SIGNING_KEY:
    return f"{_GCS_FALLBACK_URL}/{video_id}.{fmt}"

  url_prefix = f"{_CDN_BASE_URL}/media/{video_id}.{fmt}"
  expiration = int(
    (
      datetime.datetime.now(tz=datetime.UTC)
      + datetime.timedelta(seconds=_CDN_TOKEN_TTL_SECONDS)
    ).timestamp()
  )

  # Signed URL format: URL?Expires=X&KeyName=Y&Signature=Z
  unsigned = f"{url_prefix}?Expires={expiration}&KeyName={_CDN_KEY_NAME}"

  import base64

  decoded_key = base64.urlsafe_b64decode(_CDN_SIGNING_KEY)
  signature = hmac.new(decoded_key, unsigned.encode("utf-8"), hashlib.sha1).digest()
  encoded_signature = base64.urlsafe_b64encode(signature).decode("utf-8")

  return f"{unsigned}&Signature={encoded_signature}"


def _generate_hls_manifest_url(video_id: str) -> str | None:
  """Generate HLS manifest URL for adaptive bitrate streaming.

  Returns None when CDN is not configured (MVP fallback).
  """
  if not _CDN_SIGNING_KEY:
    return None
  return _generate_signed_cdn_url(video_id, fmt="m3u8")


class EmbedViewEvent(BaseModel):
  videoId: str
  referrer: str = ""
  timestamp: str = ""


@router.get("/embed/{video_id}")
async def get_embed_metadata(video_id: str):
  """Return lightweight metadata for the iframe embed player.

  Data flows: Firestore (video doc) + aggregated HDI score.
  Response is edge-cached by Cloud CDN for 60s to handle viral spikes.
  """
  db = _get_db()
  doc = db.collection("videos").document(video_id).get()

  if doc.exists:
    data = doc.to_dict()
    cdn_url = data.get("cdn_url") or _generate_signed_cdn_url(video_id)
    hls_url = _generate_hls_manifest_url(video_id)

    response_data = {
      "id": video_id,
      "cdnUrl": cdn_url,
      "models": data.get("detected_models", ["Unknown"]),
      "hdiScore": data.get("hdi_score", 0),
      "parentCreator": data.get("parent_creator", "original"),
      "remixDepth": data.get("remix_depth", 0),
      "title": data.get("title", "Synthetic Media"),
    }
    if hls_url:
      response_data["hlsUrl"] = hls_url

    return JSONResponse(
      content=response_data,
      headers={
        "Cache-Control": "public, max-age=60, s-maxage=60",
        "CDN-Cache-Control": "public, max-age=3600",
        "Vary": "Accept-Encoding",
      },
    )

  # Fallback for videos not yet in Firestore
  return JSONResponse(
    content={
      "id": video_id,
      "cdnUrl": _generate_signed_cdn_url(video_id),
      "models": ["Pending Analysis"],
      "hdiScore": 0,
      "parentCreator": "unknown",
      "remixDepth": 0,
      "title": "Synthetic Media Specimen",
    },
    headers={
      "Cache-Control": "public, max-age=30, s-maxage=30",
      "CDN-Cache-Control": "public, max-age=300",
      "Vary": "Accept-Encoding",
    },
  )


@router.post("/telemetry/embed-view")
async def log_embed_impression(event: EmbedViewEvent):
  """Silent telemetry for embed impressions → BigQuery.

  Tracks which publishers embed HeadFade content, enabling:
  - CAC measurement (should be $0.00)
  - Publisher distribution heat-mapping
  - B2B data licensing value attribution
  """
  try:
    bq = _get_bq()
    rows = [
      {
        "video_id": event.videoId,
        "referrer": event.referrer,
        "event_timestamp": event.timestamp
        or datetime.datetime.now(tz=datetime.UTC).isoformat(),
        "event_type": "embed_impression",
      }
    ]
    errors = bq.insert_rows_json(
      "shadowtag-omega-v4.analytics.embed_impressions",
      rows,
    )
    if errors:
      return {"status": "partial", "errors": str(errors)}
  except Exception as e:
    # Fire-and-forget — never block the embed player
    return {"status": "error", "message": str(e)}

  return {"status": "logged"}
