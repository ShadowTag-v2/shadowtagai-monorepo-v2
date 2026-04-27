import asyncio
import sys
import os
import time

# Ensure Python can resolve the src/ directory imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.core.startup import parallel_bootstrap
from src.tools.tool_search import ToolSearchTool


async def main():
    print("\n🚀 Bootstrapping Antigravity Engine...")
    start_time = time.time()

    # --------------------------------------------------------------------------
    # EPIC 3 (Option 12): Fire parallel keychain reads BEFORE heavy imports
    # --------------------------------------------------------------------------
    bootstrap_task = asyncio.create_task(parallel_bootstrap())

    # Simulate the "Import Tax" (loading heavy ML libs, unified_memory, etc.)
    await asyncio.sleep(0.135)

    # Harvest the background pre-fetched data (Wait time is 0ms!)
    await bootstrap_task

    print(f"⏱️  Boot sequence finished in {(time.time() - start_time) * 1000:.2f}ms")
    print("✅ Parallel Startup Module: ACTIVE (Keychain pre-fetched in background)")

    # --------------------------------------------------------------------------
    # EPIC 2 (Option 7): Tool Deferral Economics
    # --------------------------------------------------------------------------
    print("\n📦 Initializing Context Economics...")

    # Mocking a massive 50+ tool payload
    HEAVY_REGISTRY = {f"mcp_tool_{i}": {"description": f"Heavy JSON Schema for tool {i}", "parameters": {"type": "object"}} for i in range(1, 51)}

    deferral_engine = ToolSearchTool(HEAVY_REGISTRY)

    # What the LLM ACTUALLY sees in the system prompt now:
    manifest = deferral_engine.get_deferred_manifest()
    print(f"📉 Context Saved! Instead of sending {len(HEAVY_REGISTRY)} heavy schemas, the LLM only sees:")
    print(f"   {str(manifest)[:100]}...]")

    # Dynamically loading a schema only when the LLM asks for it
    print(f"🔍 Searching for 'tool_42' on demand: {list(deferral_engine.search('tool_42').keys())}")
    print("\n🟢 SYSTEM ONLINE. READY FOR DAEMON DISPATCH.")


if __name__ == "__main__":
    asyncio.run(main())
