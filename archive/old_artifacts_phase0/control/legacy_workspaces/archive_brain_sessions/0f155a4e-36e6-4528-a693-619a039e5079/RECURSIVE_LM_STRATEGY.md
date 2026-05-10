# Recursive Language Models (RLM) & Antigravity IDE
**Doc ID:** Cor.58.7-RLM-STRATEGY
**Version:** 1.0 (Gold Master)
**Date:** Feb 2, 2026
**Source:** "Cor.Recursive Language Models" (User Directive)

## 1. Executive Summary: The Death of RAG (as we know it)
We are shifting from static Vector Search (which fails on structural queries) to **Recursive Language Models (RLM)**.
*   **Concept**: Treat a document as a navigable environment (like a game world).
*   **Mechanism**: The agent "jumps" to chapters, reads chunks, and recursively spawns sub-agents to solve deeply nested queries.
*   **Kill Shot**: Context-agnostic processing of 100MB+ files using standard context windows.

## 2. The Algorithm: Recursive Navigation
Instead of `similarity_search(query)`, we do `agent.solve(query)`:
1.  **Observe**: Read current text chunk (e.g., Table of Contents).
2.  **Decide**: `JUMP` to chapter, `READ_NEXT`, or `RECURSE`.
3.  **Recurse**: If a sub-topic is found ("See Appendix B for pricing"), spawn a sub-agent to navigate Appendix B and return the answer.

## 3. The "Antigravity" IDE (VS Code God Mode)
To build this, we replicate Google's "Cider" environment using VS Code + Gemini 1.5 Pro.
*   **Stack**: `uv` (Package Manager), `ruff` (Linter), `Gemini Code Assist` (Context).
*   **Context Strategy**: "Context-First" Monorepo. Gemini loads the entire architecture (`libs/`, `apps/`, `config`) into memory.

### Configuration (`.vscode/settings.json`)
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.extraPaths": ["${workspaceFolder}/libs/auth/src", ...],
  "[python]": { "editor.defaultFormatter": "charliermarsh.ruff", "editor.formatOnSave": true },
  "gemini.context.includeWorkspace": true,
  "editor.inlineSuggest.enabled": true
}
```

## 4. Implementation Plan
1.  **Code**: `apps/shadowtagai/core/recursive_agent.py` (The RLM implementation).
2.  **IDE**: Update `.vscode/settings.json` and `tasks.json` with the Antigravity config.
3.  **Integration**: Use RLM for "Deep Search" features in the Judge6 Premium dashboard.
