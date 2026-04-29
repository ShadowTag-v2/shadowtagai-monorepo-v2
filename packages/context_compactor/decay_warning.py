"""
P5.4: Context Decay Warning System

Monitors the conversational context window and injects warnings when decay is imminent.
Triggers compaction if thresholds are crossed.
"""

import logging

logger = logging.getLogger(__name__)


class ContextDecayMonitor:
    def __init__(self, token_threshold: int = 20000, turn_threshold: int = 50):
        self.token_threshold = token_threshold
        self.turn_threshold = turn_threshold

    def check_context_health(self, current_tokens: int, current_turns: int) -> str | None:
        """
        Check if context decay is imminent based on token count or turn count.
        Returns a warning string if thresholds are crossed, else None.
        """
        warnings = []
        if current_tokens >= self.token_threshold:
            warnings.append(f"Tokens ({current_tokens}) exceed threshold ({self.token_threshold})")

        if current_turns >= self.turn_threshold:
            warnings.append(f"Turns ({current_turns}) exceed threshold ({self.turn_threshold})")

        if warnings:
            reason = " and ".join(warnings)
            logger.warning(f"Context decay warning triggered: {reason}")
            return f"<WARNING: CONTEXT DECAY IMMINENT. TRIGGER COMPACTION> Reason: {reason}"

        return None
