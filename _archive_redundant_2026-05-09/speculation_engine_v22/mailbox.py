# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Multi-Agent Mailbox — Plan approval delegation pattern.

Architecture:
  Implements a mailbox pattern for delegating plan approval to multiple
  agents (e.g., security reviewer, cost analyst, architecture board).

  Each agent can vote on a plan, and the plan is approved/rejected based
  on configurable quorum rules.

States:
  PENDING  → Awaiting votes
  APPROVED → Quorum reached (all required approvals received)
  REJECTED → Any required agent rejected
  EXPIRED  → Voting window closed

Usage::

    from speculation_engine.mailbox import AgentMailbox, ApprovalPolicy

    mailbox = AgentMailbox(
        policy=ApprovalPolicy(required_agents=["security", "arch"]),
    )
    envelope = mailbox.submit_plan(plan_id="plan-001", plan_data={...})
    mailbox.cast_vote("security", plan_id="plan-001", approved=True)
    mailbox.cast_vote("arch", plan_id="plan-001", approved=True)
    assert envelope.status == "approved"
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from speculation_engine.telemetry import SpanContext, log_speculation_event

logger = logging.getLogger(__name__)


class ApprovalStatus(StrEnum):
    """Status of a plan approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class AgentVote:
    """A single agent's vote on a plan.

    Attributes:
        agent_id: Identity of the voting agent.
        approved: Whether the agent approved the plan.
        reason: Optional justification for the vote.
        timestamp: When the vote was cast.
        metadata: Additional vote metadata.
    """

    agent_id: str
    approved: bool
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalPolicy:
    """Policy governing plan approval quorum.

    Attributes:
        required_agents: Agent IDs that MUST vote to approve.
        optional_agents: Agent IDs whose votes are recorded but not required.
        timeout_seconds: Maximum voting window before expiry.
        require_unanimous: If True, all required agents must approve.
            If False, a simple majority of required agents suffices.
    """

    required_agents: list[str] = field(default_factory=list)
    optional_agents: list[str] = field(default_factory=list)
    timeout_seconds: float = 120.0
    require_unanimous: bool = True


@dataclass
class ApprovalEnvelope:
    """An approval request envelope tracking votes.

    Attributes:
        plan_id: Unique plan identifier.
        plan_data: The plan being voted on.
        policy: The approval policy.
        votes: Collected votes.
        status: Current approval status.
        created_at: When the envelope was created.
        resolved_at: When the envelope reached a terminal state.
    """

    plan_id: str
    plan_data: dict[str, Any]
    policy: ApprovalPolicy
    votes: list[AgentVote] = field(default_factory=list)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None

    @property
    def is_terminal(self) -> bool:
        """Whether the envelope has reached a terminal state."""
        return self.status in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.EXPIRED)

    @property
    def pending_agents(self) -> list[str]:
        """Required agents that have not yet voted."""
        voted_ids = {v.agent_id for v in self.votes}
        return [a for a in self.policy.required_agents if a not in voted_ids]

    @property
    def approval_ratio(self) -> float:
        """Ratio of approvals to total required agent count."""
        if not self.policy.required_agents:
            return 1.0
        approved_count = sum(1 for v in self.votes if v.agent_id in self.policy.required_agents and v.approved)
        return approved_count / len(self.policy.required_agents)


class AgentMailbox:
    """Multi-agent plan approval mailbox.

    Manages the lifecycle of plan approval requests, collecting votes
    from designated agents and resolving based on quorum policy.

    Args:
        policy: The default approval policy for new envelopes.
    """

    def __init__(self, policy: ApprovalPolicy | None = None) -> None:
        self._default_policy = policy or ApprovalPolicy()
        self._envelopes: dict[str, ApprovalEnvelope] = {}
        self._history: list[ApprovalEnvelope] = []

    def submit_plan(
        self,
        plan_id: str,
        plan_data: dict[str, Any],
        *,
        policy: ApprovalPolicy | None = None,
    ) -> ApprovalEnvelope:
        """Submit a plan for multi-agent approval.

        Args:
            plan_id: Unique plan identifier.
            plan_data: The plan data to be reviewed.
            policy: Override policy for this specific plan.

        Returns:
            The new ApprovalEnvelope.

        Raises:
            ValueError: If a plan with this ID is already pending.
        """
        if plan_id in self._envelopes and not self._envelopes[plan_id].is_terminal:
            msg = f"Plan '{plan_id}' is already pending approval"
            raise ValueError(msg)

        envelope = ApprovalEnvelope(
            plan_id=plan_id,
            plan_data=plan_data,
            policy=policy or self._default_policy,
        )
        self._envelopes[plan_id] = envelope

        log_speculation_event(
            event="mailbox_plan_submitted",
            plan_id=plan_id,
            required_agents=",".join(envelope.policy.required_agents),
        )
        logger.info("Plan '%s' submitted for approval by %s", plan_id, envelope.policy.required_agents)
        return envelope

    def cast_vote(
        self,
        agent_id: str,
        plan_id: str,
        *,
        approved: bool,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ApprovalEnvelope:
        """Cast a vote on a pending plan.

        Args:
            agent_id: The voting agent's identity.
            plan_id: The plan being voted on.
            approved: Whether the agent approves.
            reason: Optional justification.
            metadata: Additional vote metadata.

        Returns:
            The updated ApprovalEnvelope.

        Raises:
            KeyError: If the plan_id is not found.
            ValueError: If the plan is no longer pending.
        """
        if plan_id not in self._envelopes:
            msg = f"Plan '{plan_id}' not found"
            raise KeyError(msg)

        envelope = self._envelopes[plan_id]
        if envelope.is_terminal:
            msg = f"Plan '{plan_id}' is already {envelope.status}"
            raise ValueError(msg)

        with SpanContext(
            "mailbox.cast_vote",
            agent_id=agent_id,
            plan_id=plan_id,
            approved=approved,
        ) as span:
            # Check for duplicate votes
            for existing_vote in envelope.votes:
                if existing_vote.agent_id == agent_id:
                    logger.warning("Agent '%s' already voted on plan '%s', ignoring duplicate", agent_id, plan_id)
                    span.set_attribute("duplicate", True)
                    return envelope

            vote = AgentVote(
                agent_id=agent_id,
                approved=approved,
                reason=reason,
                metadata=metadata or {},
            )
            envelope.votes.append(vote)

            log_speculation_event(
                event="mailbox_vote_cast",
                plan_id=plan_id,
                agent_id=agent_id,
                approved=approved,
            )

            # Check if the envelope can be resolved
            self._try_resolve(envelope)
            span.set_attribute("status", envelope.status.value)
            span.set_attribute("approval_ratio", envelope.approval_ratio)

        return envelope

    def get_envelope(self, plan_id: str) -> ApprovalEnvelope | None:
        """Get an approval envelope by plan ID."""
        return self._envelopes.get(plan_id)

    def check_timeouts(self) -> list[str]:
        """Check all pending envelopes for timeouts.

        Returns:
            List of plan_ids that were expired.
        """
        expired: list[str] = []
        now = time.time()

        for plan_id, envelope in self._envelopes.items():
            if envelope.status != ApprovalStatus.PENDING:
                continue
            elapsed = now - envelope.created_at
            if elapsed > envelope.policy.timeout_seconds:
                envelope.status = ApprovalStatus.EXPIRED
                envelope.resolved_at = now
                self._history.append(envelope)
                expired.append(plan_id)
                log_speculation_event(
                    event="mailbox_expired",
                    plan_id=plan_id,
                    elapsed_s=round(elapsed, 1),
                )
                logger.warning("Plan '%s' expired after %.1fs", plan_id, elapsed)

        return expired

    @property
    def pending_plans(self) -> list[ApprovalEnvelope]:
        """All currently pending approval envelopes."""
        return [e for e in self._envelopes.values() if e.status == ApprovalStatus.PENDING]

    @property
    def history(self) -> list[ApprovalEnvelope]:
        """All resolved approval envelopes."""
        return list(self._history)

    def _try_resolve(self, envelope: ApprovalEnvelope) -> None:
        """Check if the envelope can be resolved based on votes and policy.

        Resolution rules:
          - If require_unanimous: all required agents must approve.
          - If not require_unanimous: majority of required agents must approve.
          - Any required agent rejection → REJECTED (if unanimous required).
        """
        required = set(envelope.policy.required_agents)
        if not required:
            # No required agents = auto-approve
            envelope.status = ApprovalStatus.APPROVED
            envelope.resolved_at = time.time()
            self._history.append(envelope)
            return

        required_votes = {v.agent_id: v for v in envelope.votes if v.agent_id in required}

        if envelope.policy.require_unanimous:
            # Check for any rejection
            for vote in required_votes.values():
                if not vote.approved:
                    envelope.status = ApprovalStatus.REJECTED
                    envelope.resolved_at = time.time()
                    self._history.append(envelope)
                    log_speculation_event(
                        event="mailbox_rejected",
                        plan_id=envelope.plan_id,
                        rejected_by=vote.agent_id,
                        reason=vote.reason,
                    )
                    return

            # Check if all required agents have voted
            if len(required_votes) == len(required):
                envelope.status = ApprovalStatus.APPROVED
                envelope.resolved_at = time.time()
                self._history.append(envelope)
                log_speculation_event(
                    event="mailbox_approved",
                    plan_id=envelope.plan_id,
                    approval_ratio=envelope.approval_ratio,
                )
        else:
            # Majority rule
            if len(required_votes) == len(required):
                approved_count = sum(1 for v in required_votes.values() if v.approved)
                if approved_count > len(required) / 2:
                    envelope.status = ApprovalStatus.APPROVED
                else:
                    envelope.status = ApprovalStatus.REJECTED
                envelope.resolved_at = time.time()
                self._history.append(envelope)
