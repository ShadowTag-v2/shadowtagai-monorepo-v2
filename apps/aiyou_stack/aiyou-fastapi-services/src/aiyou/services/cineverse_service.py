"""CineVerse service layer.

Extracts all database operations from cineverse routes
into a proper service/repository pattern.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models.cineverse import Content, ContentType, Creator, Stream
from ..models.ingestion import IngestionJob, IngestionStatus
from ..models.user import User


class CineverseService:
    """Service layer for cineverse operations."""

    @staticmethod
    def create_upload_job(
        db: Session, user: User, content_type: ContentType, title: str, description: str | None,
    ) -> IngestionJob:
        """Create an ingestion job for content upload."""
        job = IngestionJob(
            user_id=user.id,
            content_type=content_type,
            generated_title=title,
            generated_description=description,
            status=IngestionStatus.PROCESSING,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_upload_job(db: Session, job_id: str) -> IngestionJob | None:
        """Get an ingestion job by ID."""
        return db.query(IngestionJob).filter(IngestionJob.id == job_id).first()

    @staticmethod
    def publish_content(
        db: Session,
        job: IngestionJob,
        user: User,
        is_premium: bool = False,
        price_cents: int | None = None,
    ) -> Content:
        """Publish content from a completed ingestion job."""
        creator = db.query(Creator).filter(Creator.user_id == user.id).first()
        if not creator:
            creator = Creator(
                user_id=user.id,
                display_name=user.full_name or "Creator",
                channel_url=f"channel-{uuid4()}",
            )
            db.add(creator)
            db.flush()

        content = Content(
            creator_id=creator.id,
            title=job.generated_title,
            description=job.generated_description,
            content_type=job.content_type,
            shadowtag_signature=job.shadowtag_signature or "pending-sig",
            shadowtag_chain_id=job.verification_chain_id or "pending-chain",
            shadowtag_verified_at=datetime.utcnow(),
            is_published=True,
            is_premium=is_premium,
            price_cents=price_cents,
            published_at=datetime.utcnow(),
            video_url=f"https://media.cineverse.ai/content/{job.id}/master.m3u8",
        )
        db.add(content)
        db.commit()
        db.refresh(content)
        return content

    @staticmethod
    def list_content(
        db: Session, content_type: str | None = None, skip: int = 0, limit: int = 20,
    ) -> list[Content]:
        """List published content."""
        query = db.query(Content).filter(Content.is_published)
        if content_type:
            query = query.filter(Content.content_type == content_type)
        return query.order_by(desc(Content.published_at)).offset(skip).limit(limit).all()

    @staticmethod
    def get_content(db: Session, content_id: str) -> Content | None:
        """Get content by ID."""
        return db.query(Content).filter(Content.id == content_id).first()

    @staticmethod
    def start_stream(db: Session, content: Content, user: User | None = None) -> Stream:
        """Start a streaming session and increment view count."""
        session_id = str(uuid4())
        stream = Stream(
            id=session_id,
            content_id=content.id,
            user_id=user.id if user else None,
            started_at=datetime.utcnow(),
            ip_address="127.0.0.1",
        )
        db.add(stream)
        content.view_count += 1
        db.commit()
        return stream

    @staticmethod
    def handle_transcode_webhook(db: Session, job_id: str, status: str) -> IngestionJob:
        """Update job status from transcode webhook."""
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            raise ValueError("Job not found")

        if status == "completed":
            job.status = IngestionStatus.APPROVED
        else:
            job.status = IngestionStatus.REJECTED

        db.commit()
        return job
