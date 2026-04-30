---
name: operator-invariants
description: >
  Mirrors the GEMINI.md v10.4 operator invariants verbatim before any repo-wide action.
  Activates when: session starts, before any commit/push/migration, when the user does NOT
  say MEMORY UNLOCK. Run the pre-action memory gate, then list all active invariants.
---
# Operator Invariants — Pre-Action Memory Gate

## Purpose
This skill surfaces the locked GEMINI.md operator constraints as a discoverable,
enforceable gate before any repo-wide action (commit, push, deploy, migration,
architecture shift). It ensures Antigravity mirrors these invariants before acting.

## When to Use
- At session start (initial invariant acknowledgment)
- Before any `git commit`, `git push`, or `firebase deploy`
- Before any database migration or schema change
- Before any architecture shift spanning >3 packages
- When the user has NOT said `MEMORY UNLOCK`

## Locked Invariants (from GEMINI.md v10.4)

### Canonical Truth Hierarchy
1. `AGENTS.md` is the canonical contract
2. `CLAUDE.md` is a thin shim
3. `monorepo_manifest.yaml` is workspace truth
4. `antigravity-mcp-config.json` is MCP truth
5. `BUSINESS_CONTEXT_LOCKED.md` is pricing and architecture truth
6. `RISK_REGISTER.md` is operational risk truth

### Excluded Destructive Tools (NEVER attempt)
- `ShellTool(rm -rf)`
- `ShellTool(sudo)`

### MCP Fleet Mandate
All 5 MCP servers MUST be used when their capability matches the task:
1. Firebase MCP Server (45 tools)
2. Chrome DevTools MCP (29 tools)
3. StitchMCP (12 tools)
4. Google Developer Knowledge (3 tools)
5. Sequential Thinking (1 tool)

### Capability Resolution
- `GEMINI.md` defines operator invariants ONLY — NOT capability ownership
- Capability ownership lives ONLY in `antigravity-mcp-config.json`
- If an operation CAN be performed by an MCP server, it MUST be
- No terminal fallbacks for MCP-capable operations

### Secrets Doctrine
- Secrets ONLY via GCP Secret Manager for production
- `.env` files are BANNED and DELETED — use `scripts/load_mcp_secrets.sh`
- No hardcoded API keys in source files or committed config
- No secrets in logs, chat messages, or frontend code

### Execution State Machine
- **STATE A (Pure YOLO)**: Repetitive UI, standard logic, known patterns, low-ambiguity
- **STATE B (Clutch)**: Git history rewrites, force-pushes, DB migrations, auth/payment changes, architecture shifts >3 packages

### GitHub Doctrine
- SSH is PRIMARY transport for push/pull
- GitHub App PEM is the ONLY authorized auth path
- `gh auth login` is NEVER used
- Personal access tokens (PATs) are NEVER used

## Pre-Action Checklist
Before any repo-wide action, verify:
- [ ] MCP fleet health (5 servers responsive)
- [ ] No secrets in staged files (`betterleaks` scan)
- [ ] Correct git remote (`git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git`)
- [ ] Execution state classified (STATE A or STATE B)
- [ ] Truth hierarchy respected (no second sources of truth created)
