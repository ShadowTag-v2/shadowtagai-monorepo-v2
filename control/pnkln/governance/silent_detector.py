# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Judge #6 Silent Detector — Passive signal collection layer.

Scans content streams for NY S7263, RAISE Act, credential, and injection
violations without blocking the caller. All hits are routed through
Judge6Engine.evaluate() and returned as GovernanceDecision objects.
"""

from __future__ import annotations

import re

from .judge6_core import GovernanceDecision, Judge6Engine, RiskEvent, ViolationType

_UNAUTHORIZED_PRACTICE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"you\s+should\s+(?:sue|file\s+a\s+(?:lawsuit|claim|motion))", re.I),
    re.compile(r"this\s+constitutes\s+(?:malpractice|negligence|fraud|breach)", re.I),
    re.compile(
        r"you\s+(?:have|has)\s+a\s+(?:strong|valid|viable)\s+(?:case|claim|cause\s+of\s+action)",
        re.I,
    ),
    re.compile(r"(?:my|the)\s+(?:legal\s+)?(?:advice|recommendation|counsel)\s+is", re.I),
    re.compile(r"(?:the|your)\s+diagnosis\s+is", re.I),
    re.compile(r"you\s+(?:have|suffer\s+from|are\s+diagnosed\s+with)\s+(?!a\s+(?:right|question))", re.I),
    re.compile(r"(?:prescribe|prescribed|prescribing)\s+(?:you\s+)?\w+\s+(?:mg|ml|tablets)", re.I),
]

_RAISE_ACT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?:bypass|disable|remove|circumvent)\s+(?:safety|guardrail|filter|alignment)", re.I),
    re.compile(r"(?:generate|create|produce)\s+(?:bioweapon|biological\s+weapon|chemical\s+weapon)", re.I),
]

_CREDENTIAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?:password|passwd|secret|api[_-]?key)\s*[:=]\s*\S{8,}", re.I),
    re.compile(r"(?:sk-|ghp_|ghs_|AIza)[A-Za-z0-9_\-]{16,}", re.I),
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
]

_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions", re.I),
    re.compile(r"disregard\s+(?:your\s+)?(?:system\s+)?prompt", re.I),
    re.compile(r"<\s*script[^>]*>", re.I),
    re.compile(r"(?:union|select|insert|drop|truncate)\s+\w+", re.I),
]


class SilentDetector:
    """Passive scanner — runs on every content stream without blocking output."""

    def __init__(self, engine: Judge6Engine, agent_id: str = "silent-detector") -> None:
        self.engine = engine
        self.agent_id = agent_id
        self._scan_count = 0

    def scan(
        self,
        content: str,
        session_id: str = "",
        source: str = "",
        context: dict | None = None,
    ) -> list[GovernanceDecision]:
        self._scan_count += 1
        ctx = context or {}
        decisions: list[GovernanceDecision] = []

        for violation_type, hit in self._detect_violations(content):
            event = RiskEvent(
                violation_type=violation_type,
                raw_signal=content[:500],
                source=source or self.agent_id,
                session_id=session_id,
                context={**ctx, "pattern_hit": hit},
            )
            decisions.append(self.engine.evaluate(event))

        return decisions

    def _detect_violations(self, content: str) -> list[tuple[ViolationType, str]]:
        hits: list[tuple[ViolationType, str]] = []

        for p in _UNAUTHORIZED_PRACTICE_PATTERNS:
            if m := p.search(content):
                hits.append((ViolationType.LEGAL_NY_S7263_UNAUTHORIZED_PRACTICE, m.group(0)[:80]))

        for p in _RAISE_ACT_PATTERNS:
            if m := p.search(content):
                hits.append((ViolationType.LEGAL_RAISE_ACT_FRONTIER, m.group(0)[:80]))

        for p in _CREDENTIAL_PATTERNS:
            if m := p.search(content):
                hits.append((ViolationType.CYBER_CREDENTIAL_EXPOSURE, m.group(0)[:80]))

        for p in _INJECTION_PATTERNS:
            if m := p.search(content):
                hits.append((ViolationType.OP_PROMPT_INJECTION, m.group(0)[:80]))

        return hits

    @property
    def scan_count(self) -> int:
        return self._scan_count
