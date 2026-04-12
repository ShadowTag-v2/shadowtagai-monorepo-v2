"""
JuraClassifier: Classifies requests into cost tiers.

Classification logic:
1. User override (if provided)
2. Governance tasks always PRO
3. Context size thresholds
4. Complexity estimation
"""

import re
from dataclasses import dataclass
from enum import Enum


class CostTier(Enum):
    """Cost tier for request routing."""

    FREE = "free"  # Grok, 1 agent, 5s timeout
    FLASH = "flash"  # Gemini Flash, 1-3 agents, 2s timeout
    PRO = "pro"  # Gemini Pro/Claude, 1-8 agents, 10s timeout
    AUTO = "auto"  # JuraClassifier decides


@dataclass
class ClassificationResult:
    """Result of tier classification."""

    tier: CostTier
    reason: str
    complexity_score: float
    context_tokens: int


class JuraClassifier:
    """
    Classifies requests into cost tiers based on:
    - Task complexity (keyword analysis)
    - Context size (token count)
    - Task type (governance vs execution)
    - User override
    """

    # Complexity thresholds (0.0-1.0)
    COMPLEXITY_THRESHOLDS = {
        CostTier.FREE: 0.3,  # Simple queries
        CostTier.FLASH: 0.7,  # Medium complexity
        CostTier.PRO: 1.0,  # Complex/governance
    }

    # Context size thresholds (tokens)
    CONTEXT_THRESHOLDS = {
        CostTier.FREE: 1000,  # <1K tokens
        CostTier.FLASH: 8000,  # <8K tokens
        CostTier.PRO: 128000,  # Full context
    }

    # Keywords that indicate high complexity
    HIGH_COMPLEXITY_KEYWORDS = [
        "analyze",
        "comprehensive",
        "detailed",
        "multi-step",
        "architecture",
        "design",
        "refactor",
        "security",
        "optimize",
        "review",
        "audit",
        "strategy",
        "governance",
        "compliance",
        "legal",
        "financial",
    ]

    # Keywords that indicate low complexity
    LOW_COMPLEXITY_KEYWORDS = [
        "simple",
        "quick",
        "brief",
        "short",
        "yes/no",
        "true/false",
        "one word",
        "define",
        "what is",
        "list",
    ]

    def __init__(self):
        self._high_pattern = re.compile(
            r"\b(" + "|".join(self.HIGH_COMPLEXITY_KEYWORDS) + r")\b", re.IGNORECASE
        )
        self._low_pattern = re.compile(
            r"\b(" + "|".join(self.LOW_COMPLEXITY_KEYWORDS) + r")\b", re.IGNORECASE
        )

    def classify(
        self,
        task: str,
        context_size: int = 0,
        task_type: str = "execution",
        override: CostTier | None = None,
    ) -> ClassificationResult:
        """
        Classify a request into a cost tier.

        Args:
            task: The task description/prompt
            context_size: Number of tokens in context
            task_type: "governance" or "execution"
            override: User-specified tier override

        Returns:
            ClassificationResult with tier, reason, and metrics
        """
        # 1. User override
        if override and override != CostTier.AUTO:
            return ClassificationResult(
                tier=override,
                reason=f"User override to {override.value}",
                complexity_score=0.0,
                context_tokens=context_size,
            )

        # 2. Governance always PRO
        if task_type == "governance":
            return ClassificationResult(
                tier=CostTier.PRO,
                reason="Governance task requires PRO tier",
                complexity_score=1.0,
                context_tokens=context_size,
            )

        # 3. Estimate complexity
        complexity = self._estimate_complexity(task)

        # 4. Context size classification
        if context_size > self.CONTEXT_THRESHOLDS[CostTier.FLASH]:
            return ClassificationResult(
                tier=CostTier.PRO,
                reason=f"Large context ({context_size} tokens > 8K)",
                complexity_score=complexity,
                context_tokens=context_size,
            )
        if context_size > self.CONTEXT_THRESHOLDS[CostTier.FREE]:
            # Medium context, check complexity
            if complexity > self.COMPLEXITY_THRESHOLDS[CostTier.FLASH]:
                return ClassificationResult(
                    tier=CostTier.PRO,
                    reason=f"Medium context + high complexity ({complexity:.2f})",
                    complexity_score=complexity,
                    context_tokens=context_size,
                )
            return ClassificationResult(
                tier=CostTier.FLASH,
                reason=f"Medium context ({context_size} tokens)",
                complexity_score=complexity,
                context_tokens=context_size,
            )

        # 5. Small context - use complexity
        if complexity > self.COMPLEXITY_THRESHOLDS[CostTier.FLASH]:
            return ClassificationResult(
                tier=CostTier.PRO,
                reason=f"High complexity ({complexity:.2f})",
                complexity_score=complexity,
                context_tokens=context_size,
            )
        if complexity > self.COMPLEXITY_THRESHOLDS[CostTier.FREE]:
            return ClassificationResult(
                tier=CostTier.FLASH,
                reason=f"Medium complexity ({complexity:.2f})",
                complexity_score=complexity,
                context_tokens=context_size,
            )

        return ClassificationResult(
            tier=CostTier.FREE,
            reason=f"Low complexity ({complexity:.2f}), small context",
            complexity_score=complexity,
            context_tokens=context_size,
        )

    def _estimate_complexity(self, task: str) -> float:
        """
        Estimate task complexity (0.0-1.0) based on keywords.

        Returns:
            Complexity score between 0.0 and 1.0
        """
        if not task:
            return 0.0

        # Count keyword matches
        high_matches = len(self._high_pattern.findall(task))
        low_matches = len(self._low_pattern.findall(task))

        # Word count factor (longer = more complex)
        word_count = len(task.split())
        length_factor = min(word_count / 100, 1.0)  # Caps at 100 words

        # Question complexity (multiple sentences = more complex)
        sentence_count = task.count(".") + task.count("?") + task.count("!")
        sentence_factor = min(sentence_count / 5, 1.0)  # Caps at 5 sentences

        # Calculate score
        base_score = 0.3  # Default medium-low
        base_score += high_matches * 0.15  # Each high keyword adds 0.15
        base_score -= low_matches * 0.1  # Each low keyword subtracts 0.1
        base_score += length_factor * 0.2  # Length adds up to 0.2
        base_score += sentence_factor * 0.15  # Sentences add up to 0.15

        return max(0.0, min(1.0, base_score))

    def estimate_tokens(self, text: str) -> int:
        """
        Rough token count estimation.
        Rule of thumb: ~4 characters per token for English.
        """
        return len(text) // 4
