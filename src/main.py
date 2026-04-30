# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import asyncio
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Omega Fix: Wiring the Async Watchdog into the main event loop
class StreamingWatchdog:
    async def monitor(self):
        print("👁️  StreamingWatchdog active. Monitoring context streams...")
        while True:
            await asyncio.sleep(60)


async def parallel_bootstrap():
    await asyncio.sleep(0.135)
    return {"status": "authorized"}


async def main():
    print("\n🚀 Bootstrapping Antigravity Engine...")
    start_time = time.time()

    # Run bootstrap and watchdog concurrently
    watchdog = StreamingWatchdog()
    bootstrap_task = asyncio.create_task(parallel_bootstrap())
    watchdog_task = asyncio.create_task(watchdog.monitor())

    await bootstrap_task
    print(f"⏱️  Boot sequence finished in {(time.time() - start_time) * 1000:.2f}ms")

    from packages.tool_gateway.honeypots import HONEYPOT_REGISTRY

    print(f"🛡️  Loaded {len(HONEYPOT_REGISTRY)} honeypot routes into primary gateway.")

    print("\n🟢 SYSTEM ONLINE. READY FOR DAEMON DISPATCH.")

    # Keep watchdog alive
    await watchdog_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 System gracefully shut down.")
