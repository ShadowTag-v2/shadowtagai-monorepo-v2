import time


class StreamingWatchdog:
    async def watch(self, stream, timeout=90.0, stall_threshold=30.0):
        """Kills silently hung TCP connections during streaming."""
        last_byte = time.time()
        try:
            async for chunk in stream:
                now = time.time()
                if now - last_byte > stall_threshold:
                    print(f"⚠️ WATCHDOG: Stall detected ({now - last_byte}s gap)")
                last_byte = now
                yield chunk
        except TimeoutError:
            print("🚨 WATCHDOG: Stream stalled for >90s. Severing connection.")
            raise
