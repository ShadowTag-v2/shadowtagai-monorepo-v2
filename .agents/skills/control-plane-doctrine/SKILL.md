---
name: control-plane-doctrine
description: Enforces the 5-pillar Antigravity Control Plane architecture across all agent sessions. Ensures VS Code stabilization, agent loop hardening, remote compute routing, observability, and reversibility.
---

# Control Plane Doctrine — Enforcement Skill

## Purpose

This skill enforces the Antigravity Control Plane architecture (v2.0) across all agent sessions.
It is the behavioral enforcement layer for `docs/ANTIGRAVITY_CONTROL_PLANE.md`.

## Trigger

This skill activates at **every session start** and is referenced by:
- `docs/ANTIGRAVITY_CONTROL_PLANE.md`
- `docs/AGENT_LOOP_HARDENING.md`
- `docs/OBSERVABILITY_PROTOCOL.md`

## Pre-Session Checklist

Before ANY work begins, execute these checks IN ORDER:

### 1. Temporal Anchor
```bash
git log -n 1 --format="%H %s"
git status --porcelain | wc -l
```
- Confirm HEAD commit hash
- Confirm working tree cleanliness (0 = clean)

### 2. MCP Fleet Health
Verify all 5 MCP servers are operational:
- `list_pages` → chrome-devtools-mcp
- `firebase_get_environment` → firebase-mcp-server
- `list_projects` → StitchMCP
- `search_documents` (test query) → google-developer-knowledge
- `sequentialthinking` (test thought) → sequential-thinking

If ANY server is DOWN: log to `.beads/issues.jsonl` and attempt self-healing before proceeding.

### 3. Auth Verification
Check relevant auth channels:
- GitHub: SSH key loaded (`ssh -T git@github.com`)
- Firebase CLI: `firebase login:list` (if deploying)
- GCP ADC: `gcloud auth list` (if using GCP services)

### 4. KI Review
- Scan KI summaries for patterns relevant to the current task
- Read any relevant KI artifacts before starting work
- NEVER reinvent what's already documented

## During-Session Enforcement

### File Modifications
After EVERY file write:
1. Re-read the file to confirm content
2. Run appropriate linter (`ruff` for Python, `biome` for TS/JS)
3. If lint regression: `git checkout -- <file>` and retry

### MCP Routing
Before EVERY tool call:
- Verify the operation can't be done by an MCP server
- If it can: USE the MCP server, not a terminal command
- Log any routing violations to `.beads/issues.jsonl`

### Anti-Theater
Before EVERY success claim:
- Verify file existence with `view_file` or `list_dir`
- Verify command success with exit code check
- Verify deploy success with live URL check via chrome-devtools-mcp
- NEVER claim success based on assumption

## Post-Session Protocol

### State Report
At session end, report:
- Files created/modified/archived
- Commands executed and their outcomes
- MCP servers used
- Any issues logged to `.beads/issues.jsonl`
- Pending tasks for next session

### Commit Convention
```
<type>(<scope>): <description>
```
Types: feat, fix, chore, docs, refactor, test, ci, perf

## Prohibited Actions

<!-- GUARDRAIL: These destructive patterns are documented as anti-patterns. Actual execution requires STATE B authentication per ToolGateway. See ISSUE-018/019. -->
| Action | Reason | Alternative |
|--------|--------|-------------|
| `rm -rf` | RULE 00 | `mv` to `archive/` |
| `git reset --hard` | Destroys history | `git checkout -- <file>` |
| `search_web` for Google docs | MCP available | `google-developer-knowledge` |
| `npx firebase-tools` | Token loss | Global `firebase-tools` |
| Asking user to check UI | Meatbridge eviction | `chrome-devtools-mcp` |
| Guessing API endpoints | Physical barrier | `google-developer-knowledge` |
| Writing SQL from memory | Physical barrier | Query live schema first |
| `generate_image` | TACSOP 7 ban | Stitch MCP or CSS/SVG |

## Truth Hierarchy

When in doubt, consult in this order:
1. `monorepo_manifest.yaml` (workspace truth)
2. `AGENTS.md` (agent behavior truth)
3. `antigravity-mcp-config.json` (MCP truth)
4. `BUSINESS_CONTEXT_LOCKED.md` (pricing truth)
5. `RISK_REGISTER.md` (risk truth)

## References

- `docs/ANTIGRAVITY_CONTROL_PLANE.md` — Full control plane specification
- `docs/AGENT_LOOP_HARDENING.md` — Anti-theater protocol
- `docs/OBSERVABILITY_PROTOCOL.md` — Monitoring and audit trail
- `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md` — Non-destruction law
- `.agents/skills/mcp-fleet-vanguard/SKILL.md` — MCP health monitoring
