# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Whiteboard: Shared world model that all agents can see and write to.

This is the 'single source of truth' for the Shadowtag swarm.
Implements event-driven updates so agents see changes immediately.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FindingType(Enum):
    """Types of watermark findings."""

    VISUAL_WATERMARK = "visual_watermark"
    TEXT_STEGANOGRAPHY = "text_steganography"
    METADATA_MARKER = "metadata_marker"
    C2PA_MANIFEST = "c2pa_manifest"
    SYNTHID_SIGNATURE = "synthid_signature"
    CUSTOM_WATERMARK = "custom_watermark"
    NO_WATERMARK = "no_watermark"


class ConsensusState(Enum):
    """State of agent consensus on a finding."""

    PENDING = "pending"  # Not enough votes
    AGREED = "agreed"  # ≥70% agreement
    CONTESTED = "contested"  # Significant disagreement
    INVESTIGATING = "investigating"  # Deeper analysis triggered


@dataclass
class Vote:
    """An agent's vote on a finding."""

    agent_id: str
    agent_persona: str
    agrees: bool
    confidence: float  # 0.0 - 1.0
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Vote:
        if isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class Finding:
    """A watermark detection finding posted to the whiteboard."""

    id: str
    finding_type: FindingType
    source_path: str  # File path or Google Drive ID
    description: str
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    discovered_by: str = ""  # Agent ID
    votes: list[Vote] = field(default_factory=list)
    consensus: ConsensusState = ConsensusState.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def agreement_ratio(self) -> float:
        """Calculate ratio of agreeing votes."""
        if not self.votes:
            return 0.0
        agreeing = sum(1 for v in self.votes if v.agrees)
        return agreeing / len(self.votes)

    @property
    def weighted_confidence(self) -> float:
        """Calculate confidence weighted by vote confidence."""
        if not self.votes:
            return self.confidence
        total_weight = sum(v.confidence for v in self.votes)
        if total_weight == 0:
            return self.confidence
        weighted = sum(v.confidence * (1.0 if v.agrees else 0.0) for v in self.votes)
        return weighted / total_weight

    def to_dict(self) -> dict[str, Any]:
        d = {
            "id": self.id,
            "finding_type": self.finding_type.value,
            "source_path": self.source_path,
            "description": self.description,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "discovered_by": self.discovered_by,
            "votes": [v.to_dict() for v in self.votes],
            "consensus": self.consensus.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Finding:
        data["finding_type"] = FindingType(data["finding_type"])
        data["consensus"] = ConsensusState(data["consensus"])
        data["votes"] = [Vote.from_dict(v) for v in data.get("votes", [])]
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


class Whiteboard:
    """Shared world model for Shadowtag agent swarm.

    All agents can:
    - Read all findings
    - Post new findings
    - Vote on existing findings
    - Subscribe to updates

    Maintains consensus state and triggers deeper investigation
    when disagreement is detected.
    """

    def __init__(
        self,
        session_id: str,
        consensus_threshold: float = 0.70,
        min_votes_for_consensus: int = 3,
    ):
        self.session_id = session_id
        self.consensus_threshold = consensus_threshold
        self.min_votes_for_consensus = min_votes_for_consensus

        self._findings: dict[str, Finding] = {}
        self._subscribers: list[Callable[[str, Finding], None]] = []
        self._lock = asyncio.Lock()

        # Metrics
        self.total_findings = 0
        self.total_votes = 0
        self.consensus_reached = 0
        self.contests_triggered = 0

    async def post_finding(self, finding: Finding) -> None:
        """Post a new finding to the whiteboard."""
        async with self._lock:
            self._findings[finding.id] = finding
            self.total_findings += 1
            finding.updated_at = datetime.utcnow()

        await self._notify_subscribers("new_finding", finding)

    async def add_vote(
        self,
        finding_id: str,
        vote: Vote,
    ) -> ConsensusState:
        """Add a vote to a finding and update consensus state."""
        async with self._lock:
            if finding_id not in self._findings:
                raise ValueError(f"Finding {finding_id} not found")

            finding = self._findings[finding_id]

            # Check if agent already voted
            existing = next(
                (i for i, v in enumerate(finding.votes) if v.agent_id == vote.agent_id),
                None,
            )
            if existing is not None:
                finding.votes[existing] = vote
            else:
                finding.votes.append(vote)
                self.total_votes += 1

            # Update consensus state
            old_consensus = finding.consensus
            finding.consensus = self._calculate_consensus(finding)
            finding.updated_at = datetime.utcnow()

            if (
                finding.consensus == ConsensusState.AGREED
                and old_consensus != ConsensusState.AGREED
            ):
                self.consensus_reached += 1
            elif (
                finding.consensus == ConsensusState.CONTESTED
                and old_consensus != ConsensusState.CONTESTED
            ):
                self.contests_triggered += 1

        await self._notify_subscribers("vote_added", finding)
        return finding.consensus

    def _calculate_consensus(self, finding: Finding) -> ConsensusState:
        """Calculate consensus state based on votes."""
        if len(finding.votes) < self.min_votes_for_consensus:
            return ConsensusState.PENDING

        ratio = finding.agreement_ratio

        if ratio >= self.consensus_threshold:
            return ConsensusState.AGREED
        if ratio <= (1 - self.consensus_threshold):
            # Strong disagreement - also consensus but negative
            return ConsensusState.AGREED
        # Significant disagreement triggers deeper investigation
        return ConsensusState.CONTESTED

    def get_finding(self, finding_id: str) -> Finding | None:
        """Get a specific finding by ID."""
        return self._findings.get(finding_id)

    def get_all_findings(self) -> list[Finding]:
        """Get all findings."""
        return list(self._findings.values())

    def get_findings_by_type(self, finding_type: FindingType) -> list[Finding]:
        """Get findings filtered by type."""
        return [f for f in self._findings.values() if f.finding_type == finding_type]

    def get_findings_by_consensus(self, state: ConsensusState) -> list[Finding]:
        """Get findings filtered by consensus state."""
        return [f for f in self._findings.values() if f.consensus == state]

    def get_contested_findings(self) -> list[Finding]:
        """Get findings that need deeper investigation."""
        return self.get_findings_by_consensus(ConsensusState.CONTESTED)

    def get_pending_findings(self) -> list[Finding]:
        """Get findings awaiting more votes."""
        return self.get_findings_by_consensus(ConsensusState.PENDING)

    def subscribe(self, callback: Callable[[str, Finding], None]) -> None:
        """Subscribe to whiteboard updates."""
        self._subscribers.append(callback)

    async def _notify_subscribers(self, event: str, finding: Finding) -> None:
        """Notify all subscribers of an update."""
        for callback in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event, finding)
                else:
                    callback(event, finding)
            except Exception:
                pass  # Don't let subscriber errors break the whiteboard

    def get_summary(self) -> dict[str, Any]:
        """Get summary of whiteboard state."""
        findings_by_consensus = defaultdict(int)
        findings_by_type = defaultdict(int)

        for finding in self._findings.values():
            findings_by_consensus[finding.consensus.value] += 1
            findings_by_type[finding.finding_type.value] += 1

        return {
            "session_id": self.session_id,
            "total_findings": self.total_findings,
            "total_votes": self.total_votes,
            "consensus_reached": self.consensus_reached,
            "contests_triggered": self.contests_triggered,
            "by_consensus": dict(findings_by_consensus),
            "by_type": dict(findings_by_type),
            "avg_votes_per_finding": (
                self.total_votes / self.total_findings if self.total_findings > 0 else 0
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize whiteboard state."""
        return {
            "session_id": self.session_id,
            "consensus_threshold": self.consensus_threshold,
            "min_votes_for_consensus": self.min_votes_for_consensus,
            "findings": {fid: f.to_dict() for fid, f in self._findings.items()},
            "metrics": {
                "total_findings": self.total_findings,
                "total_votes": self.total_votes,
                "consensus_reached": self.consensus_reached,
                "contests_triggered": self.contests_triggered,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Whiteboard:
        """Deserialize whiteboard state."""
        wb = cls(
            session_id=data["session_id"],
            consensus_threshold=data.get("consensus_threshold", 0.70),
            min_votes_for_consensus=data.get("min_votes_for_consensus", 3),
        )

        for fid, fdata in data.get("findings", {}).items():
            wb._findings[fid] = Finding.from_dict(fdata)

        metrics = data.get("metrics", {})
        wb.total_findings = metrics.get("total_findings", len(wb._findings))
        wb.total_votes = metrics.get("total_votes", 0)
        wb.consensus_reached = metrics.get("consensus_reached", 0)
        wb.contests_triggered = metrics.get("contests_triggered", 0)

        return wb
