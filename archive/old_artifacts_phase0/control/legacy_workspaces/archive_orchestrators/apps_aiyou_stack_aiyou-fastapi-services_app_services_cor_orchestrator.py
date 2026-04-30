"""
Cor (Core) Orchestrator
=======================
Third layer of the NS-JR-Cor compliance framework.

Responsibilities:
- Orchestrate NS → JR → Action pipeline
- Handle async batching for high throughput
- Integrate with GPTRAM for stateful session tracking
- Violation logging with 7d retention
- Compliance certificate generation
- Audit trail management

Integration Points:
- NS Detection Engine
- JR Policy Engine
- GPTRAM (Redis memory layer)
- ShadowTag (cryptographic attestation)
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from app.models.california_ai import (
    AuditTrailEntry,
    BatchAssessmentRequest,
    BatchAssessmentResult,
    CaliforniaAIAssessmentRequest,
    CaliforniaAIAssessmentResult,
    ComplianceAction,
    ComplianceAttestation,
    UserAgeCategory,
)
from app.services.crisis_webhook import get_crisis_webhook
from app.services.jr_policy_engine import JRPolicyEngine, get_jr_engine
from app.services.ns_detection_engine import NSDetectionEngine, get_ns_engine
from app.services.shadowtag_attestation import get_shadowtag_client
from corp_engine.governance.regulations.california_ai_comprehensive import (
    CRISIS_RESOURCES,
    ca_comprehensive_compliance,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class CorConfig:
    """Cor Orchestrator configuration"""

    # Pipeline settings
    enable_caching: bool = True
    enable_batching: bool = True
    batch_size: int = 10
    batch_timeout_ms: int = 100

    # Session tracking
    session_tracking_enabled: bool = True
    session_ttl_hours: int = 24

    # Audit settings
    audit_enabled: bool = True
    audit_retention_days: int = 7

    # Attestation
    attestation_enabled: bool = True
    attestation_validity_hours: int = 24

    # Performance
    max_concurrent_requests: int = 100
    timeout_ms: int = 5000


# =============================================================================
# Session Manager
# =============================================================================


class SessionManager:
    """Manages user sessions for break reminders and tracking"""

    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self._sessions: dict[str, dict] = {}

    def start_session(self, session_id: str, user_age: UserAgeCategory) -> None:
        """Start or update a session"""
        self._sessions[session_id] = {
            "start_time": datetime.utcnow(),
            "user_age": user_age,
            "message_count": 0,
            "last_break_reminder": None,
        }

    def get_session_duration_minutes(self, session_id: str) -> int:
        """Get session duration in minutes"""
        session = self._sessions.get(session_id)
        if not session:
            return 0
        duration = datetime.utcnow() - session["start_time"]
        return int(duration.total_seconds() / 60)

    def increment_message_count(self, session_id: str) -> int:
        """Increment and return message count"""
        if session_id in self._sessions:
            self._sessions[session_id]["message_count"] += 1
            return self._sessions[session_id]["message_count"]
        return 0

    def record_break_reminder(self, session_id: str) -> None:
        """Record that a break reminder was sent"""
        if session_id in self._sessions:
            self._sessions[session_id]["last_break_reminder"] = datetime.utcnow()

    def should_send_break_reminder(
        self, session_id: str, user_age: UserAgeCategory
    ) -> tuple[bool, str | None]:
        """Check if break reminder should be sent"""
        session = self._sessions.get(session_id)
        if not session:
            return False, None

        duration = self.get_session_duration_minutes(session_id)

        # Different thresholds by age
        if user_age == UserAgeCategory.UNDER_13:
            threshold = 30
            reminder = "Time for a break! Go do something fun offline!"
        elif user_age == UserAgeCategory.TEEN_13_17:
            threshold = 60
            reminder = "You've been chatting for a while. Consider taking a break!"
        else:
            return False, None

        if duration >= threshold:
            # Check if we've already sent a reminder recently (within 15 min)
            last_reminder = session.get("last_break_reminder")
            if last_reminder:
                time_since = (datetime.utcnow() - last_reminder).total_seconds() / 60
                if time_since < 15:
                    return False, None
            return True, reminder

        return False, None

    def cleanup_expired(self) -> int:
        """Remove expired sessions"""
        cutoff = datetime.utcnow() - timedelta(hours=self.ttl_hours)
        expired = [sid for sid, data in self._sessions.items() if data["start_time"] < cutoff]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)


# =============================================================================
# Audit Trail Manager
# =============================================================================


class AuditTrailManager:
    """Manages compliance audit trail"""

    def __init__(self, retention_days: int = 7):
        self.retention_days = retention_days
        self._entries: list[AuditTrailEntry] = []

    def log_entry(
        self,
        stage: str,
        action: str,
        input_hash: str,
        output_hash: str,
        latency_ms: float,
        metadata: dict | None = None,
    ) -> AuditTrailEntry:
        """Log an audit trail entry"""
        entry = AuditTrailEntry(
            stage=stage,
            action=action,
            input_hash=input_hash,
            output_hash=output_hash,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        return entry

    def get_entries(
        self,
        content_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditTrailEntry]:
        """Get audit trail entries"""
        entries = self._entries[-limit:]

        if since:
            entries = [e for e in entries if e.timestamp >= since]

        if content_id:
            entries = [e for e in entries if e.metadata.get("content_id") == content_id]

        return entries

    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        original_count = len(self._entries)
        self._entries = [e for e in self._entries if e.timestamp >= cutoff]
        return original_count - len(self._entries)


# =============================================================================
# Attestation Generator
# =============================================================================


class AttestationGenerator:
    """Generates compliance attestations/certificates"""

    def __init__(self, validity_hours: int = 24):
        self.validity_hours = validity_hours

    def generate(
        self,
        content_id: str,
        content_hash: str,
        result: CaliforniaAIAssessmentResult,
    ) -> ComplianceAttestation:
        """Generate compliance attestation"""
        now = datetime.utcnow()

        attestation = ComplianceAttestation(
            issued_at=now,
            valid_until=now + timedelta(hours=self.validity_hours),
            content_hash=content_hash,
            compliance_status="compliant" if result.is_compliant else "non_compliant",
            frameworks_assessed=["CA_AI_CHATBOT_REGULATIONS"],
        )

        # Generate signature (in production, use ShadowTag)
        signature_data = (
            f"{attestation.attestation_id}:{content_hash}:{attestation.issued_at.isoformat()}"
        )
        attestation.signature = hashlib.sha256(signature_data.encode()).hexdigest()[:32]

        return attestation


# =============================================================================
# Main Cor Orchestrator
# =============================================================================


class CorOrchestrator:
    """
    Core Orchestrator for NS-JR-Cor pipeline.

    Coordinates the full compliance assessment pipeline:
    1. NS Detection (signal extraction)
    2. JR Classification (policy evaluation)
    3. Action Determination (go/no-go + required actions)
    4. Audit Trail (logging and attestation)
    """

    def __init__(
        self,
        config: CorConfig | None = None,
        ns_engine: NSDetectionEngine | None = None,
        jr_engine: JRPolicyEngine | None = None,
    ):
        self.config = config or CorConfig()

        # Pipeline components
        self.ns_engine = ns_engine or get_ns_engine()
        self.jr_engine = jr_engine or get_jr_engine()

        # Session and audit management
        self.session_manager = SessionManager(ttl_hours=self.config.session_ttl_hours)
        self.audit_manager = AuditTrailManager(retention_days=self.config.audit_retention_days)
        self.attestation_generator = AttestationGenerator(
            validity_hours=self.config.attestation_validity_hours
        )

        # Webhook and ShadowTag integration
        self.crisis_webhook = get_crisis_webhook()
        self.shadowtag_client = get_shadowtag_client()

        # Statistics
        self._stats = {
            "total_assessments": 0,
            "compliant": 0,
            "non_compliant": 0,
            "crisis_responses": 0,
            "cache_hits": 0,
            "avg_latency_ms": 0.0,
        }

        # Semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

    async def assess(
        self,
        request: CaliforniaAIAssessmentRequest,
    ) -> CaliforniaAIAssessmentResult:
        """
        Main assessment method.

        Runs full NS-JR-Cor pipeline and returns compliance result.
        """
        async with self._semaphore:
            return await self._assess_internal(request)

    async def _assess_internal(
        self,
        request: CaliforniaAIAssessmentRequest,
    ) -> CaliforniaAIAssessmentResult:
        """Internal assessment implementation"""
        start_time = time.time()
        self._stats["total_assessments"] += 1

        audit_trail: list[AuditTrailEntry] = []

        # Generate content hash for caching/attestation
        content_hash = hashlib.sha256(request.content.encode()).hexdigest()[:32]

        # Determine user age category
        user_age = request.get_age_category()

        # Session management
        is_conversation_start = False
        session_duration = 0
        if request.session_id:
            session_duration = self.session_manager.get_session_duration_minutes(request.session_id)
            if session_duration == 0:
                is_conversation_start = True
                self.session_manager.start_session(request.session_id, user_age)
            else:
                self.session_manager.increment_message_count(request.session_id)

        # ===== STAGE 1: NS Detection =====
        ns_start = time.time()
        ns_output = await self.ns_engine.detect(
            content=request.content,
            content_type=request.content_type,
        )
        ns_latency = (time.time() - ns_start) * 1000

        if ns_output.cache_hit:
            self._stats["cache_hits"] += 1

        # Log NS stage
        audit_trail.append(
            self.audit_manager.log_entry(
                stage="NS",
                action="detect",
                input_hash=content_hash,
                output_hash=hashlib.sha256(str(ns_output.overall_risk_score).encode()).hexdigest()[
                    :16
                ],
                latency_ms=ns_latency,
                metadata={"content_id": request.content_id or content_hash},
            )
        )

        # ===== STAGE 2: JR Classification =====
        jr_start = time.time()
        jr_output = await self.jr_engine.evaluate(
            content_id=request.content_id or content_hash,
            ns_output=ns_output,
            user_age=user_age,
            session_duration_minutes=session_duration,
            is_conversation_start=is_conversation_start,
        )
        jr_latency = (time.time() - jr_start) * 1000

        # Log JR stage
        audit_trail.append(
            self.audit_manager.log_entry(
                stage="JR",
                action="classify",
                input_hash=hashlib.sha256(str(ns_output.overall_risk_score).encode()).hexdigest()[
                    :16
                ],
                output_hash=hashlib.sha256(str(jr_output.go_decision).encode()).hexdigest()[:16],
                latency_ms=jr_latency,
                metadata={"content_id": request.content_id or content_hash},
            )
        )

        # ===== STAGE 3: Build Result =====
        # Check for break reminder
        break_reminder_due = False
        break_reminder_text = None
        if request.session_id:
            break_reminder_due, break_reminder_text = (
                self.session_manager.should_send_break_reminder(request.session_id, user_age)
            )
            if break_reminder_due:
                self.session_manager.record_break_reminder(request.session_id)

        # Crisis response handling
        self_harm_detected = len(ns_output.self_harm_signals) > 0
        crisis_resources = []
        if self_harm_detected:
            self._stats["crisis_responses"] += 1
            crisis_resources = [
                CRISIS_RESOURCES[k]["name"]
                for k in ["988_LIFELINE", "CRISIS_TEXT", "TREVOR_PROJECT"]
            ]

            # Send crisis alert webhook (async, non-blocking)
            max_confidence = max(s.confidence for s in ns_output.self_harm_signals)
            asyncio.create_task(
                self.crisis_webhook.send_self_harm_alert(
                    content_id=request.content_id or content_hash,
                    confidence=max_confidence,
                    indicators=[s.signal_type for s in ns_output.self_harm_signals],
                    session_id=request.session_id,
                )
            )

        # Determine disclosure text
        disclosure_required = (
            is_conversation_start or ComplianceAction.DISCLOSE in jr_output.required_actions
        )
        disclosure_text = "I am an AI assistant. I am not a human." if disclosure_required else ""

        # Build action details
        action_details = {}
        if self_harm_detected:
            action_details["crisis_response"] = (
                ca_comprehensive_compliance.generate_crisis_response()
            )
        if break_reminder_due:
            action_details["break_reminder"] = break_reminder_text

        total_latency = (time.time() - start_time) * 1000

        # Calculate compliance score
        compliance_score = 1.0 - (len(jr_output.all_violations) * 0.1)
        compliance_score = max(0.0, min(1.0, compliance_score))

        result = CaliforniaAIAssessmentResult(
            content_id=request.content_id or content_hash,
            request_id=request.metadata.get("request_id"),
            is_compliant=jr_output.is_compliant,
            go_decision=jr_output.go_decision,
            compliance_score=compliance_score,
            risk_tier=jr_output.risk_tier,
            violations=jr_output.all_violations,
            violation_count=len(jr_output.all_violations),
            required_actions=jr_output.required_actions,
            action_details=action_details,
            self_harm_detected=self_harm_detected,
            crisis_resources=crisis_resources,
            disclosure_required=disclosure_required,
            disclosure_text=disclosure_text,
            break_reminder_due=break_reminder_due,
            break_reminder_text=break_reminder_text,
            ns_output=ns_output if request.metadata.get("include_debug") else None,
            jr_output=jr_output if request.metadata.get("include_debug") else None,
            audit_trail=audit_trail if self.config.audit_enabled else [],
            total_latency_ms=total_latency,
            cache_hit=ns_output.cache_hit,
            requires_human_review=jr_output.human_review_required,
            human_review_reason=jr_output.reasoning if jr_output.human_review_required else None,
        )

        # Generate attestation if requested
        if request.include_attestation and self.config.attestation_enabled:
            result.attestation = self.attestation_generator.generate(
                content_id=result.content_id,
                content_hash=content_hash,
                result=result,
            )

            # Create ShadowTag cryptographic proof
            try:
                proof = await self.shadowtag_client.create_compliance_proof(
                    assessment_result={
                        "assessment_id": result.assessment_id,
                        "is_compliant": result.is_compliant,
                        "compliance_score": result.compliance_score,
                        "risk_tier": result.risk_tier.value,
                        "violation_count": result.violation_count,
                    },
                    framework="CA_AI_CHATBOT",
                )
                # Update attestation with ShadowTag signature
                if result.attestation:
                    result.attestation.signature = proof.attestation.signature
            except Exception as e:
                logger.warning(f"ShadowTag attestation failed: {e}")

        # Update stats
        if result.is_compliant:
            self._stats["compliant"] += 1
        else:
            self._stats["non_compliant"] += 1

        # Update average latency
        n = self._stats["total_assessments"]
        self._stats["avg_latency_ms"] = (
            self._stats["avg_latency_ms"] * (n - 1) + total_latency
        ) / n

        return result

    async def batch_assess(
        self,
        request: BatchAssessmentRequest,
    ) -> BatchAssessmentResult:
        """
        Batch assessment for multiple content items.
        """
        start_time = time.time()
        results: list[CaliforniaAIAssessmentResult] = []
        errors = 0

        if request.parallel:
            # Run in parallel
            tasks = [self.assess(item) for item in request.items]

            if request.fail_fast:
                # Stop on first error
                for coro in asyncio.as_completed(tasks):
                    try:
                        result = await coro
                        results.append(result)
                    except Exception as e:
                        errors += 1
                        logger.error(f"Batch item failed: {e}")
                        break
            else:
                # Gather all results
                completed = await asyncio.gather(*tasks, return_exceptions=True)
                for r in completed:
                    if isinstance(r, Exception):
                        errors += 1
                        logger.error(f"Batch item failed: {r}")
                    else:
                        results.append(r)
        else:
            # Sequential processing
            for item in request.items:
                try:
                    result = await self.assess(item)
                    results.append(result)
                except Exception as e:
                    errors += 1
                    logger.error(f"Batch item failed: {e}")
                    if request.fail_fast:
                        break

        total_latency = (time.time() - start_time) * 1000
        compliant_count = sum(1 for r in results if r.is_compliant)

        return BatchAssessmentResult(
            total_items=len(request.items),
            compliant_items=compliant_count,
            non_compliant_items=len(results) - compliant_count,
            error_items=errors,
            results=results,
            overall_compliance_rate=compliant_count / len(results) if results else 0.0,
            total_latency_ms=total_latency,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get orchestrator statistics"""
        total = self._stats["total_assessments"]
        return {
            **self._stats,
            "compliance_rate": (self._stats["compliant"] / total if total > 0 else 1.0),
            "cache_hit_rate": (self._stats["cache_hits"] / total if total > 0 else 0.0),
            "crisis_response_rate": (self._stats["crisis_responses"] / total if total > 0 else 0.0),
        }


# =============================================================================
# Factory Function
# =============================================================================


def create_cor_orchestrator(
    enable_caching: bool = True,
    enable_batching: bool = True,
) -> CorOrchestrator:
    """Create configured Cor Orchestrator"""
    config = CorConfig(
        enable_caching=enable_caching,
        enable_batching=enable_batching,
    )
    return CorOrchestrator(config=config)


# Global instance
_cor_orchestrator: CorOrchestrator | None = None


def get_cor_orchestrator() -> CorOrchestrator:
    """Get or create global Cor Orchestrator instance"""
    global _cor_orchestrator
    if _cor_orchestrator is None:
        _cor_orchestrator = create_cor_orchestrator()
    return _cor_orchestrator
