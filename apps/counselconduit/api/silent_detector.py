"""Judge 6 Silent Detector — Passive signal collection layer.

Detects patterns that suggest prompt injection, data exfiltration,
or unauthorized escalation BEFORE they reach the model router.

Part of the Cor.30 Security Doctrine (OWASP LLM01, LLM05).
"""

import re
from dataclasses import dataclass


@dataclass
class SignalPacket:
    """Immutable record of a detected signal."""

    signal_type: str
    confidence: float
    raw_match: str
    context: str


INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions",
    r"you\s+are\s+now\s+",
    r"system\s*:\s*",
    r"<\|im_start\|>",
    r"\[INST\]",
    r"<\|endoftext\|>",
    r"IGNORE ALL PREVIOUS",
]

EXFIL_PATTERNS = [
    r"(api[_\s]?key|secret|password|token)\s*[:=]",
    r"(SELECT|INSERT|UPDATE|DELETE|DROP)\s+",
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__\s*\(",
    r"subprocess\.",
]


def scan_input(text: str) -> list[SignalPacket]:
    """Scan input for known attack patterns.

    Design: Zero false negatives > low false positives.
    If in doubt, flag it. Judge 6 makes the final call.
    """
    signals: list[SignalPacket] = []
    for pattern in INJECTION_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ctx_start = max(0, match.start() - 50)
            ctx_end = min(len(text), match.end() + 50)
            signals.append(
                SignalPacket(
                    signal_type="PROMPT_INJECTION",
                    confidence=0.9,
                    raw_match=match.group(),
                    context=text[ctx_start:ctx_end],
                )
            )
    for pattern in EXFIL_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ctx_start = max(0, match.start() - 50)
            ctx_end = min(len(text), match.end() + 50)
            signals.append(
                SignalPacket(
                    signal_type="DATA_EXFIL",
                    confidence=0.7,
                    raw_match=match.group(),
                    context=text[ctx_start:ctx_end],
                )
            )
    return signals
