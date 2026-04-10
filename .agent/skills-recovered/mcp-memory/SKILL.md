---
name: "mcp-memory"
description: "Native Key-Value Persistence Layer replacing the open-source memory MCP. Enables secure intra-task state caching across the agent swarm."
---

# MCP: Memory Server (Native Skill)

## Goal
Provide a fast cache for agent hypotheses, token payloads, and verification trees without leaking PII or hitting external RPC bottlenecks.

## Rules of Engagement (COR.30 Compliance)
1. **State Transience:** Memory artifacts must be ephemeral, scoped to the current active session only unless explicitly declared for Long-Term Storage.
2. **No Secret Caching:** Never cache JWTs, API Keys, or user passwords into the Memory store. All DB operations run through encrypted vaults.
3. **Graphing Data:** Store entity/relation/observation mappings formatted as JSON representations locally.

## Usage
If parsing a massive repository, store the hash mappings of previously checked paths using this skill matrix to avoid token redundancy on subsequent executions.
