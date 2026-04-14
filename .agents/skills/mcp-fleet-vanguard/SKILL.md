---
name: mcp-fleet-vanguard
description: "Verifies all MCP servers are installed, operational, and used on each tool call. Prevents raw terminal fallbacks. Self-healing loop for crashed servers. Use at session start and before EACH tool call involving Cloud Run, Firebase, databases, browser devtools, or GitHub."
---

# MCP Fleet Vanguard (v8.4)

Enforces strict "Zero-Blind Execution" rules. System tools, cloud deployments, and database queries route EXCLUSIVELY through the MCP fleet — never raw bash fallbacks.

## When to Use

- At the start of any conversation or new task
- **Before EACH tool call** involving Cloud Run (GCP), Firebase, databases, browser devtools, or GitHub
- Whenever a terminal command fails or an MCP server appears crashed

## Pre-flight Integrity Check

Before proceeding, verify the MCP fleet is installed, ONLINE, and prioritized:

| # | Server | Package | Status |
|---|--------|---------|--------|
| 1 | google-developer-knowledge | `@anthropic/developer-knowledge-mcp` | verify |
| 2 | mcp-toolbox-sdk-java | `@anthropic/mcp-toolbox-sdk-java` | verify |
| 3 | chrome-devtools-mcp | `npx -y chrome-devtools-mcp` | verify |
| 4 | github-mcp | `npx -y @anthropic/github-mcp` | verify |
| 5 | sequential-thinking | `npx -y @anthropic/sequential-thinking-mcp` | verify |
| 6 | stitch | Google Stitch MCP | verify |
| 7 | dart-mcp-server | `npx -y dart-mcp-server` | verify |
| 8 | firebase | `npx -y firebase-tools@latest mcp` | verify |
| 9 | gcloud-mcp | `npx -y @google-cloud/gcloud-mcp` | verify |

**Canonical config:** `antigravity-mcp-config.json`

## Strict Routing (No Bypassing)

- **FORBIDDEN** from bypassing the active MCP fleet
- **DO NOT** use raw terminal fallbacks for mapped domains:
  - ❌ `bash: gcloud run deploy...`
  - ❌ `bash: firebase deploy...`
  - ❌ `bash: psql ...`
- **DO** route all cloud deployments, Cloud Run services, Firestore interactions, and database queries through their respective MCP tool schemas

### Exception: When MCP is genuinely unavailable
If an MCP server is confirmed dead after self-healing attempts, document the fallback in `.beads/issues.jsonl` and proceed with terminal commands as last resort.

## The Self-Healing Loop

If any server is dead, missing, or unresponsive:

1. **HALT** — do NOT report failure or proceed with workaround
2. Drop into shell and repair:
   ```bash
   npm i -g @google-cloud/gcloud-mcp
   npm i -g firebase-tools
   ```
3. Spin the server up and verify PID/status
4. Re-verify against the fleet table above
5. Only then proceed with the original task

## MCP Database Architecture Protocol

ALL database interactions MUST be natively routed through the generic MCP tool ecosystem (e.g., `db-architect` skill). **DO NOT** hardcode ORM connection strings.

## Infrastructure Ports

| Service | Port | Status |
|---------|------|--------|
| Temporal Server | 7233+8233 | verify |
| Chrome Debug | 9222 | verify |
| BCI Intent Daemon | ws://127.0.0.1:9090 | verify |
| Volatile-Nova Telemetry | 127.0.0.1:8000 | verify |
