# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for the multi-agent mailbox, policies, feature flags, and async consumer."""

from __future__ import annotations

import asyncio
import sys
import time

import pytest

sys.path.insert(0, "packages")

from speculation_engine.feature_flags import FeatureFlagStore, SpecFlags
from speculation_engine.mailbox import (
  AgentMailbox,
  ApprovalPolicy,
  ApprovalStatus,
)
from speculation_engine.mailbox_policies import (
  ARCHITECTURE_BOARD_POLICY,
  COST_POLICY,
  POLICY_CATALOG,
  SECURITY_POLICY,
  create_full_review_policy,
  create_lightweight_policy,
  select_policy,
)
from speculation_engine.async_consumer import AsyncSuggestionConsumer
from speculation_engine.consumer import SuggestionEntry


# ---------------------------------------------------------------
# Feature Flags Tests
# ---------------------------------------------------------------


class TestFeatureFlags:
  """Test the GrowthBook-equivalent FeatureFlagStore."""

  def test_default_values(self) -> None:
    """Defaults are applied when no overrides exist."""
    flags = FeatureFlagStore.create()
    assert flags.is_enabled(SpecFlags.PROACTIVE_SUGGESTIONS) is True
    assert flags.is_enabled(SpecFlags.SEMANTIC_ROUTING) is False

  def test_runtime_override(self) -> None:
    """Runtime set_flag overrides all layers."""
    flags = FeatureFlagStore.create()
    assert flags.is_enabled(SpecFlags.SEMANTIC_ROUTING) is False
    flags.set_flag(SpecFlags.SEMANTIC_ROUTING, True)
    assert flags.is_enabled(SpecFlags.SEMANTIC_ROUTING) is True

  def test_clear_runtime_overrides(self) -> None:
    """clear_runtime_overrides reverts to defaults."""
    flags = FeatureFlagStore.create()
    flags.set_flag(SpecFlags.SEMANTIC_ROUTING, True)
    assert flags.is_enabled(SpecFlags.SEMANTIC_ROUTING) is True
    flags.clear_runtime_overrides()
    assert flags.is_enabled(SpecFlags.SEMANTIC_ROUTING) is False

  def test_get_all_flags(self) -> None:
    """get_all_flags returns all flags with their sources."""
    flags = FeatureFlagStore.create()
    all_flags = flags.get_all_flags()
    assert "semantic_routing" in all_flags
    assert all_flags["semantic_routing"]["source"] in ("default", "file", "env")

  def test_save_and_reload(self, tmp_path) -> None:
    """Flags can be persisted and reloaded."""
    flags_file = tmp_path / "flags.json"

    flags = FeatureFlagStore.create(flags_file=flags_file)
    flags.set_flag(SpecFlags.SEMANTIC_ROUTING, True)
    flags.save_to_file(flags_file)

    reloaded = FeatureFlagStore.create(flags_file=flags_file)
    assert reloaded.is_enabled(SpecFlags.SEMANTIC_ROUTING) is True

  def test_evaluation_history(self) -> None:
    """Flag evaluations are logged for telemetry."""
    flags = FeatureFlagStore.create()
    flags.is_enabled(SpecFlags.SEMANTIC_ROUTING)
    flags.is_enabled(SpecFlags.ASYNC_CONSUMER)
    assert len(flags.evaluation_history) == 2

  def test_env_override(self, monkeypatch, tmp_path) -> None:
    """Environment variables override defaults."""
    monkeypatch.setenv("SPECULATION_FLAG_SEMANTIC_ROUTING", "1")
    # Use empty flag file to avoid .beads/feature_flags.json file overrides
    dummy_flags = tmp_path / "empty_flags.json"
    flags = FeatureFlagStore.create(flags_file=dummy_flags)
    assert flags.is_enabled(SpecFlags.SEMANTIC_ROUTING) is True


# ---------------------------------------------------------------
# Mailbox Tests
# ---------------------------------------------------------------


class TestAgentMailbox:
  """Test the multi-agent mailbox pattern."""

  def test_submit_plan(self) -> None:
    """Plans can be submitted for approval."""
    mailbox = AgentMailbox(policy=SECURITY_POLICY)
    envelope = mailbox.submit_plan("plan-001", {"steps": []})
    assert envelope.status == ApprovalStatus.PENDING
    assert envelope.plan_id == "plan-001"

  def test_unanimous_approval(self) -> None:
    """All required agents approving → APPROVED."""
    policy = ApprovalPolicy(
      required_agents=["agent_a", "agent_b"],
      require_unanimous=True,
    )
    mailbox = AgentMailbox(policy=policy)
    mailbox.submit_plan("plan-002", {"steps": []})
    mailbox.cast_vote("agent_a", "plan-002", approved=True)
    envelope = mailbox.cast_vote("agent_b", "plan-002", approved=True)
    assert envelope.status == ApprovalStatus.APPROVED

  def test_unanimous_rejection(self) -> None:
    """Any required agent rejecting (unanimous mode) → REJECTED."""
    policy = ApprovalPolicy(
      required_agents=["agent_a", "agent_b"],
      require_unanimous=True,
    )
    mailbox = AgentMailbox(policy=policy)
    mailbox.submit_plan("plan-003", {"steps": []})
    envelope = mailbox.cast_vote(
      "agent_a", "plan-003", approved=False, reason="security concern"
    )
    assert envelope.status == ApprovalStatus.REJECTED

  def test_majority_approval(self) -> None:
    """Majority of required agents approving (non-unanimous) → APPROVED."""
    policy = ApprovalPolicy(
      required_agents=["a", "b", "c"],
      require_unanimous=False,
    )
    mailbox = AgentMailbox(policy=policy)
    mailbox.submit_plan("plan-004", {"steps": []})
    mailbox.cast_vote("a", "plan-004", approved=True)
    mailbox.cast_vote("b", "plan-004", approved=True)
    envelope = mailbox.cast_vote("c", "plan-004", approved=False)
    assert envelope.status == ApprovalStatus.APPROVED

  def test_majority_rejection(self) -> None:
    """Majority rejection in non-unanimous mode → REJECTED."""
    policy = ApprovalPolicy(
      required_agents=["a", "b", "c"],
      require_unanimous=False,
    )
    mailbox = AgentMailbox(policy=policy)
    mailbox.submit_plan("plan-005", {"steps": []})
    mailbox.cast_vote("a", "plan-005", approved=False)
    mailbox.cast_vote("b", "plan-005", approved=False)
    envelope = mailbox.cast_vote("c", "plan-005", approved=True)
    assert envelope.status == ApprovalStatus.REJECTED

  def test_duplicate_vote_ignored(self) -> None:
    """Duplicate votes from the same agent are ignored."""
    # Use 2-agent policy so the plan stays PENDING after the first vote
    policy = ApprovalPolicy(
      required_agents=["security_reviewer", "cost_analyst"],
      require_unanimous=True,
    )
    mailbox = AgentMailbox(policy=policy)
    mailbox.submit_plan("plan-006", {"steps": []})
    mailbox.cast_vote("security_reviewer", "plan-006", approved=True)
    envelope = mailbox.cast_vote("security_reviewer", "plan-006", approved=False)
    # First vote wins; second is ignored — plan remains PENDING
    assert envelope.status == ApprovalStatus.PENDING
    # Verify only one vote was recorded
    assert len(envelope.votes) == 1

  def test_no_required_agents_auto_approves(self) -> None:
    """Empty required_agents list → auto-approve."""
    policy = ApprovalPolicy(required_agents=[])
    mailbox = AgentMailbox(policy=policy)
    envelope = mailbox.submit_plan("plan-007", {"steps": []})
    # Auto-approved on submit via _try_resolve
    mailbox.cast_vote("anyone", "plan-007", approved=True)
    assert envelope.status == ApprovalStatus.APPROVED

  def test_timeout_expiry(self) -> None:
    """Plans expire after timeout."""
    policy = ApprovalPolicy(
      required_agents=["agent_a"],
      timeout_seconds=0.001,  # Extremely short
    )
    mailbox = AgentMailbox(policy=policy)
    mailbox.submit_plan("plan-008", {"steps": []})
    time.sleep(0.01)
    expired = mailbox.check_timeouts()
    assert "plan-008" in expired
    assert mailbox.get_envelope("plan-008").status == ApprovalStatus.EXPIRED

  def test_pending_plans_property(self) -> None:
    """pending_plans returns only PENDING envelopes."""
    mailbox = AgentMailbox(policy=SECURITY_POLICY)
    mailbox.submit_plan("plan-a", {"steps": []})
    mailbox.submit_plan("plan-b", {"steps": []})
    assert len(mailbox.pending_plans) == 2
    mailbox.cast_vote("security_reviewer", "plan-a", approved=True)
    assert len(mailbox.pending_plans) == 1

  def test_approval_ratio(self) -> None:
    """approval_ratio correctly tracks required agent approvals."""
    policy = ApprovalPolicy(
      required_agents=["a", "b", "c"],
      require_unanimous=True,
    )
    mailbox = AgentMailbox(policy=policy)
    mailbox.submit_plan("plan-ratio", {"steps": []})
    mailbox.cast_vote("a", "plan-ratio", approved=True)
    envelope = mailbox.get_envelope("plan-ratio")
    assert envelope.approval_ratio == pytest.approx(1 / 3)

  def test_vote_on_nonexistent_plan_raises(self) -> None:
    """Voting on non-existent plan raises KeyError."""
    mailbox = AgentMailbox()
    with pytest.raises(KeyError, match="not found"):
      mailbox.cast_vote("agent_a", "ghost-plan", approved=True)

  def test_vote_on_terminal_plan_raises(self) -> None:
    """Voting on a resolved plan raises ValueError."""
    mailbox = AgentMailbox(policy=SECURITY_POLICY)
    mailbox.submit_plan("plan-terminal", {"steps": []})
    mailbox.cast_vote("security_reviewer", "plan-terminal", approved=True)
    with pytest.raises(ValueError, match="already"):
      mailbox.cast_vote("other_agent", "plan-terminal", approved=True)


# ---------------------------------------------------------------
# Mailbox Policy Tests
# ---------------------------------------------------------------


class TestMailboxPolicies:
  """Test pre-defined mailbox policies."""

  def test_security_policy_agents(self) -> None:
    assert "security_reviewer" in SECURITY_POLICY.required_agents
    assert SECURITY_POLICY.require_unanimous is True

  def test_cost_policy_agents(self) -> None:
    assert "cost_analyst" in COST_POLICY.required_agents
    assert COST_POLICY.timeout_seconds == 90.0

  def test_architecture_board_agents(self) -> None:
    assert len(ARCHITECTURE_BOARD_POLICY.required_agents) == 3
    assert "cto_reviewer" in ARCHITECTURE_BOARD_POLICY.required_agents

  def test_full_review_factory(self) -> None:
    policy = create_full_review_policy(timeout_seconds=60.0)
    assert "security_reviewer" in policy.required_agents
    assert "cost_analyst" in policy.required_agents
    assert policy.timeout_seconds == 60.0

  def test_lightweight_factory(self) -> None:
    policy = create_lightweight_policy()
    assert len(policy.required_agents) == 1
    assert policy.timeout_seconds == 30.0

  def test_policy_catalog_completeness(self) -> None:
    assert len(POLICY_CATALOG) == 5
    assert "security" in POLICY_CATALOG
    assert "full_review" in POLICY_CATALOG

  def test_select_policy_risk_levels(self) -> None:
    low = select_policy("low")
    assert len(low.required_agents) == 1  # lightweight

    high = select_policy("high")
    assert len(high.required_agents) == 3  # full_review

    critical = select_policy("critical")
    assert len(critical.required_agents) == 3  # architecture_board

  def test_select_policy_unknown_defaults(self) -> None:
    """Unknown risk level falls back to security policy."""
    policy = select_policy("unknown")
    assert "security_reviewer" in policy.required_agents


# ---------------------------------------------------------------
# Async Consumer Tests
# ---------------------------------------------------------------


class TestAsyncConsumer:
  """Test the AsyncSuggestionConsumer."""

  @pytest.fixture
  def consumer(self) -> AsyncSuggestionConsumer:
    return AsyncSuggestionConsumer()

  def _make_entry(
    self, text: str = "test suggestion", fresh: bool = True
  ) -> SuggestionEntry:
    ts = time.time() if fresh else time.time() - 3600
    return SuggestionEntry(text=text, timestamp=ts)

  def test_publish_and_get(self, consumer: AsyncSuggestionConsumer) -> None:
    """Publish a suggestion and retrieve it."""
    entry = self._make_entry()

    async def run():
      result = await consumer.publish(entry)
      assert result is True
      got = await consumer.get_suggestion(timeout=1.0)
      assert got is not None
      assert got.text == "test suggestion"

    asyncio.run(run())

  def test_stale_entry_skipped(self, consumer: AsyncSuggestionConsumer) -> None:
    """Stale entries are skipped during get."""
    stale = self._make_entry(fresh=False)
    fresh = self._make_entry(text="fresh one")

    async def run():
      await consumer.publish(stale)
      await consumer.publish(fresh)
      got = await consumer.get_suggestion(timeout=1.0)
      assert got is not None
      assert got.text == "fresh one"

    asyncio.run(run())

  def test_empty_queue_returns_none(self, consumer: AsyncSuggestionConsumer) -> None:
    """Empty queue returns None with 0 timeout."""

    async def run():
      got = await consumer.get_suggestion(timeout=0)
      assert got is None

    asyncio.run(run())

  def test_accept_increments_counter(self, consumer: AsyncSuggestionConsumer) -> None:
    """Accepting a suggestion increments the accepted count."""
    entry = self._make_entry()

    async def run():
      await consumer.publish(entry)
      got = await consumer.get_suggestion(timeout=1.0)
      await consumer.accept(got)
      assert consumer.stats["accepted"] == 1

    asyncio.run(run())

  def test_dismiss_increments_counter(self, consumer: AsyncSuggestionConsumer) -> None:
    """Dismissing a suggestion increments the dismissed count."""
    entry = self._make_entry()

    async def run():
      await consumer.publish(entry)
      got = await consumer.get_suggestion(timeout=1.0)
      await consumer.dismiss(got)
      assert consumer.stats["dismissed"] == 1

    asyncio.run(run())

  def test_queue_overflow_drops_oldest(self, consumer: AsyncSuggestionConsumer) -> None:
    """When queue is full, oldest entry is dropped."""

    async def run():
      # Fill queue (maxsize=10) and then publish one more
      for i in range(11):
        entry = self._make_entry(text=f"suggestion-{i}")
        await consumer.publish(entry)
      assert consumer.pending_count <= 10

    asyncio.run(run())

  def test_cache_status_empty(self, consumer: AsyncSuggestionConsumer) -> None:
    """cache_status reports empty state correctly."""
    status = consumer.cache_status()
    assert status["state"] == "empty"

  def test_stats_totals(self, consumer: AsyncSuggestionConsumer) -> None:
    """Stats correctly sum accepted + dismissed."""
    entry1 = self._make_entry(text="a")
    entry2 = self._make_entry(text="b")

    async def run():
      await consumer.publish(entry1)
      await consumer.publish(entry2)
      got1 = await consumer.get_suggestion(timeout=1.0)
      got2 = await consumer.get_suggestion(timeout=1.0)
      await consumer.accept(got1)
      await consumer.dismiss(got2)
      assert consumer.stats["total_processed"] == 2

    asyncio.run(run())
