"""Content Ingestion API Routes
Handles file uploads and Gemini-powered content analysis
"""

import logging
import uuid
from datetime import datetime, timedelta

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..config import settings
from ..database import get_db
from ..models.ingestion import (
    AutoModerationRule,
    ContentType,
    IngestionJob,
    IngestionStatus,
    ModerationCategory,
)
from ..models.user import User
from ..services.gemini import GeminiClient, GeminiServiceError
from ..services.shadowtag.crypto import ShadowTagVerifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])

# Initialize Gemini client (in production, use dependency injection)
# gemini_client = GeminiClient(project_id="your-gcp-project")


class CreateIngestionJobRequest(BaseModel):
    """Request to create an ingestion job"""

    content_type: ContentType
    filename: str
    file_size_bytes: int
    mime_type: str


class IngestionJobResponse(BaseModel):
    """Response for ingestion job"""

    id: str
    status: IngestionStatus
    content_type: ContentType
    file_path: str | None
    moderation_category: ModerationCategory | None
    requires_human_review: bool
    progress_percent: int
    estimated_completion_seconds: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class IngestionAnalysisResponse(BaseModel):
    """Detailed analysis results"""

    job_id: str
    detected_labels: list[str]
    detected_objects: list[dict]
    detected_text: str | None
    quality_score: int
    brand_safety_score: int
    generated_title: str | None
    generated_description: str | None
    generated_tags: list[str]
    moderation_safe: bool


class IngestionStats(BaseModel):
    """Ingestion statistics"""

    total_jobs: int
    pending: int
    analyzing: int
    approved: int
    rejected: int
    requires_review: int
    avg_processing_time_seconds: float
    total_cost_usd: float
    gemini_tokens_used: int


@router.post("/jobs", response_model=IngestionJobResponse)
async def create_ingestion_job(
    file: UploadFile = File(...),
    content_type: ContentType = Query(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload content for ingestion and Gemini analysis

    This endpoint:
    1. Uploads file to GCS
    2. Creates ingestion job
    3. Queues Gemini analysis (async)
    4. Returns job ID for status tracking
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        if file.size and file.size > 500_000_000:  # 500MB limit
            raise HTTPException(status_code=413, detail="File too large (max 500MB)")

        # Generate job ID
        job_id = str(uuid.uuid4())

        # TODO: Upload to GCS
        # For now, use local path
        file_path = f"gs://shadowtag_v4-content-staging/{current_user.id}/{job_id}/{file.filename}"

        # Create ingestion job
        job = IngestionJob(
            id=job_id,
            user_id=current_user.id,
            content_type=content_type,
            file_path=file_path,
            file_size_bytes=file.size or 0,
            mime_type=file.content_type or "application/octet-stream",
            original_filename=file.filename,
            status=IngestionStatus.PENDING,
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        # Queue background processing
        background_tasks.add_task(
            process_ingestion_job,
            job_id=job_id,
            user_id=current_user.id,
        )

        logger.info(f"Created ingestion job {job_id} for user {current_user.id}")

        return IngestionJobResponse(
            id=job.id,
            status=job.status,
            content_type=job.content_type,
            file_path=job.file_path,
            moderation_category=job.moderation_category,
            requires_human_review=job.requires_human_review or False,
            progress_percent=0,
            estimated_completion_seconds=30,
            created_at=job.created_at,
        )

    except Exception as e:
        logger.error(f"Failed to create ingestion job: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/jobs/{job_id}", response_model=IngestionJobResponse)
async def get_ingestion_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get ingestion job status"""
    job = (
        db.query(IngestionJob)
        .filter(IngestionJob.id == job_id, IngestionJob.user_id == current_user.id)
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Calculate progress
    if job.status == IngestionStatus.PENDING:
        progress = 0
        eta = 30
    elif job.status == IngestionStatus.ANALYZING:
        progress = 50
        eta = 15
    elif job.status in [IngestionStatus.APPROVED, IngestionStatus.REJECTED]:
        progress = 100
        eta = 0
    else:
        progress = 75
        eta = 5

    return IngestionJobResponse(
        id=job.id,
        status=job.status,
        content_type=job.content_type,
        file_path=job.file_path,
        moderation_category=job.moderation_category,
        requires_human_review=job.requires_human_review or False,
        progress_percent=progress,
        estimated_completion_seconds=eta,
        created_at=job.created_at,
    )


@router.get("/jobs/{job_id}/analysis", response_model=IngestionAnalysisResponse)
async def get_ingestion_analysis(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed Gemini analysis results"""
    job = (
        db.query(IngestionJob)
        .filter(IngestionJob.id == job_id, IngestionJob.user_id == current_user.id)
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == IngestionStatus.PENDING:
        raise HTTPException(status_code=202, detail="Analysis not yet complete")

    return IngestionAnalysisResponse(
        job_id=job.id,
        detected_labels=job.detected_labels or [],
        detected_objects=job.detected_objects or [],
        detected_text=job.detected_text,
        quality_score=job.quality_score or 0,
        brand_safety_score=job.brand_safety_score or 0,
        generated_title=job.generated_title,
        generated_description=job.generated_description,
        generated_tags=job.generated_tags or [],
        moderation_safe=job.moderation_category == ModerationCategory.SAFE,
    )


@router.get("/jobs", response_model=list[IngestionJobResponse])
async def list_ingestion_jobs(
    status: IngestionStatus | None = None,
    content_type: ContentType | None = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's ingestion jobs"""
    query = db.query(IngestionJob).filter(IngestionJob.user_id == current_user.id)

    if status:
        query = query.filter(IngestionJob.status == status)
    if content_type:
        query = query.filter(IngestionJob.content_type == content_type)

    jobs = query.order_by(IngestionJob.created_at.desc()).limit(limit).offset(offset).all()

    return [
        IngestionJobResponse(
            id=job.id,
            status=job.status,
            content_type=job.content_type,
            file_path=job.file_path,
            moderation_category=job.moderation_category,
            requires_human_review=job.requires_human_review or False,
            progress_percent=100 if job.completed_at else 50,
            estimated_completion_seconds=0,
            created_at=job.created_at,
        )
        for job in jobs
    ]


@router.get("/stats", response_model=IngestionStats)
async def get_ingestion_stats(
    days: int = Query(30, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get ingestion statistics for the user"""
    since = datetime.utcnow() - timedelta(days=days)

    jobs = (
        db.query(IngestionJob)
        .filter(IngestionJob.user_id == current_user.id, IngestionJob.created_at >= since)
        .all()
    )

    total_jobs = len(jobs)
    pending = sum(1 for j in jobs if j.status == IngestionStatus.PENDING)
    analyzing = sum(1 for j in jobs if j.status == IngestionStatus.ANALYZING)
    approved = sum(1 for j in jobs if j.status == IngestionStatus.APPROVED)
    rejected = sum(1 for j in jobs if j.status == IngestionStatus.REJECTED)
    requires_review = sum(1 for j in jobs if j.requires_human_review)

    # Calculate average processing time
    completed_jobs = [j for j in jobs if j.completed_at and j.started_at]
    if completed_jobs:
        avg_time = sum(
            (j.completed_at - j.started_at).total_seconds() for j in completed_jobs
        ) / len(completed_jobs)
    else:
        avg_time = 0.0

    # Calculate costs
    total_cost_cents = sum(j.processing_cost_cents or 0 for j in jobs)
    total_tokens = sum(j.gemini_tokens_used or 0 for j in jobs)

    return IngestionStats(
        total_jobs=total_jobs,
        pending=pending,
        analyzing=analyzing,
        approved=approved,
        rejected=rejected,
        requires_review=requires_review,
        avg_processing_time_seconds=avg_time,
        total_cost_usd=total_cost_cents / 100.0,
        gemini_tokens_used=total_tokens,
    )


# Background processing function


async def process_ingestion_job(job_id: str, user_id: str):
    """Background task to process ingestion job with Gemini

    This would run in a separate worker (Celery, Cloud Tasks, etc)
    """
    from ..database import SessionLocal

    db = SessionLocal()
    try:
        # Get job
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        # Update status
        job.status = IngestionStatus.ANALYZING
        job.started_at = datetime.utcnow()
        db.commit()

        # Initialize Gemini client from settings
        if not settings.gemini_api_key:
            raise Exception("GEMINI_API_KEY not configured")

        gemini_client = GeminiClient(
            api_key=settings.gemini_api_key,
            project_id=settings.gemini_project_id,
        )

        # Process based on content type
        if job.content_type in [ContentType.IMAGE, ContentType.PRODUCT_IMAGE]:
            result = await gemini_client.analyze_image(
                job.file_path,
                include_labels=True,
                include_moderation=True,
                include_text=True,
                include_objects=True,
            )

            # Update job with results
            job.detected_labels = result["labels"]
            job.detected_objects = result["objects"]
            job.detected_text = result["detected_text"]
            job.moderation_category = ModerationCategory(result["moderation"]["category"])
            job.moderation_confidence = result["moderation"]["confidence"]
            job.moderation_details = result["moderation"]["details"]
            job.gemini_tokens_used = result["tokens_used"]
            job.gemini_model_version = result["model"]

        elif job.content_type == ContentType.VIDEO:
            result = await gemini_client.analyze_video(
                job.file_path,
                sample_frames=10,
                include_transcript=True,
                include_moderation=True,
            )

            job.detected_objects = result["detected_objects"]
            job.generated_transcript = result["transcript"]
            job.moderation_category = ModerationCategory(result["moderation"]["category"])
            job.moderation_confidence = result["moderation"]["confidence"]
            job.gemini_tokens_used = result["tokens_used"]

        elif job.content_type == ContentType.TEXT:
            # For text content, use moderation API
            result = await gemini_client.moderate_text(job.detected_text or "")
            job.moderation_category = ModerationCategory(result["category"])
            job.moderation_confidence = result["confidence"]
            job.moderation_details = result["details"]

        # Generate metadata
        content_desc = f"{job.content_type.value}: {job.detected_text or 'No description'}"
        metadata = await gemini_client.generate_metadata(content_desc, job.content_type.value)

        job.generated_title = metadata.get("title")
        job.generated_description = metadata.get("description")
        job.generated_tags = metadata.get("tags", [])

        # Calculate costs
        cost_usd = gemini_client.calculate_cost(
            job.gemini_tokens_used or 0,
            job.gemini_model_version or "gemini-3.1-flash-lite-preview",
            "total",
        )
        job.processing_cost_cents = int(cost_usd * 100)

        # Apply auto-moderation rules
        job.status = apply_moderation_rules(job, db)

        # ShadowTag verification
        if settings.shadowtag_enabled and settings.shadowtag_private_key:
            verifier = ShadowTagVerifier()
            # Use private key from settings (loaded from env or secrets manager)
            verification = verifier.sign(
                payload={
                    "job_id": job.id,
                    "user_id": user_id,
                    "content_type": job.content_type.value,
                    "moderation_category": job.moderation_category.value
                    if job.moderation_category
                    else "unknown",
                    "timestamp": datetime.utcnow().isoformat(),
                },
                private_key_bytes=settings.shadowtag_private_key.encode(),
            )

            job.shadowtag_signature = verification["signature"]
            job.verification_chain_id = verification["id"]
        else:
            logger.warning("ShadowTag disabled or private key not configured")

        job.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Completed ingestion job {job_id}: {job.status.value}")

    except GeminiServiceError as e:
        logger.error(f"Gemini service error for job {job_id}: {e}")
        job.status = IngestionStatus.FAILED
        db.commit()

    except Exception as e:
        logger.error(f"Failed to process job {job_id}: {e}")
        job.status = IngestionStatus.FAILED
        db.commit()

    finally:
        db.close()


def apply_moderation_rules(job: IngestionJob, db: Session) -> IngestionStatus:
    """Apply auto-moderation rules to determine job status"""
    # Get active rules
    (
        db.query(AutoModerationRule)
        .filter(AutoModerationRule.enabled)
        .order_by(AutoModerationRule.priority.desc())
        .all()
    )

    # Default to safe
    if job.moderation_category == ModerationCategory.SAFE:
        if job.moderation_confidence and job.moderation_confidence >= 80:
            return IngestionStatus.APPROVED
        job.requires_human_review = True
        return IngestionStatus.REQUIRES_REVIEW

    # Check for violations
    if job.moderation_confidence and job.moderation_confidence >= 90:
        # High confidence violation
        return IngestionStatus.REJECTED

    # Moderate confidence - requires review
    job.requires_human_review = True
    return IngestionStatus.REQUIRES_REVIEW
