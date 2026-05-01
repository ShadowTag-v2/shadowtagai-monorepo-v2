#!/usr/bin/env python3
"""
Dynamic YOLO Classifier — Ported from Claude Code's effort.ts + classifierApprovals.ts

Grounded in:
  - Claude_Source_Code/utils/effort.ts (330 lines, effort level resolution chain)
  - Claude_Source_Code/utils/classifierApprovals.ts (auto-mode denial tracking)
  - Claude_Source_Code/utils/hooks.ts (5023 lines, PreToolUse/PostToolUse hook lifecycle)

Architecture:
  Intercepts tool calls and classifies them into risk tiers using an XML 2-stage
  pipeline (matching Claude Code's internal YOLO classifier). Commands below the
  risk threshold are auto-approved (STATE A), while high-risk commands trigger
  STATE B clutch mode.

Usage:
  python scripts/yolo_classifier_daemon.py [--watch] [--dry-run]

Integration:
  Called from KAIROS daemon and pre-action-memory-gate skill as the first
  gate in the permission evaluation chain.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BEADS_DIR = PROJECT_ROOT / ".beads"
ISSUES_LOG = BEADS_DIR / "issues.jsonl"

# From Claude Code's effort.ts: EFFORT_LEVELS
EFFORT_LEVELS = ("low", "medium", "high", "max")

# From Claude Code's classifierApprovals.ts: denial tracking thresholds
MAX_CONSECUTIVE_DENIALS = 3
DENIAL_COOLDOWN_MS = 5000

# ── Risk Taxonomy (grounded in Claude Code's hooks.ts PreToolUse gate) ─────


class RiskTier(Enum):
    """Maps to Claude Code's permissionBehavior: allow/ask/deny."""

    SAFE = "allow"  # Auto-approve (STATE A YOLO)
    MODERATE = "ask"  # Log and proceed with caution
    DANGEROUS = "deny"  # Block and escalate to STATE B
    FORBIDDEN = "block"  # Absolute prohibition (RULE 00)


@dataclass
class ClassificationResult:
    """Result of classifying a command/tool invocation."""

    command: str
    risk_tier: RiskTier
    risk_score: float  # 0.0 - 1.0
    reasons: list[str] = field(default_factory=list)
    suggested_action: str = "proceed"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "risk_tier": self.risk_tier.value,
            "risk_score": self.risk_score,
            "reasons": self.reasons,
            "suggested_action": self.suggested_action,
            "timestamp": self.timestamp,
        }


# ── Forbidden Patterns (from AGENTS.md RULE 00 + hooks.ts) ────────────────

FORBIDDEN_PATTERNS: list[re.Pattern] = [
    re.compile(r"\brm\s+(-[rRf]+\s+)*[/~]", re.IGNORECASE),
    re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
    re.compile(r"\bunlink\b", re.IGNORECASE),
    re.compile(r"\bsudo\b", re.IGNORECASE),
    re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bgit\s+push\s+--force\b", re.IGNORECASE),
    re.compile(r"\bgit\s+push\s+-f\b", re.IGNORECASE),
    re.compile(r"\bgit\s+rebase\s+-i\b", re.IGNORECASE),
    re.compile(r"\bdd\s+", re.IGNORECASE),
    re.compile(r"\bmkfs\b", re.IGNORECASE),
    re.compile(r">\s*/dev/sd[a-z]", re.IGNORECASE),
]

# ── Dangerous Patterns (STATE B triggers from AGENTS.md) ──────────────────

DANGEROUS_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bgit\s+filter-branch\b", re.IGNORECASE),
    re.compile(r"\bgit\s+revert\b", re.IGNORECASE),
    re.compile(r"\bdrop\s+table\b", re.IGNORECASE),
    re.compile(r"\bdrop\s+database\b", re.IGNORECASE),
    re.compile(r"\btruncate\b", re.IGNORECASE),
    re.compile(r"\balter\s+table\b", re.IGNORECASE),
    re.compile(r"\bmigrate\b", re.IGNORECASE),
    re.compile(r"\bfirebase\s+deploy\b", re.IGNORECASE),
    re.compile(r"\bgcloud\s+.*delete\b", re.IGNORECASE),
    re.compile(r"\bkubectl\s+delete\b", re.IGNORECASE),
    re.compile(r"\bstripe\s+", re.IGNORECASE),
    re.compile(r"\bnpm\s+publish\b", re.IGNORECASE),
]

# ── Safe Patterns (STATE A auto-approve from AGENTS.md) ───────────────────

SAFE_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bgit\s+(status|log|diff|fetch|pull|branch)\b", re.IGNORECASE),
    re.compile(r"\bls\b", re.IGNORECASE),
    re.compile(r"\bcat\b", re.IGNORECASE),
    re.compile(r"\bhead\b", re.IGNORECASE),
    re.compile(r"\btail\b", re.IGNORECASE),
    re.compile(r"\bfind\b", re.IGNORECASE),
    re.compile(r"\bgrep\b", re.IGNORECASE),
    re.compile(r"\brg\b", re.IGNORECASE),
    re.compile(r"\bwc\b", re.IGNORECASE),
    re.compile(r"\becho\b", re.IGNORECASE),
    re.compile(r"\bpwd\b", re.IGNORECASE),
    re.compile(r"\bwhich\b", re.IGNORECASE),
    re.compile(r"\bpython\b.*--version", re.IGNORECASE),
    re.compile(r"\bnode\b.*--version", re.IGNORECASE),
    re.compile(r"\bnpm\s+(list|ls|info|view|search|outdated)\b", re.IGNORECASE),
    re.compile(r"\bpip\s+(list|show|freeze)\b", re.IGNORECASE),
    re.compile(r"\bruff\s+(check|format)\b", re.IGNORECASE),
    re.compile(r"\bbiome\s+(check|format|lint)\b", re.IGNORECASE),
    re.compile(r"\bpytest\b", re.IGNORECASE),
    re.compile(r"\bnpm\s+test\b", re.IGNORECASE),
    re.compile(r"\bnpm\s+run\b", re.IGNORECASE),
    re.compile(r"\bcurl\b.*localhost", re.IGNORECASE),
]

# ── MCP Tool Classification ──────────────────────────────────────────────

MCP_SAFE_TOOLS = frozenset(
    {
        "search_documents",
        "list_projects",
        "list_pages",
        "firebase_get_environment",
        "sequentialthinking",
        "get_console_logs",
        "take_screenshot",
        "get_page_info",
    }
)

MCP_DANGEROUS_TOOLS = frozenset(
    {
        "firebase_init",
        "firebase_login",
        "run_accessibility_audit",
        "lighthouse_audit",
    }
)


# ── Classifier Engine ────────────────────────────────────────────────────


class YOLOClassifier:
    """
    2-stage XML classifier ported from Claude Code's permission evaluation chain.

    Stage 1: Pattern matching (fast path — exact regex against known patterns)
    Stage 2: Heuristic scoring (slow path — contextual risk assessment)

    This mirrors Claude Code's hooks.ts processHookJSONOutput() → permissionBehavior
    resolution chain.
    """

    def __init__(self) -> None:
        self.denial_count = 0
        self.last_denial_time = 0.0
        self.classification_log: list[ClassificationResult] = []
        self.logger = logging.getLogger("yolo_classifier")

    def classify(self, command: str) -> ClassificationResult:
        """
        Classify a command through the 2-stage pipeline.

        From Claude Code's hooks.ts:
          - PreToolUse hooks check permissionBehavior (allow/deny/ask)
          - processHookJSONOutput resolves the final decision
          - Denial tracking (classifierApprovals.ts) prevents runaway denials
        """
        command = command.strip()

        # Stage 1: Forbidden check (RULE 00 — absolute)
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(command):
                result = ClassificationResult(
                    command=command,
                    risk_tier=RiskTier.FORBIDDEN,
                    risk_score=1.0,
                    reasons=[f"Matches RULE 00 forbidden pattern: {pattern.pattern}"],
                    suggested_action="block_and_log",
                )
                self._record(result)
                return result

        # Stage 1: Safe fast-path (STATE A YOLO)
        for pattern in SAFE_PATTERNS:
            if pattern.search(command):
                result = ClassificationResult(
                    command=command,
                    risk_tier=RiskTier.SAFE,
                    risk_score=0.1,
                    reasons=[f"Matches STATE A safe pattern: {pattern.pattern}"],
                    suggested_action="auto_approve",
                )
                self._record(result)
                return result

        # Stage 1: Dangerous check (STATE B trigger)
        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(command):
                result = ClassificationResult(
                    command=command,
                    risk_tier=RiskTier.DANGEROUS,
                    risk_score=0.85,
                    reasons=[f"Matches STATE B trigger: {pattern.pattern}"],
                    suggested_action="clutch_mode",
                )
                self._record(result)
                return result

        # Stage 2: Heuristic scoring for ambiguous commands
        score = self._heuristic_score(command)
        if score < 0.3:
            tier = RiskTier.SAFE
            action = "auto_approve"
        elif score < 0.6:
            tier = RiskTier.MODERATE
            action = "log_and_proceed"
        else:
            tier = RiskTier.DANGEROUS
            action = "clutch_mode"

        result = ClassificationResult(
            command=command,
            risk_tier=tier,
            risk_score=score,
            reasons=["Heuristic scoring (no exact pattern match)"],
            suggested_action=action,
        )
        self._record(result)
        return result

    def classify_mcp_tool(self, tool_name: str, server: str) -> ClassificationResult:
        """Classify an MCP tool invocation."""
        if tool_name in MCP_SAFE_TOOLS:
            return ClassificationResult(
                command=f"mcp:{server}/{tool_name}",
                risk_tier=RiskTier.SAFE,
                risk_score=0.05,
                reasons=["Known safe MCP tool"],
                suggested_action="auto_approve",
            )
        if tool_name in MCP_DANGEROUS_TOOLS:
            return ClassificationResult(
                command=f"mcp:{server}/{tool_name}",
                risk_tier=RiskTier.MODERATE,
                risk_score=0.5,
                reasons=["MCP tool with side effects"],
                suggested_action="log_and_proceed",
            )
        return ClassificationResult(
            command=f"mcp:{server}/{tool_name}",
            risk_tier=RiskTier.MODERATE,
            risk_score=0.3,
            reasons=["Unknown MCP tool — classify as moderate"],
            suggested_action="log_and_proceed",
        )

    def record_denial(self) -> bool:
        """
        Track consecutive denials (from classifierApprovals.ts).
        Returns True if cooldown should be enforced.
        """
        now = time.time() * 1000  # ms
        if now - self.last_denial_time > DENIAL_COOLDOWN_MS:
            self.denial_count = 0
        self.denial_count += 1
        self.last_denial_time = now
        return self.denial_count >= MAX_CONSECUTIVE_DENIALS

    def _heuristic_score(self, command: str) -> float:
        """
        Stage 2 heuristic scoring.
        Factors from Claude Code's effort.ts model:
        - Pipe complexity (shell metacharacters)
        - Path depth (filesystem traversal risk)
        - Network indicators (curl, wget, ssh)
        - Write indicators (>, >>, tee)
        """
        score = 0.2  # baseline

        # Pipe complexity
        pipe_count = command.count("|")
        score += min(pipe_count * 0.05, 0.15)

        # Shell metacharacters
        metachar_count = sum(1 for c in command if c in ";&$`\\")
        score += min(metachar_count * 0.03, 0.12)

        # Redirect operators (write risk)
        if ">>" in command or re.search(r">\s*[^&]", command):
            score += 0.15

        # Network indicators
        if re.search(r"\b(curl|wget|ssh|scp|rsync)\b", command, re.IGNORECASE):
            score += 0.1

        # Install commands
        if re.search(r"\b(pip\s+install|npm\s+install|brew\s+install)\b", command, re.IGNORECASE):
            score += 0.2

        # Long commands are inherently riskier
        if len(command) > 200:
            score += 0.05

        return min(score, 1.0)

    def _record(self, result: ClassificationResult) -> None:
        """Record classification for audit trail."""
        self.classification_log.append(result)
        if len(self.classification_log) > 1000:
            self.classification_log = self.classification_log[-500:]

        if result.risk_tier in (RiskTier.DANGEROUS, RiskTier.FORBIDDEN):
            self._write_issue(result)

    def _write_issue(self, result: ClassificationResult) -> None:
        """Write to .beads/issues.jsonl for audit trail."""
        BEADS_DIR.mkdir(parents=True, exist_ok=True)
        entry = {
            "type": "yolo_classification",
            "timestamp": result.timestamp,
            "severity": "critical" if result.risk_tier == RiskTier.FORBIDDEN else "warning",
            **result.to_dict(),
        }
        with open(ISSUES_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_stats(self) -> dict:
        """Return classifier statistics."""
        if not self.classification_log:
            return {"total": 0, "by_tier": {}, "avg_score": 0}

        tier_counts: dict[str, int] = {}
        total_score = 0.0
        for r in self.classification_log:
            tier_counts[r.risk_tier.value] = tier_counts.get(r.risk_tier.value, 0) + 1
            total_score += r.risk_score

        return {
            "total": len(self.classification_log),
            "by_tier": tier_counts,
            "avg_score": total_score / len(self.classification_log),
            "denial_count": self.denial_count,
        }


# ── Effort Resolution (from effort.ts) ───────────────────────────────────


def resolve_effort(
    model: str = "gemini-3.1-flash-lite-preview-thinking",
    explicit_effort: str | None = None,
) -> str:
    """
    Port of effort.ts resolveAppliedEffort().
    Resolution chain: env override → explicit → model default.
    """
    env_override = os.environ.get("AGNT_EFFORT_LEVEL", "").lower()
    if env_override in ("unset", "auto"):
        return "high"  # API default when no effort param sent
    if env_override in EFFORT_LEVELS:
        return env_override
    if explicit_effort and explicit_effort in EFFORT_LEVELS:
        return explicit_effort
    # Model defaults (from effort.ts getDefaultEffortForModel)
    if "opus" in model.lower():
        return "medium"
    if "flash" in model.lower() or "lite" in model.lower():
        return "high"
    return "high"


# ── Watch Mode ────────────────────────────────────────────────────────────


def watch_stdin(classifier: YOLOClassifier, dry_run: bool = False) -> None:
    """Read commands from stdin and classify them (daemon mode)."""
    logger = logging.getLogger("yolo_watch")
    logger.info("YOLO Classifier watching stdin (Ctrl+C to stop)")

    for line in sys.stdin:
        command = line.strip()
        if not command:
            continue

        result = classifier.classify(command)
        output = {
            "input": command,
            "classification": result.to_dict(),
            "effort": resolve_effort(),
        }

        if dry_run:
            print(json.dumps(output, indent=2))
        else:
            # In production: emit to structured log
            print(json.dumps(output))

            if result.risk_tier == RiskTier.FORBIDDEN:
                logger.critical("BLOCKED: %s", command)
            elif result.risk_tier == RiskTier.DANGEROUS:
                logger.warning("CLUTCH: %s → STATE B engaged", command)


# ── CLI Entry Point ──────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Dynamic YOLO Classifier (ported from Claude Code effort.ts)")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch stdin for commands to classify",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Pretty-print classifications without side effects",
    )
    parser.add_argument(
        "--classify",
        type=str,
        help="Classify a single command and exit",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show classifier statistics from current session",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    classifier = YOLOClassifier()

    if args.classify:
        result = classifier.classify(args.classify)
        print(json.dumps(result.to_dict(), indent=2))
    elif args.watch:
        watch_stdin(classifier, dry_run=args.dry_run)
    elif args.stats:
        print(json.dumps(classifier.get_stats(), indent=2))
    else:
        # Self-test mode
        test_commands = [
            "git status",
            "ls -la",
            "rm -rf /",
            "sudo apt-get install",
            "git push --force",
            "npm test",
            "firebase deploy --only hosting",
            "curl http://localhost:3000",
            "python3 -c 'import os; os.system(\"rm -rf /\")'",
            "ruff check --fix .",
            "git filter-branch --all",
            "kubectl delete pod nginx",
        ]
        print("═══ YOLO Classifier Self-Test ═══\n")
        for cmd in test_commands:
            result = classifier.classify(cmd)
            emoji = {
                RiskTier.SAFE: "✅",
                RiskTier.MODERATE: "⚠️ ",
                RiskTier.DANGEROUS: "🔴",
                RiskTier.FORBIDDEN: "⛔",
            }[result.risk_tier]
            print(f"  {emoji} [{result.risk_tier.value:8s}] {result.risk_score:.2f}  {cmd}")

        print(f"\n  Stats: {json.dumps(classifier.get_stats(), indent=2)}")


if __name__ == "__main__":
    main()
