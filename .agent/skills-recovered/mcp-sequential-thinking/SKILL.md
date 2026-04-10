---
name: "mcp-sequential-thinking"
description: "Native Antigravity implementation of the Formal Reasoning process. Replaces the node-based sequential-thinking MCP server with an internal deterministic logic execution path."
---

# MCP: Sequential Thinking (Native Skill)

## Goal
To enforce a structured sequence of analysis prior to executing code changes, preventing hallucination through "vibe coding".

## Rules of Engagement (COR.30 Compliance)
1. **Mandatory Tracing:** Before utilizing the `filesystem` skill, the agent MUST explicitly trace its execution path.
2. **If-Then Graphing:** Map out the exact logic blocks: `PREMISE` -> `CLAIM` -> `PREDICTION`.
3. **No Execution:** This skill is strictly analytical. No file writes or subprocesses may be triggered while operating under this schema.

## Enforcement
Use this skill whenever a bug fix, schema mutation, or feature addition is requested. Map out the 28-43 step analysis tree in your memory constraints before proceeding with code changes.
