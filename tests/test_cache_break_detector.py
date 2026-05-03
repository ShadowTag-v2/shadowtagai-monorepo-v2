# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for CacheBreakDetector — P1.2 14-vector cache break detection.

Exercises both pre_scan (anchor identification) and post_verify
(mutation detection) across all critical cache-break vectors.

Reference: AGNT STATE B Spec P1.2
"""

from __future__ import annotations

import pytest

from context_compactor.cache_break_detector import (
    CacheAnchor,
    CacheBreakDetector,
    CacheBreakReport,
    CacheBreakVector,
)
from context_compactor.layers import Message


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_message(
    role: str = "user",
    content: str = "hello",
    token_count: int = 10,
    is_cache_anchor: bool = False,
) -> Message:
    """Create a Message with the minimum fields needed for tests."""
    return Message(
        role=role,
        content=content,
        token_count=token_count,
        is_cache_anchor=is_cache_anchor,
    )


def _make_conversation(n: int = 8) -> list[Message]:
    """Create a realistic conversation with system prompt + N user/assistant turns."""
    msgs = [
        _make_message(role="system", content="You are a helpful assistant.", token_count=50),
    ]
    for i in range(1, n):
        if i % 2 == 1:
            msgs.append(_make_message(role="user", content=f"User message {i}", token_count=20))
        else:
            msgs.append(_make_message(role="assistant", content=f"Assistant response {i}", token_count=30))
    return msgs


# ── Pre-Scan Tests ───────────────────────────────────────────────────────────


class TestPreScan:
    """Phase 1: Verify anchor identification logic."""

    def test_system_messages_always_anchored(self) -> None:
        """System prompts must always be identified as cache anchors."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(3)
        anchors = detector.pre_scan(msgs)

        system_anchors = [a for a in anchors if a.is_system]
        assert len(system_anchors) == 1
        assert system_anchors[0].role == "system"
        assert system_anchors[0].index == 0

    def test_prefix_region_anchored(self) -> None:
        """First 5 messages are heuristically in the cache prefix."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(10)
        anchors = detector.pre_scan(msgs)

        prefix_indices = {a.index for a in anchors}
        for i in range(5):
            assert i in prefix_indices, f"Message at index {i} should be in prefix"

    def test_explicit_anchor_flag(self) -> None:
        """Messages with is_cache_anchor=True should be anchored regardless of position."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(10)
        # Mark message 7 (outside prefix) as explicit anchor
        msgs[7] = _make_message(
            role="assistant",
            content="Important response",
            token_count=30,
            is_cache_anchor=True,
        )

        anchors = detector.pre_scan(msgs)
        anchor_indices = {a.index for a in anchors}
        assert 7 in anchor_indices

    def test_empty_conversation(self) -> None:
        """Empty message list should return no anchors."""
        detector = CacheBreakDetector()
        anchors = detector.pre_scan([])
        assert anchors == []

    def test_single_system_message(self) -> None:
        """Single system message should produce 1 anchor."""
        detector = CacheBreakDetector()
        msgs = [_make_message(role="system", content="sys")]
        anchors = detector.pre_scan(msgs)
        assert len(anchors) == 1

    def test_content_hash_deterministic(self) -> None:
        """Same content must produce same hash across multiple scans."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(3)
        anchors1 = detector.pre_scan(msgs)
        anchors2 = detector.pre_scan(msgs)

        for a1, a2 in zip(anchors1, anchors2, strict=True):
            assert a1.content_hash == a2.content_hash


# ── Post-Verify Tests ────────────────────────────────────────────────────────


class TestPostVerify:
    """Phase 2: Verify cache break detection after mutation."""

    def test_no_change_preserves_cache(self) -> None:
        """If messages are unchanged, cache should be preserved."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(6)
        anchors = detector.pre_scan(msgs)
        report = detector.post_verify(msgs, anchors)

        assert not report.cache_broken
        assert report.vectors_triggered == []
        assert report.survival_rate == 100.0

    def test_system_prompt_change_detected(self) -> None:
        """Modifying the system prompt triggers SYSTEM_PROMPT_CHANGE."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(6)
        anchors = detector.pre_scan(msgs)

        # Mutate system prompt
        msgs[0] = _make_message(role="system", content="MODIFIED system prompt", token_count=50)

        report = detector.post_verify(msgs, anchors)
        assert report.cache_broken
        assert CacheBreakVector.SYSTEM_PROMPT_CHANGE in report.vectors_triggered
        assert report.break_position == 0

    def test_message_deletion_detected(self) -> None:
        """Removing messages triggers MESSAGE_DELETION."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(8)
        anchors = detector.pre_scan(msgs)

        # Delete last 4 messages (some anchored)
        msgs_after = msgs[:4]

        report = detector.post_verify(msgs_after, anchors)
        assert report.cache_broken
        assert CacheBreakVector.MESSAGE_DELETION in report.vectors_triggered

    def test_content_edit_detected(self) -> None:
        """Editing anchored message content triggers MESSAGE_CONTENT_EDIT."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(6)
        anchors = detector.pre_scan(msgs)

        # Modify a non-system anchored message (in prefix)
        msgs[1] = _make_message(role="user", content="EDITED user message", token_count=20)

        report = detector.post_verify(msgs, anchors)
        assert report.cache_broken
        assert CacheBreakVector.MESSAGE_CONTENT_EDIT in report.vectors_triggered

    def test_role_change_detected(self) -> None:
        """Changing a message's role triggers ROLE_CHANGE."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(6)
        anchors = detector.pre_scan(msgs)

        # Change role of message 1 from user to assistant (but keep content same hash)
        original_content = msgs[1].content
        msgs[1] = _make_message(role="assistant", content=original_content, token_count=20)

        report = detector.post_verify(msgs, anchors)
        assert report.cache_broken
        assert CacheBreakVector.ROLE_CHANGE in report.vectors_triggered

    def test_tool_result_modification_detected(self) -> None:
        """Modifying a tool message triggers TOOL_RESULT_MODIFICATION."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(6)
        # Replace message 2 with a tool message
        msgs[2] = _make_message(role="tool", content="tool output v1", token_count=15)
        anchors = detector.pre_scan(msgs)

        # Modify the tool message
        msgs[2] = _make_message(role="tool", content="tool output v2 MODIFIED", token_count=15)

        report = detector.post_verify(msgs, anchors)
        assert report.cache_broken
        assert CacheBreakVector.TOOL_RESULT_MODIFICATION in report.vectors_triggered

    def test_api_params_change_detected(self) -> None:
        """api_params_changed=True triggers TEMPERATURE_CHANGE."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(3)
        anchors = detector.pre_scan(msgs)

        report = detector.post_verify(msgs, anchors, api_params_changed=True)
        assert report.cache_broken
        assert CacheBreakVector.TEMPERATURE_CHANGE in report.vectors_triggered

    def test_survival_rate_calculation(self) -> None:
        """Survival rate correctly reflects surviving/total anchors."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(6)
        anchors = detector.pre_scan(msgs)
        total = len(anchors)

        # Modify first anchored non-system message
        msgs[1] = _make_message(role="user", content="CHANGED", token_count=20)

        report = detector.post_verify(msgs, anchors)
        assert report.anchors_total == total
        assert report.anchors_surviving == total - 1
        expected_rate = round(((total - 1) / total) * 100, 2)
        assert report.survival_rate == expected_rate

    def test_break_position_first_divergence(self) -> None:
        """break_position should report the FIRST divergent anchor index."""
        detector = CacheBreakDetector()
        msgs = _make_conversation(6)
        anchors = detector.pre_scan(msgs)

        # Modify messages at indices 2 and 3
        msgs[2] = _make_message(role="assistant", content="CHANGED-2", token_count=30)
        msgs[3] = _make_message(role="user", content="CHANGED-3", token_count=20)

        report = detector.post_verify(msgs, anchors)
        assert report.break_position == 2


# ── CacheAnchor Tests ────────────────────────────────────────────────────────


class TestCacheAnchor:
    """Test the frozen CacheAnchor dataclass."""

    def test_frozen_immutability(self) -> None:
        """CacheAnchor is frozen — attributes cannot be mutated."""
        anchor = CacheAnchor(
            index=0,
            content_hash="abc123",
            role="system",
            is_system=True,
            token_count=50,
        )
        with pytest.raises(AttributeError):
            anchor.index = 1  # type: ignore[misc]

    def test_equality(self) -> None:
        """Two anchors with same fields are equal."""
        a = CacheAnchor(index=0, content_hash="abc", role="system", is_system=True, token_count=50)
        b = CacheAnchor(index=0, content_hash="abc", role="system", is_system=True, token_count=50)
        assert a == b


# ── CacheBreakReport Tests ───────────────────────────────────────────────────


class TestCacheBreakReport:
    """Test the CacheBreakReport value calculations."""

    def test_default_not_broken(self) -> None:
        """Default report should not indicate cache break."""
        report = CacheBreakReport()
        assert not report.cache_broken
        assert report.survival_rate == 100.0

    def test_zero_anchors_100_survival(self) -> None:
        """Zero anchors total should report 100% survival (edge case)."""
        report = CacheBreakReport(anchors_total=0, anchors_surviving=0)
        assert report.survival_rate == 100.0


# ── API Params Hashing ───────────────────────────────────────────────────────


class TestApiParamsHashing:
    """Test the set_api_params hashing mechanism."""

    def test_different_models_different_hashes(self) -> None:
        """Different model names should produce different param hashes."""
        d = CacheBreakDetector()
        d.set_api_params(model="gemini-3.1-flash")
        hash1 = d._api_params_hash

        d.set_api_params(model="gemini-3.1-pro")
        hash2 = d._api_params_hash

        assert hash1 != hash2

    def test_same_params_same_hash(self) -> None:
        """Identical params should produce identical hashes."""
        d = CacheBreakDetector()
        d.set_api_params(model="gemini-3.1-flash", temperature=0.7, max_tokens=1024)
        hash1 = d._api_params_hash

        d.set_api_params(model="gemini-3.1-flash", temperature=0.7, max_tokens=1024)
        hash2 = d._api_params_hash

        assert hash1 == hash2


# ── Integration: Compactor + CacheBreakDetector ──────────────────────────────


class TestCompactorCacheIntegration:
    """Test the wired integration in ContextCompactor."""

    def test_compactor_has_cache_detector(self) -> None:
        """ContextCompactor should expose a cache_detector property."""
        from context_compactor.compactor import ContextCompactor

        compactor = ContextCompactor(feature_flags={"context_compaction": True})
        assert isinstance(compactor.cache_detector, CacheBreakDetector)

    def test_compactor_run_populates_cache_report(self) -> None:
        """After run(), last_cache_report should be populated."""
        from context_compactor.compactor import ContextCompactor

        compactor = ContextCompactor(feature_flags={"context_compaction": True})
        msgs = _make_conversation(6)

        compactor.run(msgs, target_tokens=1000, current_tokens=2000, max_layer=1)

        assert compactor.last_cache_report is not None
        assert isinstance(compactor.last_cache_report, CacheBreakReport)

    def test_compactor_disabled_skips_cache_detection(self) -> None:
        """When compaction is disabled, no cache report should be generated."""
        from context_compactor.compactor import ContextCompactor

        compactor = ContextCompactor(feature_flags={"context_compaction": False})
        msgs = _make_conversation(3)

        result = compactor.run(msgs, target_tokens=1000, current_tokens=2000)

        assert result.layer_used == "disabled"
        assert compactor.last_cache_report is None

    def test_stats_includes_cache_preservation(self) -> None:
        """Stats dict should include last_cache_preserved key."""
        from context_compactor.compactor import ContextCompactor

        compactor = ContextCompactor(feature_flags={"context_compaction": True})
        msgs = _make_conversation(6)

        compactor.run(msgs, target_tokens=1000, current_tokens=2000, max_layer=1)

        stats = compactor.stats
        assert "last_cache_preserved" in stats
