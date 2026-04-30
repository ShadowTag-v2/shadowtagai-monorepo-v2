import unittest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.services.watchdog import StreamingWatchdog


class TestStreamingWatchdog(unittest.IsolatedAsyncioTestCase):
    async def test_watchdog_timeout(self):
        async def slow_stream():
            yield "A"
            await asyncio.sleep(0.5)
            yield "B"

        wd = StreamingWatchdog()
        chunks = []
        try:
            async for chunk in wd.watch(slow_stream(), timeout=1.0, stall_threshold=0.1):
                chunks.append(chunk)
        except Exception:
            pass
        self.assertEqual(chunks, ["A", "B"])


if __name__ == "__main__":
    unittest.main()
