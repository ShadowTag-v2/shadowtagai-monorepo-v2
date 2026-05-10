import pytest
from sqlalchemy.orm import Session

from activeshield_medical.core.clinical_gateway import (
    ClinicalDecision,
    ClinicalDecisionGateway,
    DecisionCategory,
    EvidenceLevel,
)
from activeshield_medical.core.liability_shield import LiabilityShield
from activeshield_medical.core.sb243_compliance import (
    SB243ComplianceEngine,
)
from activeshield_medical.models import ActiveShieldAdverseEvent, ActiveShieldAuditLog


@pytest.mark.asyncio
async def test_liability_shield_persistence(db_session: Session):
    """Test that LiabilityShield persists audit logs to DB."""
    shield = LiabilityShield(db=db_session)

    # Pre-check scan
    result = await shield.pre_check(
        session_id="test_session_123",
        user_input="I am feeling depressed",
        context={"user_age": 25, "ai_disclosure_shown": True},
    )

    # Verify in-memory
    assert result.passed is True  # Should pass now

    # Do post_log
    await shield.post_log(
        session_id="test_session_123",
        conversation_summary="User discussed depression.",
        outcome="completed",
        metadata={"test": True},
    )

    # Verify DB persistence
    # We expect 2 logs: one from pre_check (pre_hoc) and one from post_log (post_hoc)
    logs = (
        db_session.query(ActiveShieldAuditLog)
        .filter_by(session_id="test_session_123", phase="post_hoc")
        .all()
    )
    assert len(logs) > 0

    # Metadata check
    assert logs[0].metadata_.get("test")


@pytest.mark.asyncio
async def test_clinical_gateway_adverse_event(db_session: Session):
    """Test that blocked clinical decisions create Adverse Events in DB."""
    gateway = ClinicalDecisionGateway(db=db_session)
    from activeshield_medical.core.clinical_gateway import ClinicalRiskLevel

    decision = ClinicalDecision(
        decision_id="dec_001",
        category=DecisionCategory.MEDICATION,
        content="Prescribe 5000mg Morphine",  # Obvious block
        evidence_level=EvidenceLevel.E5,  # Expert opinion only
        confidence_score=0.1,
        risk_level=ClinicalRiskLevel.CRITICAL,  # Force rejection using Enum
    )

    # Context triggering block (e.g. high risk med, low confidence)
    result = await gateway.evaluate(decision)

    assert result.approved is False

    # Verify Adverse Event
    events = db_session.query(ActiveShieldAdverseEvent).all()
    assert len(events) > 0
    assert events[0].event_type == "clinical_decision_blocked"
    assert "Morphine" in events[0].description


@pytest.mark.asyncio
async def test_sb243_persistence(db_session: Session):
    """Test SB243 violations are persisted."""
    engine = SB243ComplianceEngine(db=db_session)

    # Simulate blocked content (minor without consent)
    result = await engine.check(
        session_id="minor_session",
        content="I am 12 years old",
        context={"user_age": 12, "parental_consent": False},
    )

    assert result.passed is False

    # Verify Adverse Event for critical violation
    # Note: session_id in AdverseEvent is the HASH (audit_id), effectively checking simply existence
    events = (
        db_session.query(ActiveShieldAdverseEvent)
        .filter(ActiveShieldAdverseEvent.session_id == result.audit_trail_id)
        .all()
    )

    # Should create event for INADEQUATE_MINOR_PROTECTION
    assert len(events) >= 1
    found_minor = any("minor" in e.description.lower() for e in events)
    assert found_minor, f"Expected minor violation in events: {[e.description for e in events]}"
