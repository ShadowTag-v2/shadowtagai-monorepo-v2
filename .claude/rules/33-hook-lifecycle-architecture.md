# Rule 33 — Hook Lifecycle Architecture

Source: `claude-agent-sdk-python` types.py, `everything-claude-code` hooks.json

## 10 SDK Hook Events (Authoritative from Python SDK)

```
PreToolUse          PostToolUse         PostToolUseFailure
UserPromptSubmit    Stop                SubagentStop
PreCompact          Notification        SubagentStart
PermissionRequest
```

### Hook Input Types (SDK-Verified Fields)

Every hook receives `BaseHookInput`:
- `session_id: str`
- `transcript_path: str`
- `cwd: str`
- `permission_mode: str` (optional)

PreToolUse adds: `tool_name`, `tool_input`, `tool_use_id`, `agent_id` (optional), `agent_type` (optional)
PostToolUse adds: `tool_name`, `tool_input`, `tool_response`, `tool_use_id`
PostToolUseFailure adds: `tool_name`, `tool_input`, `tool_use_id`, `error`, `is_interrupt` (optional)
PreCompact adds: `trigger` (Literal["manual", "auto"]), `custom_instructions`
SubagentStart adds: `agent_id`, `agent_type` (required)
SubagentStop adds: `agent_id`, `agent_transcript_path`, `agent_type`, `stop_hook_active`
PermissionRequest adds: `tool_name`, `tool_input`, `permission_suggestions`

### Hook Output Types (SDK-Verified)

PreToolUse output:
- `permissionDecision`: Literal["allow", "deny", "ask"]
- `permissionDecisionReason`: str
- `updatedInput`: dict — allows input mutation before tool execution
- `additionalContext`: str — injected into conversation

PostToolUse output:
- `additionalContext`: str
- `updatedMCPToolOutput`: Any — allows output mutation

Common control:
- `continue_`: bool — stop execution flow
- `suppressOutput`: bool — hide from transcript
- `stopReason`: str — user-facing message when continue=False
- `decision`: Literal["block"] — blocking decision

## 25 Production Hook Patterns (ECC-Verified)

### PreToolUse Hooks (10 patterns)
1. **block-no-verify** — Block `git --no-verify` bypass attempts
2. **auto-tmux-dev** — Auto-start dev servers in tmux sessions
3. **tmux-reminder** — Remind for long-running commands
4. **git-push-reminder** — Review before push
5. **commit-quality** — Lint staged files, validate commit message, detect secrets
6. **doc-file-warning** — Warn about non-standard doc files
7. **suggest-compact** — Strategic compaction suggestions at intervals
8. **observe** — Continuous learning observation (async, 10s timeout)
9. **governance-capture** — Secrets/policy violation capture
10. **config-protection** — Block linter/formatter config weakening

### PostToolUse Hooks (8 patterns)
1. **command-log-audit** — Audit log all bash commands
2. **command-log-cost** — Cost tracking per command
3. **pr-created** — Log PR URL after creation
4. **build-complete** — Async build analysis
5. **quality-gate** — Quality checks after edits (async, 30s)
6. **design-quality-check** — Frontend design drift warning
7. **edit-accumulator** — Record edited files for batch processing at Stop
8. **console-warn** — Warn about console.log statements

### Stop Hooks (5 patterns)
1. **format-typecheck** — Batch Biome/Prettier + tsc on all edited JS/TS (300s timeout)
2. **check-console-log** — Final console.log sweep
3. **session-end** — Persist session state (async)
4. **evaluate-session** — Extract learnable patterns (async)
5. **cost-tracker** — Token/cost metrics summary (async)

### Other Lifecycle Hooks
- **SessionStart** → Bootstrap: load previous context, detect package manager
- **SessionEnd** → Marker: lifecycle marker for observer cleanup
- **PreCompact** → Save state before compaction
- **PostToolUseFailure** → MCP health check, reconnect attempts

## Hook Execution Model

### Sync vs Async
- Sync hooks block tool execution until complete
- Async hooks run in background with timeout (default 10s)
- Stop hooks may have extended timeouts (up to 300s for format+typecheck)

### Flag System (ECC Pattern)
Hooks use a `run-with-flags.js` wrapper with operational modes:
- `minimal` — basic checks only
- `standard` — normal operation
- `strict` — full enforcement

### Permission 3-State Model
```
PermissionBehavior = Literal["allow", "deny", "ask"]
```
This is enforced per-tool via `PermissionEnforcer` (claw-code: 340 LOC):
- `check()` → delegates to `PermissionPolicy::authorize()`
- `check_file_write()` → workspace boundaries + read-only denial
- `check_bash()` → deny mutating commands in read-only mode

## Operational Invariants

1. **No hook may modify CLAUDE.md** — hooks read-only on instruction files
2. **Async hooks MUST have timeout** — prevent resource leaks
3. **Stop hooks run ONCE** — not per-tool, aggregated at response end
4. **PostToolUseFailure triggers MCP health** — automatic reconnection attempts
5. **PreToolUse can mutate input** — `updatedInput` field enables input rewriting
6. **Hook root resolution** — plugin root discovery follows 6-path cascade
