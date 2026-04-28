# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""DualCo Database Models"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text

# Use main Base to ensure tables are created by init_db
from src.shadowtag_v4.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class DualCoMetricHistory(Base):
    """History of monthly metrics."""

    __tablename__ = "dualco_metric_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Storing flat metrics as JSON for flexibility, or we could use specific columns
    # Given the specificity of Bourne/160, specific columns are better for query performance,
    # but a JSON blob is faster to iterate on if metrics change.
    # Decision: Hybrid. Core rigid columns + extra JSON.

    metrics_data = Column(JSON, nullable=False)  # Stores the full MetricsInput dict

    # Calculated status snapshot at this time
    gate_status_snapshot = Column(JSON, nullable=True)


class DualCoDecision(Base):
    """Decision Log (Mochary Style)."""

    __tablename__ = "dualco_decisions"

    id = Column(String, primary_key=True, default=generate_uuid)
    decision_date = Column(DateTime, default=datetime.utcnow)

    context = Column(Text, nullable=False)
    options_considered = Column(JSON, nullable=False)  # List of strings
    chosen_option = Column(Text, nullable=False)
    why_first_principles = Column(Text, nullable=False)
    metrics_to_watch = Column(JSON, nullable=False)  # List of strings
    kill_criteria = Column(Text, nullable=False)
    owner = Column(String, nullable=False)
    review_cadence = Column(String, default="Monthly")


class DualCoGateState(Base):
    """Current State of Gates (Persisted)"""

    __tablename__ = "dualco_gate_states"

    gate_name = Column(String, primary_key=True)  # e.g., "GATE_A"
    status = Column(String, default="PENDING")  # PENDING, PASSED, FAILED
    consecutive_failures = Column(Integer, default=0)
    last_evaluated_at = Column(DateTime, nullable=True)
    last_metric_snapshot_id = Column(String, ForeignKey("dualco_metric_history.id"), nullable=True)
