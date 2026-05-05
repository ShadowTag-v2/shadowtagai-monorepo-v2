"""HeadFade Embed API — Zero-CAC Distribution Engine.

Powers the <iframe> Embed Player for publishers. When NYT/BBC/Substack
writes about a viral deepfake, they embed the HeadFade player instead
of a raw X/TikTok link.

Endpoints:
  GET  /api/embed/{video_id}        → Embed metadata for the iframe player
  POST /api/telemetry/embed-view    → Silent impression telemetry → BigQuery
"""

from __future__ import annotations

import datetime

from fastapi import APIRouter
from google.cloud import bigquery, firestore
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["embed"])

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
        return {
            "id": video_id,
            "cdnUrl": data.get("cdn_url", f"https://storage.googleapis.com/headfade-cdn-origin/{video_id}.mp4"),
            "models": data.get("detected_models", ["Unknown"]),
            "hdiScore": data.get("hdi_score", 0),
            "parentCreator": data.get("parent_creator", "original"),
            "remixDepth": data.get("remix_depth", 0),
            "title": data.get("title", "Synthetic Media"),
        }

    # Fallback for videos not yet in Firestore
    return {
        "id": video_id,
        "cdnUrl": f"https://storage.googleapis.com/headfade-cdn-origin/{video_id}.mp4",
        "models": ["Pending Analysis"],
        "hdiScore": 0,
        "parentCreator": "unknown",
        "remixDepth": 0,
        "title": "Synthetic Media Specimen",
    }


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
                "event_timestamp": event.timestamp or datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
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
