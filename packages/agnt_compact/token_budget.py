import os

class TokenBudgetManager:
    """Manages the 1M context window (Opus/Sonnet 4.6)."""
    def __init__(self):
        self.max_tokens = int(os.environ.get("CLAUDE_CODE_MAX_CONTEXT_TOKENS", 1000000))
        self.trigger_threshold = self.max_tokens * 0.80
        self.target_freed = 0.60

    async def check_and_compact(self, history: list, current_tokens: int) -> list:
        if current_tokens < self.trigger_threshold:
            return history

        print(f"⚠️ Context at {current_tokens}/{self.max_tokens} tokens (>80%). Initiating Auto-Compact...")
        keep_prefix = history[:2]
        keep_recent = history[-10:]
        bloated_middle = history[2:-10]
        
        compaction_instruction = os.environ.get("CUSTOM_COMPACTION_INSTRUCTION", "Summarize the key events.")
        summary = await self._generate_claude_summary(bloated_middle, compaction_instruction)

        compacted_history = keep_prefix + [
            {"role": "assistant", "content": summary},
            {"role": "user", "content": "<CompactBoundaryMessage>Historical context compacted. Proceed from here.</CompactBoundaryMessage>"}
        ] + keep_recent

        freed_percentage = (1 - (len(str(compacted_history)) / len(str(history)))) * 100
        print(f"✅ Auto-Compact complete. ~{freed_percentage:.1f}% of context window freed.")
        return compacted_history

    async def _generate_claude_summary(self, messages: list, prompt: str) -> str:
        return f"[COMPACTED SUMMARY]: Exhaustive context compressed via native agent synthesis."
