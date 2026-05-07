import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath("src"))

try:
    from libs.shadowtag_v4.agents.recursive_rlm import RecursiveAgent, TextEnvironment

    print("Successfully imported RecursiveAgent")
except ImportError as e:
    print(f"ImportError: {e}")
    raise SystemExit(1) from e


def test_rlm():
    print("Initializing RLM Agent...")
    agent = RecursiveAgent()

    file_path = "secret.txt"
    print(f"Loading environment from {file_path}...")
    env = TextEnvironment(file_path)

    query = "What is the answer?"
    print(f"Solving for: '{query}'")

    result = agent.solve(query, env)
    print(f"RLM Result: {result}")


if __name__ == "__main__":
    test_rlm()
