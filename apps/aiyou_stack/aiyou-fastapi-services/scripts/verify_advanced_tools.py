from src.shadowtag_v4.agents.base import AntigravityAgent
from src.shadowtag_v4.tools.registry import registry


def main():
    print("🔍 Verifying Antigravity Advanced Tool Use...")

    # 1. Verify Registry & Examples
    tool = registry.get_tool("search_customer_orders")
    if tool and "examples" in tool:
        print("✅ Tool Registry & Examples: OK")
    else:
        print("❌ Tool Registry or Examples missing")

    # 2. Verify Agent Tool Search
    agent = AntigravityAgent("TestAgent")
    print(f"Initial Tools: {[t['name'] for t in agent.tools]}")

    # Simulate agent searching for "budget" tools
    result = agent.execute_tool_search("budget")
    print(f"Search Result: {result}")

    # Verify tool was loaded
    current_tool_names = [t["name"] for t in agent.tools]
    if "check_budget_compliance" in current_tool_names:
        print("✅ Dynamic Tool Loading: OK")
    else:
        print("❌ Dynamic Tool Loading failed")


if __name__ == "__main__":
    main()
