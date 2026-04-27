import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.ssrf import SSRFGuard
from src.services.watchdog import StreamingWatchdog
from src.core.prompt_cache import CacheManager
from src.tools.tool_search import ToolSearchTool
from src.services.cascade import CascadeDetector
from src.core.hooks import HooksManager
from src.utils.vcr import VCRDehydrator


class APIClient:
    """
    Consolidated API Client demonstrating the integration of:
    - SSRFGuard
    - StreamingWatchdog
    - CacheManager
    - ToolSearchTool
    - CascadeDetector
    - HooksManager
    - VCRDehydrator
    """

    def __init__(self, full_tools_registry):
        self.ssrf_guard = SSRFGuard()
        self.watchdog = StreamingWatchdog()
        self.cache_manager = CacheManager()
        self.tool_search = ToolSearchTool(full_tools_registry)
        self.cascade_detector = CascadeDetector()
        self.hooks = HooksManager()
        self.vcr = VCRDehydrator("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")

    async def fetch(self, url):
        # SSRF Protection
        safe_ip = self.ssrf_guard.resolve_and_verify(url)
        return f"Fetched {safe_ip}"

    async def generate_response(self, system_prompt, dynamic_state, cache_read_tokens=0):
        # Tools Deferral
        deferred_tools = self.tool_search.get_deferred_manifest()

        # Cache break detection & splitting
        self.cache_manager.detect_break(deferred_tools, system_prompt, cache_read_tokens)
        full_prompt = self.cache_manager.build_prompt(system_prompt, dynamic_state)

        # Hooks trigger
        await self.hooks.emit("PreToolUse", prompt=full_prompt)

        # Simulating API request with Cascade/529 Tracking
        status_code = 200
        self.cascade_detector.record_response(status_code)

        # Streaming with watchdog
        async def dummy_stream():
            yield b"Hello"
            await asyncio.sleep(0.1)
            yield b"World"

        async for _chunk in self.watchdog.watch(dummy_stream()):
            pass

        return "OK"
