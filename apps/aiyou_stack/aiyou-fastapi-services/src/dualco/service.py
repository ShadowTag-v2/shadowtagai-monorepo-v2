# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""DualCo service layer.

Extracts all database operations from DualCo routes
into a proper service/repository pattern.
"""

from sqlalchemy.orm import Session

from .models import DualCoDecision


class DualCoService:
    """Service layer for DualCo operations."""

    @staticmethod
    def log_decision(db: Session, decision_data: dict) -> DualCoDecision:
        """Create a decision log entry."""
        db_decision = DualCoDecision(**decision_data)
        db.add(db_decision)
        db.commit()
        db.refresh(db_decision)
        return db_decision

    @staticmethod
    def list_decisions(db: Session, skip: int = 0, limit: int = 100) -> list[DualCoDecision]:
        """List decision log entries."""
        return db.query(DualCoDecision).offset(skip).limit(limit).all()
