"""Ingestion service layer.

Extracts all database operations from ingestion routes
into a proper service/repository pattern.
"""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models.ingestion import (
    AutoModerationRule,
    IngestionJob,
    IngestionStatus,
    ModerationCategory,
)


class IngestionService:
    """Service layer for ingestion operations."""

    @staticmethod
    def get_job(db: Session, job_id: str, user_id: str | None = None) -> IngestionJob | None:
        """Get an ingestion job by ID, optionally scoped to a user."""
        query = db.query(IngestionJob).filter(IngestionJob.id == job_id)
        if user_id:
            query = query.filter(IngestionJob.user_id == user_id)
        return query.first()

    @staticmethod
    def create_job(db: Session, **kwargs) -> IngestionJob:
        """Create a new ingestion job."""
        job = IngestionJob(**kwargs)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def list_jobs(
        db: Session,
        user_id: str,
        status: IngestionStatus | None = None,
        content_type=None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[IngestionJob]:
        """List ingestion jobs for a user with optional filtering."""
        query = db.query(IngestionJob).filter(IngestionJob.user_id == user_id)
        if status:
            query = query.filter(IngestionJob.status == status)
        if content_type:
            query = query.filter(IngestionJob.content_type == content_type)
        return query.order_by(IngestionJob.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def get_stats(db: Session, user_id: str, days: int = 30) -> dict:
        """Get ingestion statistics for a user."""
        since = datetime.utcnow() - timedelta(days=days)
        jobs = (
            db.query(IngestionJob)
            .filter(IngestionJob.user_id == user_id, IngestionJob.created_at >= since)
            .all()
        )

        total_jobs = len(jobs)
        pending = sum(1 for j in jobs if j.status == IngestionStatus.PENDING)
        analyzing = sum(1 for j in jobs if j.status == IngestionStatus.ANALYZING)
        approved = sum(1 for j in jobs if j.status == IngestionStatus.APPROVED)
        rejected = sum(1 for j in jobs if j.status == IngestionStatus.REJECTED)
        requires_review = sum(1 for j in jobs if j.requires_human_review)

        completed_jobs = [j for j in jobs if j.completed_at and j.started_at]
        avg_time = (
            sum((j.completed_at - j.started_at).total_seconds() for j in completed_jobs)
            / len(completed_jobs)
            if completed_jobs
            else 0.0
        )

        total_cost_cents = sum(j.processing_cost_cents or 0 for j in jobs)
        total_tokens = sum(j.gemini_tokens_used or 0 for j in jobs)

        return {
            "total_jobs": total_jobs,
            "pending": pending,
            "analyzing": analyzing,
            "approved": approved,
            "rejected": rejected,
            "requires_review": requires_review,
            "avg_processing_time_seconds": avg_time,
            "total_cost_usd": total_cost_cents / 100.0,
            "gemini_tokens_used": total_tokens,
        }

    @staticmethod
    def get_active_moderation_rules(db: Session) -> list[AutoModerationRule]:
        """Get active auto-moderation rules ordered by priority."""
        return (
            db.query(AutoModerationRule)
            .filter(AutoModerationRule.enabled)
            .order_by(AutoModerationRule.priority.desc())
            .all()
        )

    @staticmethod
    def apply_moderation(job: IngestionJob, db: Session) -> IngestionStatus:
        """Apply moderation rules and return the appropriate status."""
        # Fetch but not currently using rules (placeholder for future expansion)
        IngestionService.get_active_moderation_rules(db)

        if job.moderation_category == ModerationCategory.SAFE:
            if job.moderation_confidence and job.moderation_confidence >= 80:
                return IngestionStatus.APPROVED
            job.requires_human_review = True
            return IngestionStatus.REQUIRES_REVIEW

        if job.moderation_confidence and job.moderation_confidence >= 90:
            return IngestionStatus.REJECTED

        job.requires_human_review = True
        return IngestionStatus.REQUIRES_REVIEW
