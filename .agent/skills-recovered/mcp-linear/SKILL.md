---
name: "mcp-linear"
description: "Native Linear issue mapping. Enforces strict task dependency hierarchies."
---

# MCP: Linear Server (Native Skill)

## Goal
Track progress of the generated PR batches and handle issue lifecycles.

## Rules of Engagement (COR.30 Compliance)
1. **Single Source of Truth:** Correlate specific Agent executions directly against active Linear ticket IDs. 
2. **Artifact Mirroring:** Store the completed Markdown tracking logic locally inside the `brain/` while keeping Linear updated with status shifts.
