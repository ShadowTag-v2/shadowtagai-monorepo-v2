# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""DualCo strategy models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class GateStatus(StrEnum):
    """Gate evaluation status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class GateResult:
    """Result of evaluating a strategic gate."""

    gate_name: str
    status: GateStatus = GateStatus.NOT_STARTED
    score: float = 0.0
    details: dict = field(default_factory=dict)
    evaluated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DualCoStrategy:
    """Full DualCo strategy evaluation."""

    gates: list[GateResult] = field(default_factory=list)
    overall_score: float = 0.0
    recommendation: str = ""


__all__ = [
    "Base",
    "DualCoGateState",
    "DualCoMetricHistory",
    "DualCoStrategy",
    "GateResult",
    "GateStatus",
]

# ---------------------------------------------------------------------------
# SQLAlchemy ORM models — used by integration tests that persist gate state.
# ---------------------------------------------------------------------------
try:
    from sqlalchemy import Column, DateTime, Float, Integer, String
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):  # type: ignore[misc]
        """Shared ORM base for DualCo tables."""

    class DualCoGateState(Base):
        """Persistent gate state tracked across evaluations."""

        __tablename__ = "dualco_gate_state"

        id = Column(Integer, primary_key=True, autoincrement=True)
        gate_name = Column(String, nullable=False, index=True)
        status = Column(String, default="not_started")
        score = Column(Float, default=0.0)
        evaluated_at = Column(DateTime)

    class DualCoMetricHistory(Base):
        """Historical metric snapshots for DualCo evaluations."""

        __tablename__ = "dualco_metric_history"

        id = Column(Integer, primary_key=True, autoincrement=True)
        gate_name = Column(String, nullable=False, index=True)
        metric_name = Column(String, nullable=False)
        value = Column(Float, default=0.0)
        recorded_at = Column(DateTime)

except ImportError:
    # SQLAlchemy not available — provide no-op stubs for import-only usage.
    Base = type(
        "Base",
        (),
        {
            "metadata": type(
                "M", (), {"create_all": lambda **kw: None, "drop_all": lambda **kw: None}
            )()
        },
    )  # type: ignore[assignment,misc]
    DualCoGateState = None  # type: ignore[assignment,misc]
    DualCoMetricHistory = None  # type: ignore[assignment,misc]
