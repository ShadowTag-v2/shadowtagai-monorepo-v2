# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""LangGraph State Models for Judge 6 Governance Engine

Defines the three-phase state machine:
1. AssessmentState - OPA Fast Check (JREngine)
2. DebateState - Judge#6 Reasoning (PanelDebateSystem)
3. AuditState - Audit Logger (AuditCompressKernel)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class AssessmentStatus(StrEnum):
    """Status of assessment phase"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DebateStatus(StrEnum):
    """Status of debate phase"""

    NOT_TRIGGERED = "not_triggered"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditStatus(StrEnum):
    """Status of audit logging phase"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class VotingMode(StrEnum):
    """Voting mode selection"""

    SWARM = "swarm"  # Default: 200-agent heuristic + conditional LLM
    SINGLE_ROUND = "single_round"  # Memory-augmented single vote
    THREE_PHASE = "three_phase"  # Legacy: Prosecutor → Defender → Judge
    DISABLED = "disabled"  # Skip voting entirely


class SwarmVoteMethod(StrEnum):
    """How the swarm vote was determined"""

    HEURISTIC = "heuristic"  # All 200 agents voted heuristically ($0)
    LLM_TIEBREAKER = "llm_tiebreaker"  # Unclear consensus, LLM broke tie ($0.0003)


class RiskLevel(StrEnum):
    """Risk levels from ATP 5-19 risk matrix"""

    EXTREMELY_HIGH = "EH"
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


@dataclass
class AssessmentState:
    """Assessment state for OPA Fast Check phase.
    Wraps existing JREngine validation.
    Target latency: <500μs (deterministic, no LLM calls)
    """

    decision_id: str
    trace_id: str
    context: dict[str, Any]

    # Assessment execution
    status: AssessmentStatus = AssessmentStatus.PENDING
    purpose: dict[str, Any] | None = None
    reasons: list[dict[str, Any]] = field(default_factory=list)
    brakes: list[dict[str, Any]] = field(default_factory=list)
    risk_level: RiskLevel | None = None
    confidence: float = 0.0

    # Results
    assessment_result: dict[str, Any] | None = None
    assessment_latency_us: float = 0.0
    assessment_errors: list[str] = field(default_factory=list)

    # Metadata
    started_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def should_proceed(self) -> bool:
        """Determine if action should proceed based on risk level"""
        return self.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]

    def requires_escalation(self) -> bool:
        """Check if human escalation required"""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.EXTREMELY_HIGH]

    def to_dict(self) -> dict[str, Any]:
        """Serialize for checkpoint/recovery"""
        return {
            "decision_id": self.decision_id,
            "trace_id": self.trace_id,
            "context": self.context,
            "status": self.status.value,
            "purpose": self.purpose,
            "reasons": self.reasons,
            "brakes": self.brakes,
            "risk_level": self.risk_level.value if self.risk_level else None,
            "confidence": self.confidence,
            "assessment_result": self.assessment_result,
            "assessment_latency_us": self.assessment_latency_us,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class DebateRound:
    """Single round of panel debate"""

    round_number: int
    prosecutor_argument: str
    defender_argument: str
    judge_analysis: str
    consensus_score: float
    models_used: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DebateState:
    """Debate/Voting state for Judge#6 Reasoning phase.

    Supports two modes:
    - SINGLE_ROUND (default): Memory-augmented single vote using precedents
    - THREE_PHASE (legacy): Prosecutor → Defender → Judge pattern

    Triggered conditionally when confidence <80% or high risk.
    """

    decision_id: str

    # Voting mode selection
    voting_mode: VotingMode = VotingMode.SWARM  # Default to swarm voting

    # === SWARM MODE FIELDS (Default) ===
    swarm_vote: "SwarmVoteState | None" = None

    # Debate execution
    status: DebateStatus = DebateStatus.NOT_TRIGGERED
    should_debate: bool = False
    debate_trigger_reason: str | None = None

    # === SINGLE_ROUND MODE FIELDS ===
    # Memory-augmented voting
    precedent_ids: list[str] = field(default_factory=list)
    precedent_votes: list[dict[str, Any]] = field(default_factory=list)
    memory_context: str | None = None
    single_vote_reasoning: str | None = None

    # === THREE_PHASE MODE FIELDS (Legacy) ===
    # Debate rounds
    rounds: list[DebateRound] = field(default_factory=list)
    current_round: int = 0
    max_rounds: int = 3
    consensus_threshold: float = 0.80

    # Final result (used by both modes)
    debate_conclusion: str | None = None
    final_confidence: float | None = None
    final_decision: str | None = None  # APPROVE, REJECT, ESCALATE

    # Metrics
    debate_latency_ms: float = 0.0
    debate_cost_usd: float = 0.0
    debate_errors: list[str] = field(default_factory=list)

    # Metadata
    started_at: datetime | None = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for checkpoint/recovery"""
        return {
            "decision_id": self.decision_id,
            "voting_mode": self.voting_mode.value,
            "status": self.status.value,
            "should_debate": self.should_debate,
            "debate_trigger_reason": self.debate_trigger_reason,
            # Swarm mode fields (default)
            "swarm_vote": self.swarm_vote.to_dict() if self.swarm_vote else None,
            # Single-round mode fields
            "precedent_ids": self.precedent_ids,
            "precedent_votes": self.precedent_votes,
            "memory_context": self.memory_context,
            "single_vote_reasoning": self.single_vote_reasoning,
            # Three-phase mode fields (legacy)
            "rounds": [
                {
                    "round_number": r.round_number,
                    "prosecutor_argument": r.prosecutor_argument,
                    "defender_argument": r.defender_argument,
                    "judge_analysis": r.judge_analysis,
                    "consensus_score": r.consensus_score,
                    "models_used": r.models_used,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self.rounds
            ],
            "current_round": self.current_round,
            "debate_conclusion": self.debate_conclusion,
            "final_confidence": self.final_confidence,
            "final_decision": self.final_decision,
            "debate_latency_ms": self.debate_latency_ms,
            "debate_cost_usd": self.debate_cost_usd,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class SwarmVoteState:
    """Swarm voting state for n-autoresearch/Kosmos/BioAgents2 integration.

    Cost: $0.00006/decision average (5x under $0.0003 target)
    - 80% clear consensus: $0 (heuristic only)
    - 20% unclear → LLM tiebreaker: $0.0003

    Latency: ~7ms (clear) / ~77ms (unclear) / ~21ms average
    """

    decision_id: str

    # Vote result
    decision: str | None = None  # APPROVE, REJECT, ESCALATE
    confidence: float = 0.0
    method: SwarmVoteMethod = SwarmVoteMethod.HEURISTIC

    # Consensus metrics
    consensus_ratio: float = 0.0
    total_votes: int = 0
    weighted_approve: float = 0.0
    weighted_total: float = 0.0

    # LLM tiebreaker info
    llm_override: bool = False
    llm_tokens_used: int = 0

    # Cost tracking
    cost_usd: float = 0.0  # $0 for heuristic, $0.0003 for LLM

    # Latency
    latency_ms: float = 0.0

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for checkpoint/recovery"""
        return {
            "decision_id": self.decision_id,
            "decision": self.decision,
            "confidence": self.confidence,
            "method": self.method.value,
            "consensus_ratio": self.consensus_ratio,
            "total_votes": self.total_votes,
            "weighted_approve": self.weighted_approve,
            "weighted_total": self.weighted_total,
            "llm_override": self.llm_override,
            "llm_tokens_used": self.llm_tokens_used,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class AuditEntry:
    """Single audit log entry"""

    timestamp: datetime
    event_type: str
    details: dict[str, Any]
    severity: str = "INFO"


@dataclass
class AuditState:
    """Audit state for Audit Logger phase.
    Wraps existing AuditCompressKernel.
    Compresses to ATP 5-19 format (≤487 bytes target).
    """

    decision_id: str
    trace_id: str

    # Audit execution
    status: AuditStatus = AuditStatus.PENDING

    # Audit trail accumulation
    entries: list[AuditEntry] = field(default_factory=list)

    # Compressed audit result
    compressed_audit: bytes | None = None
    compression_ratio: float = 0.0
    original_size_bytes: int = 0
    compressed_size_bytes: int = 0
    checksum: str | None = None

    # Metadata
    audit_latency_ms: float = 0.0
    audit_errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_entry(self, event_type: str, details: dict[str, Any], severity: str = "INFO") -> None:
        """Add audit entry"""
        self.entries.append(
            AuditEntry(
                timestamp=datetime.utcnow(),
                event_type=event_type,
                details=details,
                severity=severity,
            ),
        )
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Serialize for checkpoint/recovery"""
        return {
            "decision_id": self.decision_id,
            "trace_id": self.trace_id,
            "status": self.status.value,
            "entries": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type,
                    "details": e.details,
                    "severity": e.severity,
                }
                for e in self.entries
            ],
            "compression_ratio": self.compression_ratio,
            "original_size_bytes": self.original_size_bytes,
            "compressed_size_bytes": self.compressed_size_bytes,
            "checksum": self.checksum,
            "audit_latency_ms": self.audit_latency_ms,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class GovernanceState:
    """Complete governance state machine state.
    This is what LangGraph's StateGraph manages.
    """

    # Tracking
    decision_id: str
    trace_id: str

    # The three phases of the kill chain
    assessment: AssessmentState
    debate: DebateState
    audit: AuditState

    # Kill chain execution control
    current_phase: str = "assessment"
    phase_sequence: list[str] = field(default_factory=lambda: ["assessment", "debate", "audit"])

    # Final output
    final_decision: bool | None = None
    final_confidence: float | None = None
    final_reasoning: str | None = None

    # Memory references (for Mem0 integration)
    similar_precedents: list[str] = field(default_factory=list)
    memory_fingerprint: str | None = None

    # Global metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    total_latency_ms: float = 0.0

    # Recovery/checkpoint info
    checkpoint_id: str | None = None
    last_successful_phase: str | None = None

    def full_checkpoint(self) -> dict[str, Any]:
        """Create full recoverable checkpoint"""
        return {
            "decision_id": self.decision_id,
            "trace_id": self.trace_id,
            "assessment": self.assessment.to_dict(),
            "debate": self.debate.to_dict(),
            "audit": self.audit.to_dict(),
            "current_phase": self.current_phase,
            "final_decision": self.final_decision,
            "final_confidence": self.final_confidence,
            "final_reasoning": self.final_reasoning,
            "similar_precedents": self.similar_precedents,
            "memory_fingerprint": self.memory_fingerprint,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_latency_ms": self.total_latency_ms,
            "last_successful_phase": self.last_successful_phase,
        }
