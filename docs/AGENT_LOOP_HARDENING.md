# AGENT_LOOP_HARDENING.md

> **Status:** LOCKED — Anti-theater protocol and agent execution integrity enforcement.
>
> **Last updated:** 2026-04-27

---

## Purpose

This document defines the hardening protocols that prevent "agent theater" — the failure mode
where agents claim success without verification, reference files that don't exist, or skip
error handling. Every protocol here is enforced by the control plane, not by trust.

---

## 1. Anti-Theater Checklist

Before reporting success on ANY operation, the agent MUST verify:

### File Operations
- [ ] File exists (verified via `view_file` or `list_dir`)
- [ ] File content matches expected state (verified via `view_file`)
- [ ] No silent write failures (verified via re-read after write)

### Build Operations
- [ ] Command exit code is 0 (checked via `command_status`)
- [ ] No error output in stderr (parsed from command output)
- [ ] Build artifacts exist (verified via `list_dir`)

### Test Operations
- [ ] Test runner completed (checked via `command_status`)
- [ ] Pass/fail counts extracted from output
- [ ] No test regressions vs. baseline (504 collected, 480 passed)

### Deploy Operations
- [ ] Deployment URL is reachable (verified via `chrome-devtools-mcp`)
- [ ] Page content renders correctly (verified via `take_snapshot` or `take_screenshot`)
- [ ] No console errors on live page (verified via `list_console_messages`)
- [ ] Lighthouse scores meet thresholds (verified via `lighthouse_audit`)

### Auth Operations
- [ ] Token is not expired (checked expiry timestamp)
- [ ] Token has required scopes
- [ ] Push succeeds with actual remote acknowledgment (not just local exit code)

---

## 2. MCP-First Enforcement

### Routing Rules

```
IF operation CAN be done by MCP server:
    USE MCP server (mandatory)
ELSE IF operation has a skill:
    USE skill (preferred)
ELSE:
    USE terminal (acceptable)
```

### Routing Table

| Intent | MCP Server | Tool | Terminal Fallback |
|--------|-----------|------|-------------------|
| Google API docs | google-developer-knowledge | search_documents | ❌ NEVER search_web |
| Firebase deploy | firebase-mcp-server | firebase_init + terminal | ❌ NEVER npx firebase |
| DOM inspection | chrome-devtools-mcp | take_snapshot | ❌ NEVER ask user |
| Screenshot | chrome-devtools-mcp | take_screenshot | ❌ NEVER external tool |
| Lighthouse audit | chrome-devtools-mcp | lighthouse_audit | ❌ NEVER npm lighthouse |
| Console errors | chrome-devtools-mcp | list_console_messages | ❌ NEVER ask user |
| Design tokens | StitchMCP | create_design_system | ❌ NEVER hand-code |
| Architecture reasoning | sequential-thinking | sequentialthinking | ❌ NEVER ad-hoc lists |

### Violation Logging

Any MCP routing violation is logged to `.beads/issues.jsonl`:

```json
{
  "ts": "2026-04-27T07:00:00Z",
  "type": "mcp_routing_violation",
  "detail": "Used search_web for Firebase docs instead of google-developer-knowledge",
  "severity": "HIGH"
}
```

---

## 3. Pre-Action Memory Gate

### Sequence (Mandatory Before Every Complex Action)

```
1. CHECK KI summaries for existing patterns
2. VERIFY MCP server health (Fleet Vanguard)
3. ANCHOR temporal state (git log -n 1)
4. CONFIRM auth state (relevant credentials)
5. EXECUTE the action
6. VERIFY the result (anti-theater checklist)
```

### KI Consultation Priority

```
KI artifacts → Conversation logs → Fresh research
```

Never reinvent what's already documented. Always check the knowledge base first.

---

## 4. Post-Edit Validation Loop

### Trigger

After EVERY file modification, regardless of confidence level.

### Python Files

```bash
ruff check --fix <modified_file>
ruff format <modified_file>
```

### TypeScript/JavaScript Files

```bash
biome check --fix <modified_file>
```

### Structural Search (When Applicable)

```bash
ast-grep --pattern '<pattern>' <modified_file>
```

### Failure Recovery

If the validation loop introduces a regression:

1. Immediately revert: `git checkout -- <file>`
2. Re-examine the original edit
3. Apply the fix without the regression
4. Re-run validation

**NEVER** use `git reset --hard` — this is a BANNED command.

---

## 5. Execution Ledger

For operations with >10 checkpoints, maintain a numbered checkpoint ledger:

```
[CP-001] 2026-04-27T07:00:00Z — Git state anchored at ffc1741bd7
[CP-002] 2026-04-27T07:00:05Z — MCP fleet verified (5/5 UP)
[CP-003] 2026-04-27T07:00:10Z — Firebase auth confirmed (expires 07:55)
[CP-004] 2026-04-27T07:00:15Z — Build started (npm run build)
[CP-005] 2026-04-27T07:01:30Z — Build succeeded (exit 0, 0 errors)
...
```

Write the ledger to the active task artifact or `.beads/issues.jsonl`.

---

## 6. Autonomous Navigation Protocol (Meatbridge Eviction)

### Rule

The agent MUST autonomously navigate, interact with, and verify ALL frontend work using:

- `browser_subagent` — Multi-step UI workflows, navigation, form filling, video recording
- `chrome-devtools-mcp` — DOM snapshots, screenshots, console errors, Lighthouse audits

### Prohibited Phrases

These are PROTOCOL VIOLATIONS:

- "Please open localhost and check..."
- "Can you verify the UI for me?"
- "Copy-paste the console errors"
- "Navigate to the website and..."

### Fallbacks

- Shadow DOM / Canvas elements → coordinate-based clicking via `evaluate_script`
- Generative UIs → polling loops (15s images, 30s video)
- File downloads → terminal `mv` from `~/Downloads/`

---

## 7. Headless CLI Protocol

### Problem

Agent terminals lack full PTY attachment. Interactive TUIs (Inquirer.js, bubbletea, gum, fzf)
will trap the agent in infinite loops.

### Mandatory Flags

```bash
export CI=true DEBIAN_FRONTEND=noninteractive
# + --non-interactive, --quiet, --yes/-y when available
```

### Recovery

1. Terminate hung process immediately
2. Retry with `CI=true` + `--non-interactive`
3. If still blocked: write a `pexpect` script
4. If truly interactive (OAuth flow): tell the user the EXACT command to run
5. NEVER commit in a broken state because a CLI blocked you

---

## Cross-References

- [ANTIGRAVITY_CONTROL_PLANE.md](./ANTIGRAVITY_CONTROL_PLANE.md) — Parent control plane spec
- [OBSERVABILITY_PROTOCOL.md](./OBSERVABILITY_PROTOCOL.md) — Monitoring and tracing
- `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md` — Non-destruction law
- `.agents/skills/mcp-fleet-vanguard/SKILL.md` — MCP health monitoring
- `.agents/skills/post-edit-validation-loop/` — Lint enforcement
- `.agents/skills/cor-meatbridge-eviction/SKILL.md` — Autonomous navigation
