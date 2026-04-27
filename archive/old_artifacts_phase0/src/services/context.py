class FourTierContext:
    def microcompact(self, memory):
        """Strips stale outputs without busting prompt cache."""
        for msg in memory:
            if len(msg.get("content", "")) > 5000:
                msg["content"] = msg["content"][:1000] + "\n...[MICROCOMPACTED]...\n" + msg["content"][-1000:]
        return memory

    def reactive_compact(self, api_call, memory, *args):
        """Tries API, intercepts 413 Too Large, compacts, and retries."""
        try:
            return api_call(memory, *args)
        except Exception as e:
            if "413" in str(e) or "too_long" in str(e).lower():
                compacted = self.microcompact(memory)
                return api_call(compacted, *args)
            raise
