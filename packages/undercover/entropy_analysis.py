# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Anti-Distillation Entropy Analysis.

Detects potential model distillation attempts by analyzing output entropy
patterns. When outputs consistently show suspiciously low entropy (i.e.,
over-confident, templated responses), it may indicate an external party
is using the agent's outputs to train a competing model.

Ported from: Claude Code services/undercover/antiDistillation.ts

Key metrics:
    - Token-level entropy (Shannon) of outputs
    - Bigram repetition rate
    - Vocabulary diversity (unique/total ratio)
    - Template detection via structural fingerprinting

Reference: CC Forensic Spec §17 — Anti-Distillation Mechanisms
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EntropyReport:
    """Result of entropy analysis on a text sample.

    Attributes:
        token_entropy: Shannon entropy of unigram token distribution (bits).
        bigram_repetition: Fraction of repeated bigrams (0.0–1.0).
        vocab_diversity: Unique tokens / total tokens (0.0–1.0).
        structural_fingerprint: SHA-256 of structural skeleton (lowered, stripped).
        is_suspicious: True if metrics suggest distillation-quality output.
        flags: Human-readable explanations of triggered checks.
    """

    token_entropy: float
    bigram_repetition: float
    vocab_diversity: float
    structural_fingerprint: str
    is_suspicious: bool
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSONL telemetry emission."""
        return {
            "token_entropy": round(self.token_entropy, 4),
            "bigram_repetition": round(self.bigram_repetition, 4),
            "vocab_diversity": round(self.vocab_diversity, 4),
            "structural_fingerprint": self.structural_fingerprint,
            "is_suspicious": self.is_suspicious,
            "flags": self.flags,
        }


# ---------------------------------------------------------------------------
# Thresholds (calibrated against CC forensic spec §17)
# ---------------------------------------------------------------------------

# Outputs below this entropy are suspiciously templated.
_MIN_ENTROPY_THRESHOLD = 2.5

# Bigram repetition above this signals copy-paste / template behavior.
_MAX_BIGRAM_REPETITION = 0.35

# Vocabulary diversity below this signals constrained generation.
_MIN_VOCAB_DIVERSITY = 0.25

# Minimum token count to run analysis (skip very short outputs).
_MIN_TOKEN_COUNT = 20


def _tokenize(text: str) -> list[str]:
    """Simple whitespace tokenizer for entropy analysis.

    We intentionally do NOT use a BPE/sentencepiece tokenizer here — the
    analysis targets surface-level lexical diversity, not subword entropy.
    """
    return text.split()


def _shannon_entropy(tokens: list[str]) -> float:
    """Compute Shannon entropy (bits) of the token frequency distribution."""
    if not tokens:
        return 0.0
    counter = Counter(tokens)
    total = len(tokens)
    entropy = 0.0
    for count in counter.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def _bigram_repetition(tokens: list[str]) -> float:
    """Compute the fraction of repeated bigrams.

    Returns 0.0 if there are fewer than 2 tokens.
    """
    if len(tokens) < 2:
        return 0.0
    bigrams = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
    counter = Counter(bigrams)
    repeated = sum(1 for _bg, count in counter.items() if count > 1)
    return repeated / len(counter) if counter else 0.0


def _vocab_diversity(tokens: list[str]) -> float:
    """Compute the unique-to-total token ratio."""
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def _structural_fingerprint(text: str) -> str:
    """Generate a structural fingerprint of the text.

    Strips all alphanumeric content and hashes the remaining structure
    (punctuation, whitespace patterns). Two outputs with the same structure
    but different content will match — indicating template reuse.
    """
    # Keep only structural characters: punctuation, newlines, brackets
    skeleton = ""
    for ch in text:
        if ch in "\n\t .,;:!?()[]{}\"'`-=+*/<>@#$%^&|\\~":
            skeleton += ch
    return hashlib.sha256(skeleton.encode("utf-8")).hexdigest()[:16]


def analyze_entropy(text: str) -> EntropyReport:
    """Analyze a text output for distillation-indicative patterns.

    Args:
        text: The agent output text to analyze.

    Returns:
        EntropyReport with metrics and suspicion flag.
    """
    tokens = _tokenize(text)
    flags: list[str] = []

    # Short-circuit for very short texts — not enough signal.
    if len(tokens) < _MIN_TOKEN_COUNT:
        return EntropyReport(
            token_entropy=0.0,
            bigram_repetition=0.0,
            vocab_diversity=0.0,
            structural_fingerprint=_structural_fingerprint(text),
            is_suspicious=False,
            flags=["too_short_for_analysis"],
        )

    entropy = _shannon_entropy(tokens)
    bigram_rep = _bigram_repetition(tokens)
    vocab_div = _vocab_diversity(tokens)
    fingerprint = _structural_fingerprint(text)

    if entropy < _MIN_ENTROPY_THRESHOLD:
        flags.append(f"low_entropy({entropy:.2f} < {_MIN_ENTROPY_THRESHOLD})")

    if bigram_rep > _MAX_BIGRAM_REPETITION:
        flags.append(f"high_bigram_repetition({bigram_rep:.2f} > {_MAX_BIGRAM_REPETITION})")

    if vocab_div < _MIN_VOCAB_DIVERSITY:
        flags.append(f"low_vocab_diversity({vocab_div:.2f} < {_MIN_VOCAB_DIVERSITY})")

    # Suspicious if 2+ flags triggered.
    is_suspicious = len(flags) >= 2

    return EntropyReport(
        token_entropy=entropy,
        bigram_repetition=bigram_rep,
        vocab_diversity=vocab_div,
        structural_fingerprint=fingerprint,
        is_suspicious=is_suspicious,
        flags=flags,
    )


class EntropyMonitor:
    """Session-level monitor that tracks entropy trends across outputs.

    Maintains a sliding window of recent EntropyReports and raises alerts
    when the session-level average entropy drops below thresholds —
    indicating sustained low-quality output that could fuel distillation.

    Args:
        window_size: Number of recent reports to track.
        alert_threshold: Number of consecutive suspicious reports before alerting.
    """

    def __init__(
        self,
        window_size: int = 50,
        alert_threshold: int = 5,
    ) -> None:
        self._window_size = window_size
        self._alert_threshold = alert_threshold
        self._reports: list[EntropyReport] = []
        self._consecutive_suspicious: int = 0
        self._total_analyzed: int = 0
        self._total_suspicious: int = 0

    def observe(self, text: str) -> EntropyReport:
        """Analyze text and track the result.

        Args:
            text: Agent output text.

        Returns:
            The EntropyReport for this observation.
        """
        report = analyze_entropy(text)
        self._reports.append(report)
        self._total_analyzed += 1

        # Trim window
        if len(self._reports) > self._window_size:
            self._reports = self._reports[-self._window_size :]

        if report.is_suspicious:
            self._consecutive_suspicious += 1
            self._total_suspicious += 1
        else:
            self._consecutive_suspicious = 0

        return report

    @property
    def is_alert(self) -> bool:
        """True if consecutive suspicious outputs exceed the alert threshold."""
        return self._consecutive_suspicious >= self._alert_threshold

    @property
    def session_avg_entropy(self) -> float:
        """Average token entropy across the current window."""
        if not self._reports:
            return 0.0
        return sum(r.token_entropy for r in self._reports) / len(self._reports)

    @property
    def suspicious_rate(self) -> float:
        """Fraction of all analyzed outputs that were suspicious."""
        if self._total_analyzed == 0:
            return 0.0
        return self._total_suspicious / self._total_analyzed

    def get_stats(self) -> dict[str, Any]:
        """Return diagnostic stats for the telemetry sink."""
        return {
            "total_analyzed": self._total_analyzed,
            "total_suspicious": self._total_suspicious,
            "consecutive_suspicious": self._consecutive_suspicious,
            "session_avg_entropy": round(self.session_avg_entropy, 4),
            "suspicious_rate": round(self.suspicious_rate, 4),
            "is_alert": self.is_alert,
            "window_size": self._window_size,
            "alert_threshold": self._alert_threshold,
        }

    def __repr__(self) -> str:
        return f"EntropyMonitor(analyzed={self._total_analyzed}, suspicious={self._total_suspicious}, alert={self.is_alert})"
