# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge 6 — Chain Depth Limiter (Risk #34 Mitigation).

Implements the Adversa AI 50-subcommand bypass defense:
  - Tracks sequential BashTool/command invocations per session
  - Auto-ESCALATES to STATE B when chain depth exceeds threshold
  - Detects encoding evasion (base64, hex, octal) in command chains
  - Implements progressive throttling at depth milestones

Reference: Risk #34 in RISK_REGISTER.md
           Adversa AI paper: 50-subcommand bypass attack
           CC Leaks feature: bash_max_concurrent_commands = 5

Thresholds (C1–C5):
  C1: depth > 5  → log warning
  C2: depth > 10 → auto-ESCALATE to STATE B
  C3: depth > 20 → require human approval
  C4: depth > 35 → hard block, session pause
  C5: depth > 50 → kill chain, alert
"""

from __future__ import annotations

import base64
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

THRESHOLD_C1_WARN = 5
THRESHOLD_C2_ESCALATE = 10
THRESHOLD_C3_HUMAN = 20
THRESHOLD_C4_BLOCK = 35
THRESHOLD_C5_KILL = 50

# Encoding patterns that indicate evasion attempts
ENCODING_PATTERNS = frozenset(
    {
        r"base64\s+(-d|--decode)",  # base64 decode
        r"echo\s+[\w+/=]{20,}\s*\|\s*base64",  # piped base64
        r"\\x[0-9a-fA-F]{2}",  # hex escape
        r"\\[0-7]{3}",  # octal escape
        r"\$\(\s*printf",  # printf-based encoding
        r"xxd\s+-r",  # hex reverse
        r"python[23]?\s+-c\s+['\"].*(?:decode|b64|chr)",  # python inline decode
        r"perl\s+-e\s+['\"].*(?:decode|pack|chr)",  # perl inline decode
        r"ruby\s+-e\s+['\"].*(?:decode|Base64|chr)",  # ruby inline decode
    }
)


class EscalationLevel(Enum):
    """Chain depth escalation levels."""

    NORMAL = "NORMAL"
    WARN = "WARN"  # C1
    ESCALATE = "ESCALATE"  # C2 — STATE B
    HUMAN_REQUIRED = "HUMAN_REQUIRED"  # C3
    BLOCKED = "BLOCKED"  # C4
    KILLED = "KILLED"  # C5


@dataclass
class ChainState:
    """Tracks the state of a command chain within a session."""

    session_id: str = ""
    depth: int = 0
    encoding_detections: int = 0
    escalation_level: EscalationLevel = EscalationLevel.NORMAL
    commands: list[str] = field(default_factory=list)
    timestamps: list[float] = field(default_factory=list)
    last_reset: float = field(default_factory=time.time)

    @property
    def commands_per_minute(self) -> float:
        """Calculate command velocity for burst detection."""
        if len(self.timestamps) < 2:
            return 0.0
        elapsed = self.timestamps[-1] - self.timestamps[0]
        if elapsed <= 0:
            return float(len(self.timestamps))
        return len(self.timestamps) / (elapsed / 60.0)


class ChainDepthLimiter:
    """Judge 6: Sequential command chain depth limiter.

    Tracks consecutive BashTool/command invocations and enforces
    progressive throttling to prevent the Adversa AI 50-subcommand
    bypass attack.

    Usage:
        limiter = ChainDepthLimiter()
        verdict = limiter.check("rm -rf /tmp/test")
        if verdict.escalation_level == EscalationLevel.BLOCKED:
            raise SecurityError("Chain depth exceeded")
    """

    def __init__(
        self,
        *,
        session_id: str = "",
        warn_threshold: int = THRESHOLD_C1_WARN,
        escalate_threshold: int = THRESHOLD_C2_ESCALATE,
        human_threshold: int = THRESHOLD_C3_HUMAN,
        block_threshold: int = THRESHOLD_C4_BLOCK,
        kill_threshold: int = THRESHOLD_C5_KILL,
    ) -> None:
        self._state = ChainState(session_id=session_id)
        self._warn = warn_threshold
        self._escalate = escalate_threshold
        self._human = human_threshold
        self._block = block_threshold
        self._kill = kill_threshold
        self._compiled_patterns = [re.compile(p) for p in ENCODING_PATTERNS]

    @property
    def state(self) -> ChainState:
        """Read-only access to current chain state."""
        return self._state

    def reset(self) -> None:
        """Reset chain tracking (e.g., on non-command tool call)."""
        self._state = ChainState(
            session_id=self._state.session_id,
            last_reset=time.time(),
        )

    def check(self, command: str) -> ChainState:
        """Evaluate a command and update chain depth.

        Returns the updated ChainState with the current escalation level.
        """
        now = time.time()
        self._state.depth += 1
        self._state.commands.append(command[:200])  # Truncate for memory
        self._state.timestamps.append(now)

        # Detect encoding evasion
        if self._detect_encoding(command):
            self._state.encoding_detections += 1
            logger.warning(
                "Encoding evasion detected in command chain (depth=%d, detections=%d): %s",
                self._state.depth,
                self._state.encoding_detections,
                command[:100],
            )

        # Evaluate escalation level
        self._state.escalation_level = self._evaluate_level()

        # Log at appropriate level
        self._log_escalation(command)

        return self._state

    def _detect_encoding(self, command: str) -> bool:
        """Check for encoding-based evasion patterns."""
        for pattern in self._compiled_patterns:
            if pattern.search(command):
                return True

        # Check for suspiciously long base64-like strings
        b64_candidates = re.findall(r"[A-Za-z0-9+/=]{40,}", command)
        for candidate in b64_candidates:
            try:
                decoded = base64.b64decode(candidate, validate=True)
                # If it decodes to valid ASCII, it's suspicious
                if decoded.isascii() and len(decoded) > 10:
                    return True
            except Exception:
                continue

        return False

    def _evaluate_level(self) -> EscalationLevel:
        """Determine escalation level based on depth and encoding detections."""
        depth = self._state.depth
        encoding_bonus = self._state.encoding_detections * 5  # Each encoding detection = +5 depth

        effective_depth = depth + encoding_bonus

        if effective_depth >= self._kill:
            return EscalationLevel.KILLED
        if effective_depth >= self._block:
            return EscalationLevel.BLOCKED
        if effective_depth >= self._human:
            return EscalationLevel.HUMAN_REQUIRED
        if effective_depth >= self._escalate:
            return EscalationLevel.ESCALATE
        if effective_depth >= self._warn:
            return EscalationLevel.WARN
        return EscalationLevel.NORMAL

    def _log_escalation(self, command: str) -> None:
        """Log based on current escalation level."""
        level = self._state.escalation_level
        depth = self._state.depth
        cmd_preview = command[:80]

        match level:
            case EscalationLevel.NORMAL:
                logger.debug("Chain depth %d: %s", depth, cmd_preview)
            case EscalationLevel.WARN:
                logger.warning(
                    "[C1] Chain depth %d exceeds warning threshold. Command: %s",
                    depth,
                    cmd_preview,
                )
            case EscalationLevel.ESCALATE:
                logger.warning(
                    "[C2] Chain depth %d — AUTO-ESCALATING to STATE B. Clutch engaged. Command: %s",
                    depth,
                    cmd_preview,
                )
            case EscalationLevel.HUMAN_REQUIRED:
                logger.error(
                    "[C3] Chain depth %d — HUMAN APPROVAL REQUIRED. Command chain paused. Command: %s",
                    depth,
                    cmd_preview,
                )
            case EscalationLevel.BLOCKED:
                logger.critical(
                    "[C4] Chain depth %d — HARD BLOCK. Session paused. Command: %s",
                    depth,
                    cmd_preview,
                )
            case EscalationLevel.KILLED:
                logger.critical(
                    "[C5] Chain depth %d — KILL CHAIN. Alerting. Command: %s",
                    depth,
                    cmd_preview,
                )

    def summary(self) -> dict:
        """Return diagnostic summary of current chain state."""
        return {
            "session_id": self._state.session_id,
            "depth": self._state.depth,
            "encoding_detections": self._state.encoding_detections,
            "escalation_level": self._state.escalation_level.value,
            "commands_per_minute": round(self._state.commands_per_minute, 2),
            "command_count": len(self._state.commands),
            "last_reset": self._state.last_reset,
        }


__all__ = [
    "ChainDepthLimiter",
    "ChainState",
    "EscalationLevel",
    "THRESHOLD_C1_WARN",
    "THRESHOLD_C2_ESCALATE",
    "THRESHOLD_C3_HUMAN",
    "THRESHOLD_C4_BLOCK",
    "THRESHOLD_C5_KILL",
]
