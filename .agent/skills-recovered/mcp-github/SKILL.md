---
name: "mcp-github"
description: "Native Github Orchestrator. Replaces the broad external Github MCP with strict local CI/CD trigger rules."
---

# MCP: Github Server (Native Skill)

## Goal
Securely interact with the underlying Github repository to execute the God Mode Pushes, retrieve PR states, and handle code diffs without leaking SSH/PEM keys to unstructured output.

## Rules of Engagement (COR.30 Compliance)
1. **PEM Key Isolation:** Standard commit operations must use the local `.git` scope. Any direct API payload interaction must natively leverage `god_mode_push.py` wrapped securely.
2. **Branching:** You merge nothing to `main` without explicit User (Judge #6) authorization.
3. **Commit Formatting:** Follow the `commit-message-format.md` conditionally available when writing commit sequences.
