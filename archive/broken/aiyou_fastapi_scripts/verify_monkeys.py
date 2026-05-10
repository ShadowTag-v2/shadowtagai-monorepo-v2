import asyncio
import os
import sys

# Add src to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Explicitly load .env from project root
from dotenv import load_dotenv

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(base_path, ".env")
load_dotenv(dotenv_path=env_path)

from antigravity.autoresearch import n-autoresearch/Kosmos/BioAgents


async def main():
    print("🐒 ACTIVATING FLYING n-autoresearch/Kosmos/BioAgents (Official Google ADK + MCP) 🐒")
    print("---------------------------------------------------------")

    # Check for keys
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("⚠️  WARNING: GOOGLE_CLOUD_PROJECT not set. BigQuery MCP might fail.")
    if not os.getenv("MAPS_API_KEY"):
        print("⚠️  WARNING: MAPS_API_KEY not set. Maps MCP will be disabled.")

    # Check for GOOGLE_API_KEY for LlmAgent
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  WARNING: GOOGLE_API_KEY not set. LlmAgent will fail (requires Gemini API Key).")

    try:
        n-autoresearch/Kosmos/BioAgents = n-autoresearch/Kosmos/BioAgents()
        agent_name = getattr(n-autoresearch/Kosmos/BioAgents, "name", "n-autoresearch/Kosmos/BioAgents")
        print(f"✅ Agent Initialized: {agent_name}")

        task = "What is the capital of France? (Test Task)"
        print(f"\nTask: {task}\n")

        print("Executing via LlmAgent...")
        # n-autoresearch/Kosmos/BioAgents.execute_task is expected to be async and return a dict
        result = await n-autoresearch/Kosmos/BioAgents.execute_task(task)

        print("\n--- 📝 AGENT REPORT 📝 ---")
        print(result)
        print("--------------------------")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
