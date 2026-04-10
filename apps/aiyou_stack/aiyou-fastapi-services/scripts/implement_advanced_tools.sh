#!/bin/bash
set -e

# ==============================================================================
# ANTIGRAVITY: Advanced Tool Use Implementation Script
# ==============================================================================
# This script implements the "Advanced Tool Use" patterns (Tool Search, PTC, Examples)
# into the ShadowTag-v2-fastapi-services agent ecosystem.
#
# Patterns:
# 1. Tool Search: Adds a 'search_tools' capability to the base agent class.
# 2. Programmatic Tool Calling: Enables Python code execution for orchestration.
# 3. Tool Examples: Injects few-shot examples into key tool definitions.
# ==============================================================================

echo "🚀 Initiating Antigravity Tool Upgrade..."

# 1. Create the Tool Registry & Search Capability
# ------------------------------------------------------------------------------
echo "📦 Creating Tool Registry (src/ShadowTag-v2/tools/registry.py)..."
mkdir -p src/ShadowTag-v2/tools

cat > src/ShadowTag-v2/tools/registry.py << 'EOF'
import json
from typing import List, Dict, Any

class ToolRegistry:
    """
    Central registry for all agent tools.
    Enables 'Tool Search' pattern to reduce context usage.
    """
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, tool_def: Dict[str, Any]):
        """Register a tool definition."""
        self._tools[tool_def["name"]] = tool_def

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for tools by name or description.
        Used by agents to find capabilities on-demand.
        """
        query = query.lower()
        results = []
        for name, tool in self._tools.items():
            if query in name.lower() or query in tool.get("description", "").lower():
                results.append(tool)
        return results[:5]  # Limit to top 5 to save context

    def get_tool(self, name: str) -> Dict[str, Any]:
        return self._tools.get(name)

# Global registry instance
registry = ToolRegistry()

# --- Tool Definitions with Few-Shot Examples (Pattern 3) ---

registry.register({
    "name": "search_customer_orders",
    "description": "Search for customer orders by date range, status, or total amount.",
    "input_schema": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["pending", "shipped", "delivered"]},
            "date_range": {"type": "string"},
            "min_amount": {"type": "number"}
        }
    },
    "examples": [
        {
            "input": { "status": "shipped", "date_range": "last_30_days" },
            "output": "[{'id': 'ord_123', 'total': 150.00, 'status': 'shipped'}]"
        }
    ]
})

registry.register({
    "name": "check_budget_compliance",
    "description": "Check if a department or user is within budget limits.",
    "input_schema": {
        "type": "object",
        "properties": {
            "department": {"type": "string"},
            "quarter": {"type": "string"}
        },
        "required": ["department"]
    },
    "examples": [
        {
            "input": { "department": "engineering", "quarter": "Q3" },
            "output": "{'compliant': False, 'overage': 5000.00}"
        }
    ]
})
EOF

# 2. Update Base Agent to Support Tool Search & PTC
# ------------------------------------------------------------------------------
echo "🧠 Updating Base Agent (src/ShadowTag-v2/agents/base.py)..."
mkdir -p src/ShadowTag-v2/agents

cat > src/ShadowTag-v2/agents/base.py << 'EOF'
from src.ShadowTag-v2.tools.registry import registry

class AntigravityAgent:
    """
    Base agent class supporting Advanced Tool Use patterns.
    """
    def __init__(self, name: str, model: str = "claude-3-5-sonnet-20241022"):
        self.name = name
        self.model = model
        # Pattern 1: Load ONLY the search tool initially
        self.tools = [self._get_search_tool_def()]

    def _get_search_tool_def(self):
        return {
            "name": "search_tools",
            "description": "Search for available tools to perform tasks. Use this when you don't have a specific tool loaded.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for tool capabilities"}
                },
                "required": ["query"]
            }
        }

    def execute_tool_search(self, query: str):
        """Execute the search and load found tools into context."""
        found_tools = registry.search(query)
        # Dynamically add found tools to the agent's active toolset
        for tool in found_tools:
            if tool not in self.tools:
                self.tools.append(tool)
        return f"Found and loaded {len(found_tools)} tools: {[t['name'] for t in found_tools]}"

    # Pattern 2: Programmatic Tool Calling (Placeholder)
    # In a real implementation, this would execute the Python script generated by Claude
    def execute_python_orchestration(self, script: str):
        """
        Executes a Python script that orchestrates multiple tool calls.
        This keeps intermediate data out of the LLM context.
        """
        # Security Warning: This requires a sandboxed environment (e.g., E2B, Docker)
        # For demo purposes, we just print the script.
        print(f"--- Executing Orchestration Script ---\n{script}\n--------------------------------------")
        return "Script execution simulated. (Implement sandbox for production)"
EOF

# 3. Create a Demo Script to Verify Implementation
# ------------------------------------------------------------------------------
echo "🧪 Creating Verification Script (scripts/verify_advanced_tools.py)..."

cat > scripts/verify_advanced_tools.py << 'EOF'
from src.ShadowTag-v2.tools.registry import registry
from src.ShadowTag-v2.agents.base import AntigravityAgent

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
    current_tool_names = [t['name'] for t in agent.tools]
    if "check_budget_compliance" in current_tool_names:
        print("✅ Dynamic Tool Loading: OK")
    else:
        print("❌ Dynamic Tool Loading failed")

if __name__ == "__main__":
    main()
EOF

# 4. Finalize
# ------------------------------------------------------------------------------
chmod +x scripts/verify_advanced_tools.py
echo "✨ Implementation Complete!"
echo "Run 'python3 scripts/verify_advanced_tools.py' to verify."
