# Puzzle Room Challenge: Advanced Tool Use Benchmark

**Source**: Anthropic Engineering Demo
**Context**: Validation Protocol for `ShadowTag-v2` Agent Efficiency

## Overview

The "Puzzle Room Challenge" is a standardized benchmark to demonstrate the efficiency gains of **Advanced Tool Use** (Tool Search + Programmatic Tool Calling). It simulates a vault with 7+ encoded locks requiring dynamic reasoning, code execution, and tool discovery.

**Benchmark Goal**: Prove that intelligent tool orchestration (Opus 4.5 + Tools) is **~7x cheaper** and **~10x more token-efficient** than brute-force reasoning (Sonnet 4.5 baseline).

## Protocol: Replicating the Challenge

### 1. Setup

- **Platform**: [claude.ai](https://claude.ai) (Pro/Team) or API.
- **Model**: Claude 3.5 Sonnet (Baseline) vs. Claude 4.5 Opus (Efficient).
- **Feature**: Enable "Advanced tool use" (Beta).

### 2. The Prompt

```text
Run the Puzzle Room Challenge demo. Open the vault door by solving all locks (e.g., math codes, key patterns). Use advanced tools proactively. Show real-time token usage and cost estimates.
```

### 3. Expected Metrics (Target vs Baseline)

| Metric | Baseline (Sonnet 4.5 / No Tools) | Target (Opus 4.5 / Advanced Tools) | Improvement |
|--------|----------------------------------|------------------------------------|-------------|
| **Total Tokens** | ~7.6M - 10M | ~663k | **~91-93% Reduction** |
| **Cost** | ~$4.22 - $9.95 | ~$0.95 | **~7x Cheaper** |
| **Context Load** | High (bloated with reasoning) | Low (<10% window used) | **High Efficiency** |
| **Method** | Brute-force natural language | Dynamic Tool Search + Python Orchestration | **Precision** |

## Implementation in `ShadowTag-v2`

We can adapt this challenge to validate our `AntigravityAgent`:

### 1. The "Locks" (Tasks)

Create a script `scripts/benchmark_puzzle.py` that initializes an `AntigravityAgent` and challenges it with:

1. **Lock 1 (Math)**: "Calculate the 50th Fibonacci number." (Requires Code Execution)
2. **Lock 2 (Search)**: "Find the specific tool for 'decoding rot13' and use it." (Requires Tool Search)
3. **Lock 3 (Data)**: "Process this 10k item JSON list to find the anomaly." (Requires PTC)

### 2. Validation

Run the agent against these tasks and measure:

- **Token Usage**: Did `search_tools` prevent loading unused tools?
- **Context Size**: Did `execute_python_orchestration` keep the 10k items out of context?

## API Implementation Reference

(For custom benchmarking via `src/ShadowTag-v2/agents/base.py`)

```python
import anthropic

client = anthropic.Anthropic(api_key="your_api_key_here")

tools = [
    {
        "type": "tool_search_tool_regex_20251119",
        "name": "tool_search_tool_regex",
    },
    {
        "type": "code_execution_20250825",
        "name": "code_execution",
        "description": "Python interpreter for math/code puzzles",
        "input_schema": {"type": "object", "properties": {"code": {"type": "string"}}},
        "defer_loading": True,  # Loads on-demand to save tokens
        "allowed_callers": ["code_execution_20250825"],  # Enables programmatic calling
        "input_examples": [
            {"code": "print(2 + 2)"},
            {"code": "import math; math.sqrt(16)"}
        ]
    }
]

# ... (See full implementation in src/ShadowTag-v2/agents/base.py)
```
