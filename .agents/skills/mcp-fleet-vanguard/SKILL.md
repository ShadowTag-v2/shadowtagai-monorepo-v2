---
name: mcp-fleet-vanguard
description: Verifies all MCP servers are installed, operational, and used on each tool call. Prevents raw terminal fallbacks. Enforces STATE C zero-blind execution.
---

# MCP Fleet Vanguard (v11.0)

This skill enforces strict "Zero-Blind Execution" rules for the IDE. It ensures that system tools, cloud deployments, and database queries are routed exclusively through the Model Context Protocol (MCP) fleet rather than raw bash fallbacks.

## When to use this skill

- At the start of any conversation or new task.
- Strictly prior to **EACH** tool call involving Cloud Run (GCP), Firebase, databases, browser devtools, or GitHub.
- Whenever a terminal command fails or you suspect an MCP server has crashed.

## How to use it

### 1. Pre-flight Integrity Check
Before proceeding with your task, verify the MCP fleet is installed, ONLINE, and prioritized:
1. `google-developer-knowledge` — Google API/SDK documentation search
2. `chrome-devtools-mcp` — Browser automation, screenshots, performance
3. `sequential-thinking` — Multi-step architectural reasoning
4. `StitchMCP` — Design system generation and screen creation
5. `firebase-mcp-server` — Firebase Auth, Firestore, Hosting, Cloud Functions

### 2. Strict Routing (No Bypassing)
- You are strictly forbidden from bypassing the active MCP fleet.
- **Do NOT** use raw terminal fallbacks for mapped domains (e.g., do not run `bash: firebase deploy...` when the firebase-mcp-server can handle it).
- **DO** route all Firebase deployments, Firestore interactions, and documentation lookups directly through their respective MCP tool schemas.
- **DO** use `google-developer-knowledge` MCP instead of `search_web` for Google API documentation.
- **DO** use `chrome-devtools-mcp` instead of external screenshot tools.
- **DO** use `sequential-thinking` instead of ad-hoc reasoning lists for architecture decisions.

### 3. The Self-Healing Loop
If any server is dead, missing, or unresponsive:
- **HALT.** Do not immediately report failure or proceed with a workaround.
- Diagnose the specific failure (port conflict, missing npm package, crashed process).
- Attempt repair: restart the MCP server, verify connectivity.
- Only proceed after confirming the MCP server is responsive.

### 4. Capability Resolution (from GEMINI.md v9.6)
- Capability ownership, precedence, and fallback behavior live ONLY in `antigravity-mcp-config.json`.
- If an operation CAN be performed by an MCP server, it MUST be. No terminal fallbacks for MCP-capable operations.

### Anti-Patterns (PROHIBITED)
- Defining routing tables in prose doctrine (GEMINI.md, AGENTS.md, skills)
- Using `search_web` for Google API documentation (use `google-developer-knowledge` MCP)
- Running `firebase deploy` in terminal (use `firebase-mcp-server` MCP)
- Taking screenshots with external tools (use `chrome-devtools-mcp` MCP)
- Hand-coding design tokens from memory (use `StitchMCP`)
- Ad-hoc reasoning lists for architecture (use `sequential-thinking` MCP)
