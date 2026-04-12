import os
import sys

# Add src to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from antigravity.adk_monkeys import ADKn-autoresearch/Kosmos/BioAgents

from dotenv import load_dotenv

# Explicitly load .env from project root
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(base_path, ".env")
load_dotenv(dotenv_path=env_path)


def main():
    print("🐒 ACTIVATING ADK FLYING n-autoresearch/Kosmos/BioAgents (Official Google MCP) 🐒")
    print("--------------------------------------------------")

    # Check for keys
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("⚠️  WARNING: GOOGLE_CLOUD_PROJECT not set. BigQuery MCP might fail.")
    if not os.getenv("MAPS_API_KEY"):
        print("⚠️  WARNING: MAPS_API_KEY not set. Maps MCP will be disabled.")

    try:
        n-autoresearch/Kosmos/BioAgents = ADKn-autoresearch/Kosmos/BioAgents()

        task = "What is the capital of France? (Test Task)"
        print(f"\nTask: {task}\n")

        print("Executing via LlmAgent...")
        result = n-autoresearch/Kosmos/BioAgents.execute_task(task)

        print("\n--- 📝 ADK AGENT REPORT 📝 ---")
        print(result)
        print("------------------------------")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
