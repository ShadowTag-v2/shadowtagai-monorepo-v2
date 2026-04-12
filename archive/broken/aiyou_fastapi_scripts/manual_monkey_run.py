import asyncio
import json
import os
import sys

# Add src to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from antigravity.autoresearch import n-autoresearch/Kosmos/BioAgents

from dotenv import load_dotenv

# Explicitly load .env from project root
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(base_path, ".env")
load_dotenv(dotenv_path=env_path)

# Debug: Check if key is loaded (masked)
key = os.getenv("GEMINI_API_KEY")
if not key or "your-" in key:
    print("DEBUG: Primary Key invalid/placeholder. Checking GEMINI_KEY_1...")
    key = os.getenv("GEMINI_KEY_1")

if key and "your-" not in key:
    print(f"DEBUG: Valid Key Found: {key[:5]}...{key[-3:]} (Len: {len(key)})")
    # Force set it for the library
    os.environ["GEMINI_API_KEY"] = key
else:
    print("DEBUG: No valid API Key found (all placeholders).")


async def main():
    print("🐒 ACTIVATING FLYING n-autoresearch/Kosmos/BioAgents (Manual Override) 🐒")
    print("--------------------------------------------------")

    # Initialize the n-autoresearch/Kosmos/BioAgents with Gemini 1.5 Pro
    # Note: Ensure GEMINI_API_KEY is set in your env or .env file
    try:
        n-autoresearch/Kosmos/BioAgents = n-autoresearch/Kosmos/BioAgents(model="gemini-1.5-pro-001")
    except Exception as e:
        print(f"Failed to initialize n-autoresearch/Kosmos/BioAgents: {e}")
        return

    # The Task: Based on your current focus
    task = "Research 'Context Engineering' strategies for LLM agents. Specifically, define the 'Session' vs 'Memory' vs 'Context Compilation' architecture."

    print(f"Task: {task}\n")
    print("Executing... (This uses the n-autoresearch/Kosmos/BioAgents.execute_task() logic)")

    try:
        # We pass an empty context for this manual run
        result = await n-autoresearch/Kosmos/BioAgents.execute_task(task, context={"source": "manual_override"})
        print(f"\nDEBUG RAW RESULT: {json.dumps(result, indent=2)}\n")

        print("\n--- 📝 MONKEY REPORT 📝 ---")
        print(result.get("final_report", "No report generated."))

        if "plan" in result:
            print(f"\n--- 🗺️ STRATEGY PLAN ---\n{result['plan']}")

        if "results" in result:
            print("\n--- 🛠️ TOOLS USED ---")
            for i, res in enumerate(result["results"]):
                print(f"{i + 1}. {res.get('tool')}: {str(res.get('result'))[:100]}...")

    except Exception as e:
        print(f"Monkey Mission Failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
