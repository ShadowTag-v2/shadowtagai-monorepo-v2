# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Security Hardening — P5.1 through P5.4 Implementation.

Consolidates all Phase 5 security items from the AGNT STATE B Spec:
  P5.1 — Fail-Closed Error Handling
  P5.2 — 50-Subcommand Security Cap
  P5.3 — Assistant Text Exclusion
  P5.4 — Context Decay Warning System

Usage:
    from packages.tool_gateway.security import SecurityHardening
    sec = SecurityHardening()
    sec.check_subcommand_count(command)
    sec.check_context_decay(current_tokens, max_tokens)
    sec.filter_classifier_input(messages)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

MAX_SUBCOMMANDS = 50
FILE_READ_LINE_CAP = 2_000
TOOL_RESULT_MAX_CHARS = 50_000
CONTEXT_WARNING_THRESHOLD_PCT = 20  # Warn when <20% remaining


@dataclass
class SecurityCheckResult:
    """Result of a security check."""

    passed: bool = True
    reason: str = ""
    warnings: list[str] = field(default_factory=list)


class SecurityHardening:
    """Consolidated security hardening checks (P5.1-P5.4)."""

    # --- P5.1: Fail-Closed Error Handling ---

    @staticmethod
    def fail_closed(func):
        """Decorator: any exception in a permission check → BLOCK.

        This ensures API errors, parse failures, schema issues,
        and timeouts all result in blocking, never permitting.
        """

        def wrapper(*args, **kwargs) -> SecurityCheckResult:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error("Fail-closed triggered in %s: %s", func.__name__, e)
                return SecurityCheckResult(passed=False, reason=f"Fail-closed: {e}")

        return wrapper

    # --- P5.2: 50-Subcommand Security Cap ---

    def check_subcommand_count(self, command: str) -> SecurityCheckResult:
        """Check if a shell command exceeds the 50-subcommand cap.

        Parses the command for pipes, semicolons, &&, ||, $(),
        backticks, and other compound operators.

        Args:
            command: Shell command string to analyze.

        Returns:
            SecurityCheckResult with pass/fail.
        """
        # Count subcommands by splitting on compound operators
        # Operators: ;, &&, ||, |, $(), ``, \n
        subcommands = re.split(r"[;\n]|\|\||&&|\|", command)

        # Also count $() and `` substitutions
        backtick_count = command.count("`") // 2
        subst_count = len(re.findall(r"\$\(", command))

        total = len([s for s in subcommands if s.strip()]) + backtick_count + subst_count

        if total > MAX_SUBCOMMANDS:
            return SecurityCheckResult(
                passed=False,
                reason=(f"Command has {total} subcommands (cap: {MAX_SUBCOMMANDS}). Break into smaller commands or get explicit approval."),
            )

        if total > MAX_SUBCOMMANDS * 0.8:
            return SecurityCheckResult(
                passed=True,
                warnings=[f"Command has {total} subcommands (approaching cap of {MAX_SUBCOMMANDS})"],
            )

        return SecurityCheckResult(passed=True)

    # --- P5.3: Assistant Text Exclusion ---

    def filter_classifier_input(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter messages for classifier input — exclude assistant prose.

        Only tool_use blocks should go to the classifier, never
        model-generated text (which could be crafted to influence decisions).

        Args:
            messages: Full conversation messages.

        Returns:
            Filtered messages containing only tool_use blocks.
        """
        filtered = []
        for msg in messages:
            if msg.get("role") == "assistant":
                # Extract only tool_use blocks, drop prose
                content = msg.get("content")
                if isinstance(content, list):
                    tool_blocks = [b for b in content if isinstance(b, dict) and b.get("type") == "tool_use"]
                    if tool_blocks:
                        filtered.append({"role": "assistant", "content": tool_blocks})
                # Skip pure text assistant messages entirely
                continue
            filtered.append(msg)
        return filtered

    # --- P5.4: Context Decay Warning System ---

    def check_context_decay(self, current_tokens: int, max_tokens: int) -> SecurityCheckResult:
        """Check for context window decay warnings.

        Warns when:
          - Context window below 20% remaining
          - Approaching critical exhaustion

        Args:
            current_tokens: Current context usage.
            max_tokens: Maximum context capacity.

        Returns:
            SecurityCheckResult with warnings if applicable.
        """
        if max_tokens <= 0:
            return SecurityCheckResult(passed=True)

        remaining_pct = ((max_tokens - current_tokens) / max_tokens) * 100
        warnings = []

        if remaining_pct < 5:
            return SecurityCheckResult(
                passed=False,
                reason=f"Context CRITICAL: {remaining_pct:.1f}% remaining ({current_tokens}/{max_tokens} tokens)",
            )

        if remaining_pct < CONTEXT_WARNING_THRESHOLD_PCT:
            warnings.append(f"Context LOW: {remaining_pct:.1f}% remaining ({current_tokens}/{max_tokens} tokens)")

        return SecurityCheckResult(passed=True, warnings=warnings)

    def check_file_read_budget(self, line_count: int) -> SecurityCheckResult:
        """Check if a file read exceeds the line budget.

        Args:
            line_count: Number of lines being read.

        Returns:
            SecurityCheckResult with warning if over budget.
        """
        if line_count > FILE_READ_LINE_CAP:
            return SecurityCheckResult(
                passed=True,
                warnings=[f"File read has {line_count} lines (budget: {FILE_READ_LINE_CAP})"],
            )
        return SecurityCheckResult(passed=True)

    def check_tool_result_size(self, result_text: str) -> SecurityCheckResult:
        """Check if a tool result exceeds the truncation limit.

        Args:
            result_text: Tool result text.

        Returns:
            SecurityCheckResult with warning if over limit.
        """
        if len(result_text) > TOOL_RESULT_MAX_CHARS:
            return SecurityCheckResult(
                passed=True,
                warnings=[f"Tool result is {len(result_text)} chars (truncation limit: {TOOL_RESULT_MAX_CHARS})"],
            )
        return SecurityCheckResult(passed=True)
