# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.sales_agent.core import SalesAutomator


async def main():
    print("=== STARTING SALES AGENT DEMO ===")
    agent = SalesAutomator()

    # Run the agent
    await agent.execute_run()

    print("=== DEMO COMPLETE ===")

    # Check if artifacts were "created" (simulated)
    if agent.state.messages_sent > 0:
        print("✅ SUCCESS: Agent generated outreach messages.")
    else:
        print("❌ FAILURE: Agent failed to generate messages.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
