import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.agents.n-autoresearch/Kosmos/BioAgents7 import n-autoresearch/Kosmos/BioAgents7, Task


def test_rlm_recursion():
    print("🧪 [TEST] Initializing n-autoresearch/Kosmos/BioAgents7 with RLM...")
    kosmos = n-autoresearch/Kosmos/BioAgents7()

    # 1. Load Dummy "Large Context" into REPL
    large_text = (
        "This is a massive genomic dataset. " * 1000
        + " SECRET_GENE: TP53_MUTATION "
        + "End of data."
    )
    print(f"🧪 [TEST] Loading Context ({len(large_text)} chars) into KosmosREPL...")
    kosmos.repl.load_context("context", large_text)

    # 2. Create an RLM-Specific Task
    # The agent should detect "find" and "context" and use regex instead of linear reading
    task = Task("DataAnalysis", "Find the SECRET_GENE in the context.")

    print(f"🧪 [TEST] Dispatching Task: {task.description}")

    # 3. Execute
    # We manually pick an agent to test the logic directly
    agent = kosmos.data_agent_pool[0]
    finding = agent.execute_task(task, repl=kosmos.repl)

    print(f"🧪 [TEST] Agent Finding: {finding.content}")
    print(f"🧪 [TEST] Provenance: {finding.provenance}")

    # 4. Assertions
    assert "RLM Analysis" in finding.content, "Agent did not trigger RLM mode."
    assert "TP53_MUTATION" in finding.content, "Agent failed to find the needle."
    assert "re.search" in finding.content, "Agent did not use Python regex code (re.search)."

    print("✅ [TEST] PASSED: RLM Recursion Verified.")


if __name__ == "__main__":
    test_rlm_recursion()
