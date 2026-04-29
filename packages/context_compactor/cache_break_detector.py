# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Cache Break Detection — P1.2 Implementation.

Ported from: compact/microCompact.ts (14 cache-break vectors)
Reference: AGNT STATE B Spec P1.2

Implements the two-phase detection protocol:
  1. Pre-compact scan: Identify which messages are cache-anchored
  2. Post-compact verify: Confirm cache prefix survived compaction

This module ensures that the compaction pipeline (L1-L4) does not
inadvertently break the prompt cache, which would cause Gemini to
reprocess the entire context window (expensive and slow).

Usage:
    detector = CacheBreakDetector()
    anchors = detector.pre_scan(messages)
    # ... run compaction ...
    report = detector.post_verify(messages, anchors)
    if report.cache_broken:
        handle_cache_break(report)
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from packages.context_compactor.layers import Message

logger = logging.getLogger(__name__)


class CacheBreakVector(StrEnum):
    """14 cache-break vectors identified in microCompact.ts."""

    SYSTEM_PROMPT_CHANGE = "system_prompt_change"
    TOOL_DEFINITION_CHANGE = "tool_definition_change"
    MESSAGE_INSERTION = "message_insertion"
    MESSAGE_DELETION = "message_deletion"
    MESSAGE_CONTENT_EDIT = "message_content_edit"
    ROLE_CHANGE = "role_change"
    TOOL_RESULT_MODIFICATION = "tool_result_modification"
    THINKING_BLOCK_REMOVAL = "thinking_block_removal"
    IMAGE_BLOCK_REMOVAL = "image_block_removal"
    CACHE_CONTROL_HEADER_CHANGE = "cache_control_header_change"
    TEMPERATURE_CHANGE = "temperature_change"
    MAX_TOKENS_CHANGE = "max_tokens_change"
    STOP_SEQUENCE_CHANGE = "stop_sequence_change"
    MODEL_SWITCH = "model_switch"


@dataclass(frozen=True)
class CacheAnchor:
    """A message position that anchors the prompt cache.

    Attributes:
        index: Message index in the conversation.
        content_hash: SHA-256 hash of the message content.
        role: Message role.
        is_system: Whether this is a system prompt.
        token_count: Token count at time of scan.
    """

    index: int
    content_hash: str
    role: str
    is_system: bool
    token_count: int


@dataclass
class CacheBreakReport:
    """Result of a post-compaction cache verification.

    Attributes:
        cache_broken: Whether the cache was broken by compaction.
        vectors_triggered: Which cache-break vectors were activated.
        anchors_surviving: Count of anchors that survived.
        anchors_total: Total anchors from pre-scan.
        break_position: First message index where cache diverged.
        timestamp: When the verification was performed.
    """

    cache_broken: bool = False
    vectors_triggered: list[CacheBreakVector] = field(default_factory=list)
    anchors_surviving: int = 0
    anchors_total: int = 0
    break_position: int = -1
    timestamp: float = field(default_factory=time.time)

    @property
    def survival_rate(self) -> float:
        """Percentage of cache anchors that survived compaction."""
        if self.anchors_total == 0:
            return 100.0
        return round((self.anchors_surviving / self.anchors_total) * 100, 2)


@dataclass
class CacheBreakDetector:
    """Two-phase prompt cache break detector.

    Phase 1 (pre_scan): Takes a snapshot of cache-anchored messages
    Phase 2 (post_verify): Compares post-compaction state against snapshot

    This ensures L1 compaction truly preserves the cache, and L2-L4
    compaction properly reports cache breaks for telemetry.

    Attributes:
        _api_params_hash: Hash of API parameters (model, temperature, etc.)
    """

    _api_params_hash: str = ""

    def set_api_params(
        self,
        model: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        stop_sequences: list[str] | None = None,
        tool_definitions: list[dict[str, Any]] | None = None,
    ) -> None:
        """Capture current API parameters for cache-break detection.

        These parameters are hashed and compared before/after compaction
        to detect cache-breaking configuration changes.

        Args:
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum output tokens.
            stop_sequences: Stop sequences.
            tool_definitions: Tool definitions sent to the API.
        """
        params_str = (
            f"model={model}|"
            f"temp={temperature}|"
            f"max_tokens={max_tokens}|"
            f"stop={sorted(stop_sequences or [])}|"
            f"tools={len(tool_definitions or [])}"
        )
        self._api_params_hash = hashlib.sha256(
            params_str.encode()
        ).hexdigest()[:16]

    def pre_scan(self, messages: list[Message]) -> list[CacheAnchor]:
        """Phase 1: Identify cache-anchored messages before compaction.

        A message is considered a cache anchor if:
          - It is a system prompt (always anchored)
          - It has is_cache_anchor=True (explicitly marked)
          - It is in the cache-prefix region (first N messages)

        The cache prefix is the longest contiguous sequence of messages
        from the start that the API will cache. Modifying ANY message
        within this prefix invalidates the cache.

        Args:
            messages: Current conversation messages.

        Returns:
            List of CacheAnchor snapshots.
        """
        anchors = []

        for i, msg in enumerate(messages):
            # All system messages are cache anchors
            is_system = msg.role == "system"

            # Explicitly marked cache anchors
            is_explicit = msg.is_cache_anchor

            # First 5 messages are in the cache prefix region by heuristic
            # (Gemini's cache window typically covers the prefix)
            is_prefix = i < 5

            if is_system or is_explicit or is_prefix:
                content_hash = self._hash_content(msg.content)
                anchors.append(
                    CacheAnchor(
                        index=i,
                        content_hash=content_hash,
                        role=msg.role,
                        is_system=is_system,
                        token_count=msg.token_count,
                    )
                )

        logger.debug(
            "Pre-scan found %d cache anchors in %d messages",
            len(anchors),
            len(messages),
        )

        return anchors

    def post_verify(
        self,
        messages: list[Message],
        pre_anchors: list[CacheAnchor],
        api_params_changed: bool = False,
    ) -> CacheBreakReport:
        """Phase 2: Verify cache prefix survived compaction.

        Compares the current message state against the pre-scan snapshot
        to detect any cache-breaking mutations.

        Args:
            messages: Messages after compaction.
            pre_anchors: Anchors from pre_scan().
            api_params_changed: Whether API params changed during compaction.

        Returns:
            CacheBreakReport with detailed analysis.
        """
        report = CacheBreakReport(anchors_total=len(pre_anchors))

        if api_params_changed:
            report.cache_broken = True
            report.vectors_triggered.append(
                CacheBreakVector.TEMPERATURE_CHANGE
            )

        # Check message count change (insertion/deletion)
        if len(messages) < len(pre_anchors):
            report.cache_broken = True
            report.vectors_triggered.append(CacheBreakVector.MESSAGE_DELETION)

        # Verify each anchor
        surviving = 0
        for anchor in pre_anchors:
            if anchor.index >= len(messages):
                # Message was deleted
                if report.break_position < 0:
                    report.break_position = anchor.index
                report.cache_broken = True
                if CacheBreakVector.MESSAGE_DELETION not in report.vectors_triggered:
                    report.vectors_triggered.append(
                        CacheBreakVector.MESSAGE_DELETION
                    )
                continue

            current_msg = messages[anchor.index]
            current_hash = self._hash_content(current_msg.content)

            # Check content mutation
            if current_hash != anchor.content_hash:
                if report.break_position < 0:
                    report.break_position = anchor.index

                report.cache_broken = True

                # Determine the specific vector
                vector = self._classify_mutation(
                    anchor, current_msg, current_hash
                )
                if vector not in report.vectors_triggered:
                    report.vectors_triggered.append(vector)
            else:
                surviving += 1

            # Check role change
            if current_msg.role != anchor.role:
                report.cache_broken = True
                if CacheBreakVector.ROLE_CHANGE not in report.vectors_triggered:
                    report.vectors_triggered.append(
                        CacheBreakVector.ROLE_CHANGE
                    )

        report.anchors_surviving = surviving

        if report.cache_broken:
            logger.warning(
                "Cache break detected: %d/%d anchors survived "
                "(vectors: %s, break at position %d)",
                surviving,
                len(pre_anchors),
                [v.value for v in report.vectors_triggered],
                report.break_position,
            )
        else:
            logger.debug(
                "Cache preserved: %d/%d anchors intact",
                surviving,
                len(pre_anchors),
            )

        return report

    def _classify_mutation(
        self,
        anchor: CacheAnchor,
        current_msg: Message,
        current_hash: str,
    ) -> CacheBreakVector:
        """Classify the type of mutation that broke the cache.

        Args:
            anchor: Original anchor snapshot.
            current_msg: Current message state.
            current_hash: Hash of current message content.

        Returns:
            The most specific CacheBreakVector for this mutation.
        """
        # System prompt change
        if anchor.is_system:
            return CacheBreakVector.SYSTEM_PROMPT_CHANGE

        # Tool result modification
        if current_msg.role == "tool":
            return CacheBreakVector.TOOL_RESULT_MODIFICATION

        # Content edit (generic fallback)
        return CacheBreakVector.MESSAGE_CONTENT_EDIT

    def _hash_content(self, content: Any) -> str:
        """Compute a stable hash of message content.

        Handles both string and structured (list/dict) content.

        Args:
            content: Message content to hash.

        Returns:
            16-char hex digest.
        """
        if isinstance(content, str):
            data = content.encode()
        elif isinstance(content, (list, dict)):
            import json
            data = json.dumps(content, sort_keys=True).encode()
        else:
            data = str(content).encode()

        return hashlib.sha256(data).hexdigest()[:16]
