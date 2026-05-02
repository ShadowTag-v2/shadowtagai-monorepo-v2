"""AiUCRM Audit Module — Compliance logging and reporting.

Provides audit trail for all governance decisions made by the AiUCRM engine.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """Single audit log entry."""

    timestamp: datetime
    operation: str
    decision: str
    risk_level: str
    details: dict[str, Any] = field(default_factory=dict)
    user_id: str | None = None


@dataclass
class ComplianceReport:
    """Aggregated compliance report for a time period."""

    report_id: str
    generated_at: datetime = field(default_factory=datetime.utcnow)
    entries: list[AuditEntry] = field(default_factory=list)
    total_decisions: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    escalated_count: int = 0

    @property
    def approval_rate(self) -> float:
        """Calculate approval rate."""
        if self.total_decisions == 0:
            return 0.0
        return self.approved_count / self.total_decisions

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage/transport."""
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at.isoformat(),
            "total_decisions": self.total_decisions,
            "approved_count": self.approved_count,
            "rejected_count": self.rejected_count,
            "escalated_count": self.escalated_count,
            "approval_rate": self.approval_rate,
        }


class AuditLogger:
    """Compliance audit logger for AiUCRM decisions."""

    def __init__(self, *, storage_backend: str = "memory"):
        self._entries: list[AuditEntry] = []
        self._storage_backend = storage_backend
        logger.info("AuditLogger initialized with backend: %s", storage_backend)

    def log_decision(
        self,
        operation: str,
        decision: str,
        risk_level: str,
        details: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> AuditEntry:
        """Record a governance decision."""
        entry = AuditEntry(
            timestamp=datetime.utcnow(),
            operation=operation,
            decision=decision,
            risk_level=risk_level,
            details=details or {},
            user_id=user_id,
        )
        self._entries.append(entry)
        logger.debug("Audit entry logged: %s -> %s", operation, decision)
        return entry

    def generate_report(self, report_id: str) -> ComplianceReport:
        """Generate a compliance report from logged entries."""
        report = ComplianceReport(
            report_id=report_id,
            entries=list(self._entries),
            total_decisions=len(self._entries),
            approved_count=sum(1 for e in self._entries if e.decision == "approved"),
            rejected_count=sum(1 for e in self._entries if e.decision == "rejected"),
            escalated_count=sum(1 for e in self._entries if e.decision == "escalated"),
        )
        return report
