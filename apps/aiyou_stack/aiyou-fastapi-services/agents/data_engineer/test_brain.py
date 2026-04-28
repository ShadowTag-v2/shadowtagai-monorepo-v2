# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import asyncio
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.getcwd())

from agents.data_engineer.agent import DataEngineeringAgent


async def main():
    PROJECT_ID = "acquired-jet-478701-b3"
    print(f"🧠 Initializing Data Engineering Agent for project: {PROJECT_ID}")

    agent = DataEngineeringAgent(PROJECT_ID)

    print("🔬 Checking Nervous System Health (BigQuery)...")
    health = await agent.check_nervous_system_health()

    print("\n---------- ANALYSIS RESULT ----------")
    print(health)
    print("-------------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
