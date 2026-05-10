---
name: "mcp-filesystem"
description: "Native Filesystem API wrapper. Filters all raw open/write operations through the Judge #6 structural gate before disk access."
---

# MCP: Filesystem Server (Native Skill)

## Goal
Secure read/write operations against arbitrary path traversal attacks or destructive shell instructions.

## Rules of Engagement (COR.30 Compliance)
1. **Absolute Paths Only:** Agents must resolve filesystem paths fully using the `.gemini/antigravity` root structure.
2. **Gate 0 Verification:** Do not invoke `write_to_file` on `css/tsx/jsx` files containing direct hardcoded colors or sizing margins. Rely on the `design_police_linter.py` checks mentally before executing standard edits.
3. **Workspace Locking:** Write operations outside the defined `Monorepo-Uphillsnowball` boundary are heavily strictly prohibited unless explicitly escalated to the user via prompt.
