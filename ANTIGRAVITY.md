---
date: 2026-04-24
tags: [workspace-manual, antigravity, operating-manual]
---

# Antigravity Workspace Operating Manual

> This file defines operating procedures for the [[ShadowTag-v2]] monorepo
> workspace. It is read by agents at session start.

## 1. Memory Retrieval

Before answering questions about project architecture or preferences:
1. Check `.agents/skills/notebooklm-oracle/` for mandatory context retrieval
2. Query the Master Brain notebook: `notebooklm ask "What are the preferences for this project?"`
3. Check `vault/serve/` for cached embeddings

## 2. Research Protocol

All raw research MUST be saved using the [[obsidian-formatter]] skill:
- Files go to the Obsidian vault or `vault/ingest/`
- All markdown uses YAML frontmatter + `[[WikiLinks]]`
- Naming: `Research/YYYY-MM-DD-<topic>.md`

## 3. External Data Ingestion

Follow the [[cor-notebooklm-tacsop]] TACSOP:
1. Route through [[Switchboard]] MCP
2. Quarantine in `vault/quarantine/`
3. Sanitize via [[NotebookLM]] MCP
4. Only clean intelligence enters the agent context

## 4. Reference Libraries

Use tools cloned in `external_repos/`:
- `antigravity-notebooklm-mcp/` — NotebookLM MCP server
- `switchboard/` — Routing firewall

## 5. Deployment

- **Firebase Hosting:** Via Firebase MCP server (never terminal)
- **Cloud Run:** Via `gcloud run deploy` or Cloud Code extension
- **NEVER** use third-party deployment platforms without explicit approval

## 6. Canonical Truth Sources

| Source | Purpose |
|--------|---------|
| `AGENTS.md` | Agent behavioral contract |
| `GEMINI.md` | Operator invariants |
| `monorepo_manifest.yaml` | Workspace structure |
| `antigravity-mcp-config.json` | MCP routing truth |
| `BUSINESS_CONTEXT_LOCKED.md` | Pricing/architecture |
| `RISK_REGISTER.md` | Operational risks |
| `.agents/skills/cor-notebooklm-tacsop/SKILL.md` | Zero-Trust TACSOP |
