"""Scrape Job Service Layer

Encapsulates database operations for AI Thread scrape job management.
"""

import uuid

from sqlalchemy.orm import Session
from src.shadowtag_v4.models.ai_threads import AIThreadScrapeJob


class ScrapeJobService:
    """Service layer for scrape job operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> AIThreadScrapeJob:
        """Create a new scrape job from validated data."""
        job = AIThreadScrapeJob(
            id=str(uuid.uuid4()),
            query=data.get("query"),
            min_likes=data.get("min_likes"),
            max_results=data.get("max_results"),
            scheduled_at=data.get("scheduled_at"),
            status="pending",
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get(self, job_id: str) -> AIThreadScrapeJob | None:
        """Get a scrape job by ID."""
        return self.db.query(AIThreadScrapeJob).filter_by(id=job_id).first()

    def list(
        self,
        status_filter: str | None = None,
        limit: int = 20,
    ) -> list[AIThreadScrapeJob]:
        """List scrape jobs with optional status filter."""
        query = self.db.query(AIThreadScrapeJob)
        if status_filter:
            query = query.filter(AIThreadScrapeJob.status == status_filter)
        return query.order_by(AIThreadScrapeJob.created_at.desc()).limit(limit).all()
