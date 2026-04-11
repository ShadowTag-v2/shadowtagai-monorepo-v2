# .claude/CLAUDE.md — Module-Level Overrides

Follow `AGENTS.md` as the canonical project guide.

## Claude-Specific Rules
- Prefer concise plans over verbose explanations
- Use existing scripts under `scripts/` — do not invent commands
- Re-read files before editing (FileEdit fails silently on stale context)
- After ANY file modification, verify with the project's type-checker
- For tasks touching >5 independent files, launch parallel sub-agents

## Modular Rules
51 modular rules are loaded from `.claude/rules/*.md`:
- 01-verification-loop.md — Employee-grade post-edit verification
- 02-context-death-spiral.md — Compaction triggers at 167K tokens
- 03-senior-dev-override.md — Override "simplest approach" mandate
- 04-sub-agent-swarming.md — Parallel agents, KV cache forking
- 05-file-read-blind-spot.md — 2K line read cap, chunk large files
- 06-tool-result-blindness.md — 50K char truncation to 2K preview
- 07-grep-not-ast.md — Semantic search gaps on renames
- 08-edit-integrity.md — Re-read before/after every edit, absolute paths always (v2.1.97)
- 09-build-pipeline-audit.md — Source map / secrets audit
- 10-cache-and-operations.md — Cache architecture, emotion vector
- 11-compaction-pipeline.md — 4-layer compaction pipeline architecture
- 12-anti-distillation.md — Fake tool injection, client attestation, bypass
- 13-kairos-daemon.md — KAIROS autonomous mode, coordinator, buddy
- 14-architecture-and-leak.md — Terminal rendering, source map leak details
- 15-ultrathink-fastmode.md — Ultrathink keyword, Fast Mode, effort precedence
- 16-feature-flags-env-vars.md — 85+ feature flags, 170+ env vars catalog
- 17-undercover-buddy-hidden.md — Undercover mode, buddy companion, hidden commands
- 18-adversarial-verification.md — Runtime verification, adversarial probes, PASS/FAIL verdicts
- 19-autonomous-security-monitor.md — Block/Allow rules for autonomous actions
- 20-memory-consolidation.md — Dream cycle, v2.1.98 team memory, conservative pruning
- 21-fork-worker-patterns.md — Fork vs fresh agent, cache economics, worker isolation, v2.1.97 metadata
- 22-tool-deferral-cache-scoping.md — Tool schema deferral, cache break detection, prompt split
- 23-bash-security-depth.md — 20-layer bash validator, permission pipeline, CWD persistence
- 24-resilience-patterns.md — Idle watchdog, 529 cascade, SSRF guard, secret scanner
- 25-communication-and-exploration.md — v2.1.98 style, exploratory questions, advisor tool
- 26-managed-agents-lifecycle.md — Managed Agents API lifecycle, SDK routing, event steering (v2.1.97)
- 27-dream-schedule-verify-probes.md — /dream nightly cron, verify skill probes by change type (v2.1.97)
- 28-claudemd-hierarchy.md — 4-location CLAUDE.md loading order, @include directives, layering strategy
- 29-memory-as-hint.md — Memory-as-hint verification protocol, 4-type taxonomy, drift caveat
- 30-cache-economics.md — 14 cache-break vectors, sticky latches, DANGEROUS_uncachedSystemPromptSection
- 31-analyze-before-implement.md — Exploratory analysis-before-implementation protocol (v2.1.98)
- 32-managed-agents-patterns.md — Managed Agents SDK patterns, client patterns, configuration schema
- 33-hook-lifecycle-architecture.md — 10 SDK hook events, 25 ECC production patterns, 3-state permission model
- 34-context-budget-economics.md — SDK ContextUsageResponse, token cost models, compaction decision table
- 35-continuous-learning-instincts.md — Instinct-based learning v2.1, project scoping, confidence scoring
- 36-compact-timing-discipline.md — Compact AFTER milestones/research/debugging, NEVER mid-implementation (Wilbanks)
- 37-sse-streaming-resilience.md — SSE exponential backoff, liveness detection, sequence dedup (SSETransport.ts)
- 38-agent-orchestrator-patterns.md — 8-slot plugin architecture, lifecycle state machine, YAML config (ComposioHQ)
- 39-code-review-pipeline.md — Automated review → fix → verify cycle (CodeRabbit + Superpowers)
- 40-ast-grep-patterns.md — AST structural search over regex for code transforms (ast-grep MCP)
- 41-stack-agnostic-workflows.md — 5 workflow principles: stack-agnostic, question-driven, composable (antigravity-workflows)
- 42-context-window-hygiene.md — Re-read protocol, dead code token burn, degradation signals, sub-agent splitting (iamfakeguru + guanyang)
- 43-multi-agent-coordination.md — Role assignment, handoff protocol, parallel execution mandate, token economics (repowise + OMC)
- 44-edit-safety-self-correction.md — Edit safety, rename/signature change, self-correction loop, evidence standard (iamfakeguru + repowise)
- 45-beads-memory-integration.md — Git-backed memory lifecycle, Find→Read→Remember→Code pattern (akng8 + miqcie)
- 46-system-prompt-architecture.md — Layered prompt architecture, instruction priority hierarchy (repowise + GCP)
- 47-risk-scoring-tool-calls.md — 4-axis risk analysis, composite score actions, model selection (OMC + everything-CC)
- 48-agui-generative-ui-protocol.md — AG-UI event taxonomy, 3-layer architecture, generative UI patterns, multi-agent frontend (ag-ui + CopilotKit + Atmosphere)
- 49-notebooklm-protocol.md — NotebookLM research offloading decision matrix, auth protocol, security constraints
- 50-obsidian-protocol.md — Obsidian vault conventions, wikilinks, frontmatter, knowledge graph hygiene
- 51-pre-agent-protocol.md — Pre-Agent Decision Protocol: NotebookLM diagnostics → Decision Integrity Gate → Execution

## Hook Pipeline (Source-Verified: 3 Types, 27 Events)
Hooks are configured in `.claude/hooks.json`. Three hook types (NOT 5):
- **Command** (`type: 'command'`) — shell scripts
- **Prompt** (`type: 'prompt'`) — single LLM call with configurable model
- **Agent** (`type: 'agent'`) — multi-turn verification agent

### All 27 Lifecycle Events (coreTypes.ts)
```
PreToolUse, PostToolUse, PostToolUseFailure,
Notification, UserPromptSubmit,
SessionStart, SessionEnd,
Stop, StopFailure,
SubagentStart, SubagentStop,
PreCompact, PostCompact,
PermissionRequest, PermissionDenied,
Setup, TeammateIdle,
TaskCreated, TaskCompleted,
Elicitation, ElicitationResult,
ConfigChange,
WorktreeCreate, WorktreeRemove,
InstructionsLoaded, CwdChanged, FileChanged
```

### 10 SDK Hook Events (Python SDK Authoritative — types.py)
```python
HookEvent = Literal[
    "PreToolUse", "PostToolUse", "PostToolUseFailure",
    "UserPromptSubmit", "Stop", "SubagentStop",
    "PreCompact", "Notification", "SubagentStart",
    "PermissionRequest"
]
```

### Active Hooks (21 total — `.claude/hooks.json`)
**PreToolUse (4):**
- PreToolUse(Bash) → validate-bash.py (23 blocking patterns + 50-subcommand mitigation)
- PreToolUse(Write|Edit|MultiEdit) → pre-file-write.sh
- PreToolUse(Write|Edit|MultiEdit) → suggest-compact.js (ECC strategic compaction advisor)
- PreToolUse(*) → observe-instincts.sh (instinct observer — 100% capture)

**PostToolUse (3):**
- PostToolUse(Write|Edit|MultiEdit) → post-file-write.sh (auto-format)
- PostToolUse(Bash) → command-audit-log.sh (JSONL audit trail)
- PostToolUse(*) → observe-instincts.sh (instinct observer — 100% capture)

**PostToolUseFailure (1):**
- PostToolUseFailure(*) → failure-tracker.sh (circuit breaker at 3 failures)

**UserPromptSubmit (1):**
- UserPromptSubmit(*) → prompt-context.py

**PreCompact (1):**
- PreCompact(manual) → pre-compact-state.sh (git state snapshot)

**Stop (3):**
- Stop(*) → stop-quality-gate.sh (tsc + eslint + mypy batch verification)
- Stop(*) → session-cost-tracker.sh (session metrics summary)
- Stop(*) → reactive-compact-sim.py --reset (circuit breaker reset)

**Source-Verified Reactive (3):**
- **InstructionsLoaded** → instructions-loaded.sh (brevity audit + sync)
- **CwdChanged** → cwd-changed.sh (CWD safety + watchPaths registration)
- **FileChanged**(.env|.envrc|tsconfig.json) → file-changed.sh (tsc --noEmit + eslint)

**Unlisted/Planned (2):**
- SessionStart → session-start.sh (context bootstrap)
- Notification → system alerts

### Ant-Grade Verification
`FileChanged` hook + `stop-quality-gate.sh` together provide dual-layer verification:
1. **Real-time**: `FileChanged` runs `tsc --noEmit` + `eslint` on each file change
2. **Batch**: `stop-quality-gate.sh` runs at Stop to catch anything missed
This simulates Anthropic employee verification that prevents false "Done" messages.

### Reactive Compact Simulation (Blocker 4 — RESOLVED)
`reactive-compact-sim.py` reconstructs the reactiveCompact.ts behavior from query.ts:
- Detects 413 (PromptTooLong) + media-size errors
- Withholds errors from user (should_withhold)
- Circuit breaker prevents infinite compaction spiral (hasAttemptedReactiveCompact)
- State persisted to `~/.claude/homunculus/reactive-compact-state.json`
- Auto-reset at session Stop via hook

### Instinct System (Blocker 2 — RESOLVED)
`~/.claude/homunculus/` directory structure initialized with:
- `identity.json` — operator profile, technical level
- `projects.json` — project hash registry
- `config.json` — observer settings, compact timing discipline
- `instincts/{personal,inherited}/` — global instinct storage
- `evolved/{agents,skills,commands}/` — evolved knowledge
- `projects/` — per-project isolated instinct trees
Observer hook (`observe-instincts.sh`) captures 100% of tool use via hooks.json.

## NotebookLM + Obsidian Integration (Phase 4)

### Skills
- `notebooklm-bridge` — Complete NotebookLM API: notebooks, sources, chat, research, artifacts, downloads
- `obsidian-vault-operator` — Vault-native file ops, wikilinks, frontmatter, templates, knowledge graph
- `session-wrap-up` — End-of-session ritual: summarize → Master Brain upload → Obsidian daily note

### Workflows
- `/notebooklm-research` — Zero-token deep research pipeline via NotebookLM
- `/wrap-up` — Session memory persistence to Master Brain + Obsidian
- `/obsidian-sync` — Sync research outputs to Obsidian vault

### Master Brain Retrieval
At session start, if relevant context is needed from past sessions:
```bash
BRAIN_ID=$(cat ~/.notebooklm/master-brain-id 2>/dev/null)
if [ -n "$BRAIN_ID" ]; then
  notebooklm use "$BRAIN_ID"
  notebooklm ask "What do I know about [current topic]?"
fi
```
