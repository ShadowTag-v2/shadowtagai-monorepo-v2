---
name: "mcp-googleworkspace"
description: "Native Google Workspace integration. Replaces Slack/Notion MCPs for secure corporate messaging and persistent documentation."
---

# MCP: Google Workspace Server (Native Skill)

## Goal
Use Google Chat and Google Docs natively to communicate with the user and store artifacts safely inside the sovereign environment instead of relying on external tools.

## Rules of Engagement (COR.30 Compliance)
1. **Google Native:** Any request to document external features or notify external team members must pipe through Google Chat/Docs APIs using `googleworkspace/cli`.
2. **PII Sanitization:** Even internal workspaces must obey PII constraints. Scrub identifiable tokens before syncing architecture documents (like PR summaries).
