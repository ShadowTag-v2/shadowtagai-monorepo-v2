# Advanced Tool Use Implementation Guide

**Source**: [Anthropic Engineering - Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)
**Context**: Applied to `ShadowTag-v2-fastapi-services` Agent Ecosystem
**Benchmark**: [Puzzle Room Challenge](demos/puzzle_room_challenge.md) - Validation Protocol

## Overview

This guide outlines how to implement Anthropic's advanced tool use patterns—**Tool Search**, **Programmatic Tool Calling (PTC)**, and **Tool Use Examples**—to optimize token usage, improve accuracy, and enable complex orchestration within the `ShadowTag-v2` agent swarm.

## 1. Tool Search (Dynamic Tool Loading)

**Problem**: Loading all tool definitions upfront (e.g., GitHub, Slack, Jira) consumes massive context (50k+ tokens), reducing space for reasoning and increasing costs.
**Solution**: Load only a "Tool Search" tool initially. Claude uses it to find and load specific tools on-demand.

### Implementation Strategy for `ShadowTag-v2` (Tool Search)

For agents like `swarm_boss.py` or `atomic_chat_manager.py` that have access to many tools:

1. **Define a `search_tools` tool**:

    ```python
    def search_tools(query: str):
        """
        Search for available tools by name or description.
        Returns: List of matching tool definitions (JSON schemas).
        """
        # Logic to search your tool registry
        pass
    ```

2. **Initial Context**:
    - Provide *only* `search_tools` and maybe 3-5 critical "always-on" tools in the initial system prompt/tool list.
    - Instruct Claude: "You have access to a vast library of tools. Use `search_tools` to find capabilities for [Task X, Y, Z]."

3. **Token Savings**:
    - **Traditional**: 50+ tools ~ 55k tokens.
    - **With Tool Search**: ~500 tokens (search tool) + ~3k tokens (loaded tools). **~90% reduction**.

## 2. Programmatic Tool Calling (PTC)

**Problem**: Complex tasks (e.g., "check budget for all 20 employees") require many round-trips. Intermediate results (2,000+ line items) bloat context and confuse the model.
**Solution**: Claude writes a Python script to orchestrate tool calls, process data, and return only the final result.

### Implementation Strategy for `ShadowTag-v2` (PTC)

For complex analysis agents (`judge6`, `financial_analyst`):

1. **Enable Code Execution**: Ensure the agent has a `run_python` or `execute_code` tool.
2. **Prompt Engineering**:
    - "Write a Python script to orchestrate this task. Use the available tools `get_X`, `get_Y` within your script to fetch data, process it, and print the final answer."
    - **Crucial**: The tools must be callable from the Python sandbox (or mocked/proxied).

3. **Example Workflow (Budget Check)**:
    - **Bad**: Call `get_expenses` 20 times, put all JSON in context, ask Claude to sum.
    - **Good (PTC)**: Claude writes:

      ```python
      employees = get_employees()
      for emp in employees:
          expenses = get_expenses(emp.id)
          if sum(e.amount for e in expenses) > budget:
              print(f"{emp.name} over budget")
      ```

    - **Result**: Only the printed output enters context. **~95% token reduction** for data-heavy tasks.

## 3. Tool Use Examples (Few-Shot Prompting)

**Problem**: Models often hallucinate parameters or use wrong formats (e.g., `notification-send-user` vs `notification-send-channel`).
**Solution**: Embed 1-5 concise, realistic examples *inside* the tool definition.

### Implementation Strategy for `ShadowTag-v2` (Examples)

Update tool definitions in `src/ShadowTag-v2/tools/` or `agents/`:

```json
{
  "name": "search_customer_orders",
  "description": "Search for orders. Returns order details.",
  "input_schema": { ... },
  "examples": [
    {
      "input": { "status": "shipped", "date_range": "last_30_days" },
      "output": "[List of 5 order objects...]"
    }
  ]
}
```

**Best Practices**:

- **Realism**: Use real-looking data (e.g., "New York", "$12.50"), not "string" or "value".
- **Variety**: Show minimal vs. full parameter usage.
- **Focus**: Only add examples for ambiguous cases.

## Integration Checklist

- [ ] **Audit Agents**: Identify agents with >20 tools (Candidates for Tool Search).
- [ ] **Identify Data Heavy Tasks**: Find workflows with large intermediate data (Candidates for PTC).
- [ ] **Refine Definitions**: Add examples to tools with high error rates.