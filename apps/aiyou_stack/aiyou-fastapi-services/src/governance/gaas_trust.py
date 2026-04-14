"""GaaS (Governance-as-a-Service) Trust Factor System.

Implements longitudinal compliance scoring with severity-aware penalization
and graduated enforcement modes (coercive, normative, adaptive).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ViolationSeverity(StrEnum):
    """Severity classification for policy violations."""

    CRITICAL = "critical"  # Financial fraud, data breach, etc.
    HIGH = "high"  # Compliance violation, security risk
    MEDIUM = "medium"  # Process deviation, minor policy breach
    LOW = "low"  # Formatting, documentation issues


class EnforcementMode(StrEnum):
    """GaaS enforcement modes based on trust tier."""

    COERCIVE = "coercive"  # Block immediately
    NORMATIVE = "normative"  # Warn and log
    ADAPTIVE = "adaptive"  # Trust-based escalation


class TrustTier(StrEnum):
    """Trust tiers determining enforcement behavior."""

    HIGH = "high"  # >0.7
    MEDIUM = "medium"  # 0.3-0.7
    LOW = "low"  # <0.3


class ViolationRecord(BaseModel):
    """Record of a policy violation."""

    violation_id: str
    timestamp: datetime
    agent_id: str
    policy_id: str
    severity: ViolationSeverity
    description: str
    penalty_applied: float


@dataclass
class TrustScore:
    """Agent trust score with metadata."""

    agent_id: str
    score: float = 1.0  # Start with full trust
    tier: TrustTier = TrustTier.HIGH
    violations: list[ViolationRecord] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    total_decisions: int = 0
    successful_decisions: int = 0


class GaaSTrustManager:
    """Manages trust scoring for agent-based governance.

    Implements GaaS framework with:
    - Severity-aware violation penalties
    - Time-decay for violation recovery
    - Graduated enforcement based on trust tiers
    """

    def __init__(
        self,
        high_threshold: float = 0.7,
        low_threshold: float = 0.3,
        decay_days: int = 90,
    ):
        """Initialize trust manager.

        Args:
            high_threshold: Score above which agent is high trust
            low_threshold: Score below which agent is low trust
            decay_days: Days for violation penalty to decay to zero

        """
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.decay_days = decay_days

        # Trust scores by agent
        self.trust_scores: dict[str, TrustScore] = {}

        # Penalty weights by severity
        self.penalty_weights = {
            ViolationSeverity.CRITICAL: 0.30,  # 30% trust reduction
            ViolationSeverity.HIGH: 0.15,  # 15% reduction
            ViolationSeverity.MEDIUM: 0.05,  # 5% reduction
            ViolationSeverity.LOW: 0.01,  # 1% reduction
        }

    def get_trust_score(self, agent_id: str) -> TrustScore:
        """Get current trust score for agent."""
        if agent_id not in self.trust_scores:
            self.trust_scores[agent_id] = TrustScore(agent_id=agent_id)
        return self.trust_scores[agent_id]

    def record_decision(
        self,
        agent_id: str,
        success: bool,
        violation: ViolationRecord | None = None,
    ) -> TrustScore:
        """Record decision outcome and update trust score.

        Args:
            agent_id: Agent identifier
            success: Whether decision was compliant
            violation: Violation record if decision failed

        Returns:
            Updated trust score

        """
        trust = self.get_trust_score(agent_id)

        # Update decision counts
        trust.total_decisions += 1
        if success:
            trust.successful_decisions += 1
        # Record violation
        elif violation:
            trust.violations.append(violation)

            # Apply penalty
            penalty = self.penalty_weights[violation.severity]
            trust.score = max(0.0, trust.score - penalty)

        # Apply time decay to recover from old violations
        trust.score = self._apply_decay(trust)

        # Update tier
        trust.tier = self._calculate_tier(trust.score)
        trust.last_updated = datetime.utcnow()

        return trust

    def _apply_decay(self, trust: TrustScore) -> float:
        """Apply time-decay to trust score recovery.

        Violations older than decay_days contribute zero penalty.
        Linear decay between violation date and decay_days.
        """
        if not trust.violations:
            return min(1.0, trust.score + 0.01)  # Slow recovery if no violations

        now = datetime.utcnow()
        total_penalty = 0.0

        for violation in trust.violations:
            age_days = (now - violation.timestamp).days

            if age_days >= self.decay_days:
                # Violation fully decayed
                continue

            # Linear decay
            decay_factor = 1.0 - (age_days / self.decay_days)
            penalty = self.penalty_weights[violation.severity] * decay_factor
            total_penalty += penalty

        # Calculate score: start at 1.0, subtract active penalties
        return max(0.0, min(1.0, 1.0 - total_penalty))

    def _calculate_tier(self, score: float) -> TrustTier:
        """Calculate trust tier from score."""
        if score > self.high_threshold:
            return TrustTier.HIGH
        if score >= self.low_threshold:
            return TrustTier.MEDIUM
        return TrustTier.LOW

    def get_enforcement_mode(
        self,
        agent_id: str,
        rule_type: str = "normative",
    ) -> EnforcementMode:
        """Determine enforcement mode based on trust tier and rule type.

        GaaS Matrix:
                    | Normative Rules | Coercive Rules |
        High (>0.7) | Allow          | Allow          |
        Med (0.3-0.7)| Warn           | Block          |
        Low (<0.3)  | Block          | Block (immed)  |

        Args:
            agent_id: Agent identifier
            rule_type: "normative" or "coercive"

        Returns:
            Enforcement mode to apply

        """
        trust = self.get_trust_score(agent_id)

        if trust.tier == TrustTier.HIGH:
            return EnforcementMode.ADAPTIVE  # Allow with monitoring

        if trust.tier == TrustTier.MEDIUM:
            if rule_type == "normative":
                return EnforcementMode.NORMATIVE  # Warn
            return EnforcementMode.COERCIVE  # Block

        # Low trust
        return EnforcementMode.COERCIVE  # Always block

    def should_block(
        self,
        agent_id: str,
        rule_type: str = "normative",
    ) -> tuple[bool, EnforcementMode]:
        """Determine if action should be blocked based on trust.

        Args:
            agent_id: Agent identifier
            rule_type: "normative" or "coercive"

        Returns:
            Tuple of (should_block, enforcement_mode)

        """
        mode = self.get_enforcement_mode(agent_id, rule_type)

        if mode == EnforcementMode.COERCIVE:
            return True, mode
        if mode == EnforcementMode.NORMATIVE:
            return False, mode  # Warn but allow
        return False, mode  # Trust-based allow

    def get_metrics(self, agent_id: str) -> dict:
        """Get trust metrics for agent."""
        trust = self.get_trust_score(agent_id)

        return {
            "agent_id": agent_id,
            "trust_score": trust.score,
            "trust_tier": trust.tier.value,
            "total_decisions": trust.total_decisions,
            "successful_decisions": trust.successful_decisions,
            "success_rate": (
                trust.successful_decisions / trust.total_decisions
                if trust.total_decisions > 0
                else 0.0
            ),
            "violation_count": len(trust.violations),
            "recent_violations": len(
                [v for v in trust.violations if (datetime.utcnow() - v.timestamp).days <= 30],
            ),
            "last_updated": trust.last_updated.isoformat(),
        }
