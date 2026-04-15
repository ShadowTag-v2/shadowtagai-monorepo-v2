---
name: mcp-fleet-vanguard
description: "Verifies all MCP servers are installed, operational, and used on each tool call. Prevents raw terminal fallbacks. Self-healing loop for crashed servers. Use at session start and before EACH tool call involving Firebase, browser devtools, Stitch design, or developer knowledge."
---

# MCP Fleet Vanguard (v10.0)

Enforces strict "Zero-Blind Execution" rules. Design operations, Firebase deployments, browser testing, and knowledge lookups route EXCLUSIVELY through the MCP fleet — never raw bash fallbacks.

## When to Use

- At the start of any conversation or new task
- **Before EACH tool call** involving Firebase, browser devtools, design tokens, screen generation, or SDK documentation
- Whenever a terminal command fails or an MCP server appears crashed

## Pre-flight Integrity Check (5-Server Fleet)

Before proceeding, verify the MCP fleet is installed, ONLINE, and prioritized:

| # | Server | Transport | Tools | Purpose | Status |
|---|--------|-----------|-------|---------|--------|
| 1 | `StitchMCP` | Remote (mcp-remote → stitch.googleapis.com) | ~12 | Design tokens, screen generation, UI structure, brand assets | verify |
| 2 | `chrome-devtools-mcp` | Local (npx) | ~25 | Browser inspection, DOM queries, console, network, screenshots | verify |
| 3 | `firebase-mcp-server` | Local (npx) | ~45 | Hosting, Auth, Storage, Functions, Firestore, App Hosting | verify |
| 4 | `google-developer-knowledge` | Remote (mcp-remote → developerknowledge.googleapis.com) | ~3 | SDK docs, API references, developer knowledge | verify |
| 5 | `sequential-thinking` | Local (npx) | ~1 | Formal step-by-step reasoning for multi-step decisions | verify |

**Total budget:** ~86 tools (under 100 ceiling)

**Canonical config:** `~/.gemini/antigravity/mcp_config.json` (editor runtime)
**Mirror:** `antigravity-mcp-config.json` (repo truth)

### CRITICAL: npx PATH Fix

All `command` entries MUST use the absolute nvm path:
```
/Users/pikeymickey/.nvm/versions/node/v24.14.1/bin/npx
```
Bare `npx` WILL FAIL with `exec: "npx": executable file not found in $PATH`.

Every server entry MUST include:
```json
"env": {
  "PATH": "/Users/pikeymickey/.nvm/versions/node/v24.14.1/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
  "HOME": "/Users/pikeymickey"
}
```

## Strict Routing Rules (MANDATORY)

### Design & Media — Use `StitchMCP`

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Pull design tokens | Hand-code colors/fonts | StitchMCP: extract design context |
| Generate screens | Manual HTML/CSS from memory | StitchMCP: `generate_screen_from_text` |
| Edit designs | Rewrite entire files | StitchMCP: `edit_screens` |
| Create projects | Manual setup | StitchMCP: `create_project` |
| Generate variants | Copy-paste iterations | StitchMCP: `variants` with creative range |
| Design systems | Invent token values | StitchMCP: `createDesignSystem` / `listDesignSystems` |

### Firebase & Hosting — Use `firebase-mcp-server`

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Deploy hosting | `bash: firebase deploy --only hosting` | Firebase MCP: deploy hosting tool |
| Init project | `bash: firebase init` | Firebase MCP: initialize tool |
| List projects | `bash: firebase projects:list` | Firebase MCP: list projects tool |
| Firestore rules | `bash: firebase deploy --only firestore:rules` | Firebase MCP: deploy rules tool |
| Auth config | `bash: firebase auth:export` | Firebase MCP: auth management tools |

### Browser Testing — Use `chrome-devtools-mcp`

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Take screenshots | External tools | Chrome DevTools MCP: `take_screenshot` |
| Inspect DOM | Manual curl/wget | Chrome DevTools MCP: DOM query tools |
| Read console | Guess errors | Chrome DevTools MCP: console tools |
| Navigate pages | Manual browser | Chrome DevTools MCP: `new_page` / navigation |

### Developer Knowledge — Use `google-developer-knowledge`

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Look up API docs | `search_web` for Google API docs | Dev Knowledge MCP: `search_documents` |
| Check SDK methods | Guessing from memory | Dev Knowledge MCP: `get_documents` |
| Verify model specs | Web search for Gemini model info | Dev Knowledge MCP: model information |

## The Self-Healing Loop

If any server is dead, missing, or unresponsive:

1. **HALT** — do NOT report failure or proceed with workaround
2. Check `~/.gemini/antigravity/mcp_config.json` for the server entry
3. Verify the `command` uses absolute nvm path (not bare `npx`)
4. Verify `env.PATH` includes `/Users/pikeymickey/.nvm/versions/node/v24.14.1/bin`
5. For remote servers (StitchMCP, google-developer-knowledge): verify API key in args
6. Re-verify against the fleet table above
7. Only then proceed with the original task

## Terminal Commands — When They ARE Allowed

| Operation | Tool | Reason |
|-----------|------|--------|
| `git add/commit/push/pull` | `run_command` | Local git, not GitHub API |
| `python3 scripts/*.py` | `run_command` | Local script execution |
| `pytest / go test` | `run_command` | Local test runners |
| `ruff / vulture` | `run_command` | Local linting |
| `brew install` | `run_command` | System package management |
| File editing | `write_to_file` / `replace_file_content` | IDE-native tools |

## Design Workflow (Cor.Build via Stitch)

The correct pipeline for all UI/visual work:

```
StitchMCP: create_project
  → StitchMCP: generate_screen_from_text (full page design)
  → StitchMCP: edit_screens (iterate on design)
  → StitchMCP: get_screen → download HTML
  → Chrome DevTools MCP: test in browser
  → Firebase MCP: deploy to hosting
```

## Stitch SDK Reference

Cloned to: `.stitch-sdk/` in monorepo root
NPM package: `@google/stitch-sdk`
MCP endpoint: `https://stitch.googleapis.com/mcp`

Key tools:
- `create_project` — Create a new Stitch project
- `generate_screen_from_text` — Generate UI screen from prompt
- `edit_screens` — Edit existing screen with prompt
- `get_screen` — Retrieve screen HTML + screenshot
- `list_projects` — List all projects
- `createDesignSystem` — Create design system tokens
- `listDesignSystems` — List design systems
- `variants` — Generate design variants with creative range

## 100-Tool Ceiling Management

The Antigravity editor enforces a **hard 100-tool limit** across all connected MCP servers.

Current allocation:
| Server | Tools | Notes |
|--------|-------|-------|
| StitchMCP | ~12 | Design generation |
| chrome-devtools-mcp | ~25 | Browser testing |
| firebase-mcp-server | ~45 | Full Firebase suite |
| google-developer-knowledge | ~3 | Doc search |
| sequential-thinking | ~1 | Reasoning |
| **Total** | **~86** | **14 tools headroom** |

To add more servers, use `disabledTools` array in the config to selectively disable unused tools from existing servers.
