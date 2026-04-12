"""
CineVerse streaming platform routes.

Handles video upload, transcoding, content management, and streaming.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models.cineverse import Content, ContentType, Creator, Stream
from ..models.ingestion import IngestionJob, IngestionStatus
from ..models.user import User

# Create a dedicated router for Cineverse
router = APIRouter(prefix="/cineverse", tags=["cineverse"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pydantic Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class UploadRequest(BaseModel):
    title: str
    content_type: ContentType
    description: str | None = None
    filename: str
    file_size_bytes: int


class UploadResponse(BaseModel):
    job_id: str
    upload_url: HttpUrl
    status: str


class UploadStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float | None = None
    error: str | None = None
    master_playlist_url: str | None = None


class ContentPublishRequest(BaseModel):
    is_premium: bool = False
    price_cents: int | None = None


class ContentResponse(BaseModel):
    id: str
    title: str
    content_type: str
    description: str | None
    duration_seconds: int | None
    video_url: str | None
    thumbnail_url: str | None
    is_published: bool
    view_count: int
    created_at: datetime
    published_at: datetime | None

    class Config:
        from_attributes = True


class StreamStartResponse(BaseModel):
    session_id: str
    content_id: str
    manifest_url: str
    started_at: datetime


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Upload & Ingestion Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.post("/upload", response_model=UploadResponse)
async def submit_upload(
    request: UploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Initialize a video upload.
    Creates an IngestionJob and returns a signed upload URL.
    """
    # Create DB record
    job = IngestionJob(
        user_id=current_user.id,
        content_type=request.content_type,  # Using shared enum might need mapping if models differ
        generated_title=request.title,
        generated_description=request.description,
        status=IngestionStatus.PROCESSING,  # Initial status
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # TODO: In production, generate signed URL for GCS/S3
    upload_url = f"https://storage.cineverse.ai/uploads/{job.id}/{request.filename}"

    return UploadResponse(
        job_id=job.id,
        upload_url=upload_url,
        status=job.status.value,
    )


@router.get("/upload/{job_id}/status", response_model=UploadStatusResponse)
async def get_upload_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the status of an ingestion job.
    """
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Simple permissions check
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return UploadStatusResponse(
        job_id=job.id,
        status=job.status.value,
        progress=None,  # Todo: track progress
        error=None,  # Todo: track error details
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Content Management Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.post("/content/publish/{job_id}", response_model=ContentResponse)
async def publish_content(
    job_id: str,
    request: ContentPublishRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Publish content from a completed ingestion job.
    """
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != IngestionStatus.APPROVED:
        raise HTTPException(status_code=400, detail=f"Job not ready/approved. Status: {job.status}")

    # Ensure creator profile exists
    creator = db.query(Creator).filter(Creator.user_id == current_user.id).first()
    if not creator:
        # Auto-create basic profile
        creator = Creator(
            user_id=current_user.id,
            display_name=current_user.full_name or "Creator",
            channel_url=f"channel-{uuid4()}",
        )
        db.add(creator)
        db.flush()

    # Create Content record
    content = Content(
        creator_id=creator.id,
        title=job.generated_title,
        description=job.generated_description,
        content_type=job.content_type,  # Ensure mapping matches
        shadowtag_signature=job.shadowtag_signature or "pending-sig",
        shadowtag_chain_id=job.verification_chain_id or "pending-chain",
        shadowtag_verified_at=datetime.utcnow(),
        is_published=True,
        is_premium=request.is_premium,
        price_cents=request.price_cents,
        published_at=datetime.utcnow(),
        # Video URL would come from ingestion result
        video_url=f"https://media.cineverse.ai/content/{job.id}/master.m3u8",
    )

    db.add(content)
    db.commit()
    db.refresh(content)

    return content


@router.get("/content", response_model=list[ContentResponse])
async def list_content(
    content_type: str | None = None,
    limit: int = Query(default=20, le=100),
    skip: int = 0,
    db: Session = Depends(get_db),
):
    """
    List published content.
    """
    query = db.query(Content).filter(Content.is_published)
    if content_type:
        query = query.filter(Content.content_type == content_type)

    content_list = query.order_by(desc(Content.published_at)).offset(skip).limit(limit).all()
    return content_list


@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    db: Session = Depends(get_db),
):
    """
    Get content details.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Streaming Endpoints
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@router.post("/content/{content_id}/stream/start", response_model=StreamStartResponse)
async def start_stream(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user),  # Allow anonymous
):
    """
    Start a streaming session.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if not content.is_published:
        raise HTTPException(status_code=403, detail="Content not published")

    session_id = str(uuid4())

    # Record stream session
    stream = Stream(
        id=session_id,
        content_id=content_id,
        user_id=current_user.id if current_user else None,
        started_at=datetime.utcnow(),
        ip_address="127.0.0.1",  # In prod, get from request
    )
    db.add(stream)

    # Increment view count atomic update
    content.view_count += 1

    db.commit()

    return StreamStartResponse(
        session_id=session_id,
        content_id=content_id,
        manifest_url=content.video_url,
        started_at=datetime.utcnow(),
    )


class TranscodeCompleteWebhook(BaseModel):
    """Webhook payload from transcode service."""

    job_id: str
    status: str
    error: str | None = None


@router.post("/webhook/transcode-complete")
async def transcode_complete_webhook(
    payload: TranscodeCompleteWebhook,
    db: Session = Depends(get_db),
):
    """
    Webhook to update job status.
    """
    job = db.query(IngestionJob).filter(IngestionJob.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if payload.status == "completed":
        job.status = IngestionStatus.APPROVED  # Simplified flow
    else:
        job.status = IngestionStatus.REJECTED

    db.commit()
    return {"status": "ok"}
