# AI Coding Agent Competitive Matrix — April 2026

> Updated: 2026-04-30 | Source: web research, cc_leaks_deep_fold_in KI, cl4r1t4s_competitive_intel KI

## Tier 1: Direct Competitors

| Dimension | Antigravity (Gemini) | Claude Code v2.1 (Tengu) | Cursor 2.0 | Devin 2.0 |
|-----------|---------------------|--------------------------|------------|-----------|
| **Architecture** | IDE-embedded MCP agent | Terminal REPL agent | VS Code fork + AI IDE | Cloud sandbox autonomous |
| **Model** | Gemini 3.1 Flash/Pro | Claude 4.5 Opus | Multi-model (Claude 4.5, GPT-5) | Proprietary fine-tuned |
| **Autonomy** | Configurable (STATE A/B) | YOLO + Bash AST cap | Developer-in-loop | Full autonomous delegation |
| **Context Window** | 2M tokens | 200K tokens + compaction | ~200K effective | Unknown (cloud-managed) |
| **Memory** | KI system + Dream daemon | AutoDream + VCR replay | Workspace context + @Docs | Devin Wiki auto-index |
| **Tool Ecosystem** | 90 MCP tools, 5 servers | 44 feature flags, 372 ant gates | Composer 2 + /multitask | Slack/Teams integration |
| **Security** | 3-layer XML classifier | BLOCK/ALLOW monitor + AST | Basic guardrails | Cloud sandbox isolation |
| **Pricing** | Google Workspace tier | API + Pro subscription | $20/mo Pro | $500/mo Teams |
| **Self-Healing** | Ruff + Biome auto-fix | ESLint auto-fix | Auto-fix suggestions | Auto-test + retry |

## Key Differentiators (April 2026 Update)

### Devin 2.0 — New Capabilities
- **Devin Wiki & Search**: Automatic repository indexing with architecture diagrams
- **Interactive Planning**: Proactive research → roadmap → approval before execution
- **Desktop Testing**: Can "see" and interact with desktop apps for E2E testing
- **Devin Review**: PR analysis with bug/security detection, grouped change view
- **Pricing**: $500/mo Teams tier (up from $20/mo individual in 2025)

### Cursor 2.0 — New Capabilities
- **Composer 2**: Multi-file agentic workflows, cross-repository editing
- **/multitask**: Parallelized sub-agents for independent tasks
- **Cursor SDK**: Developers can build custom programmatic agents
- **Instant Grep**: Faster codebase navigation than standard ripgrep
- **Model Flexibility**: Choose between Claude 4.5, GPT-5, Gemini per task
- **ACP (Agent Control Protocol)**: JetBrains integration (beyond VS Code)

### Antigravity Advantages (Our Moat)
1. **5-server MCP Fleet**: No competitor has equivalent integrated tool surface (90 tools)
2. **2M Context Window**: 10x larger than any competitor
3. **KI + Dream Architecture**: Persistent cross-session memory (no competitor matches)
4. **STATE A/B Machine**: Configurable autonomy with security gates
5. **Zero-Trust Security**: 3-layer XML classifier + betterleaks + Cor.30 pipeline
6. **Google-Native**: Direct Firebase, Cloud Run, Firestore, Stitch integration
7. **Sovereign Skill Fleet**: 264 skills (no competitor has comparable extensibility)

### Antigravity Gaps (Address in Q2 2026)
1. **Desktop Testing**: Devin can interact with desktop apps; we're browser-only via Chrome DevTools MCP
2. **PR Review UI**: Devin Review provides grouped change analysis; we lack a dedicated UI
3. **Multi-Model**: Cursor allows model switching per task; we're locked to Gemini family
4. **SDK/API**: Cursor SDK lets devs build custom agents; our extensibility is skill-based only
5. **Team Collaboration**: Devin has native Slack/Teams integration; we're single-operator

## Market Positioning

```
Autonomy ──────────────────────────────────────────►
│ Low                    Medium                High
│
│ Cursor 2.0         Antigravity          Devin 2.0
│ (pair programmer)  (configurable)       (delegated)
│
│                    Claude Code
│                    (terminal REPL)
```

## Claude Agent SDK Python — Architecture Analysis (2026-04-30)

> Source: `external_repos/claude-agent-sdk-python/` (official Anthropic SDK)

### Key Patterns Discovered

| Module | Pattern | Adoptable? |
|--------|---------|------------|
| `session_resume.py` | Materializes external store sessions into temp `CLAUDE_CONFIG_DIR` for subprocess resume | ✅ Reference for KI-backed session restore |
| `transcript_mirror_batcher.py` | Bounded async buffer (500 entries / 1MiB) with eager background flush | ✅ Pattern for Dream daemon evidence streaming |
| `session_store_validation.py` | Pre-flight validation of store option combinations (fail-fast before spawn) | ✅ Apply to daemon config validation |
| `message_parser.py` | Typed message parsing (21 message types: Text, Thinking, ToolUse, ToolResult, RateLimit, etc.) | ✅ Reference for MCP message handling |
| `session_store_conformance.py` | Protocol conformance test harness for custom session stores | ✅ Template for our KI store testing |
| `types.py` | `PermissionMode` enum (`default/acceptEdits/plan/bypassPermissions/dontAsk/auto`) | ✅ Maps to our STATE A/B machine |
| `types.py` | `exclude_dynamic_sections` flag for cross-user prompt caching | ✅ Cost optimization pattern |
| `_task_compat.py` | Python 3.10/3.11/3.14 TaskGroup compatibility shim | ⬜ Already on 3.14 exclusively |

### SDK Architecture Insights

1. **Session Store Protocol**: Abstract `SessionStore` with `append()`, `list()`, `get()`, `list_subkeys()` — implementations for Postgres, Redis, S3
2. **Transcript Mirroring**: Real-time session recording via bounded batcher (prevents OOM during long sessions)
3. **6 Permission Modes**: `auto` = full YOLO, `plan` = read-only planning, `dontAsk` = bypass all permission prompts
4. **Beta Headers**: `context-1m-2025-08-07` — confirms 1M context was beta gated

## ECC2 Rust TUI — Architecture Reference (2026-04-30)

> Source: `external_repos/everything-claude-code/ecc2/src/` (16 Rust files)
> Status: QUARANTINE — REFERENCE ONLY (Rust, not adoptable as Python/TS code)

### Architecture Patterns (Adoptable as Design)

| Module | Pattern | Value |
|--------|---------|-------|
| `worktree/` | Git worktree-based agent isolation (dedicated branch per task) | HIGH — parallel agent execution |
| `session/daemon.rs` | Background session daemon with TCP IPC | MED — daemon fleet architecture reference |
| `session/runtime.rs` | Session lifecycle management (spawn → monitor → collect) | MED — maps to our daemon registry |
| `tui/dashboard.rs` | Real-time agent activity dashboard | LOW — we use Chrome DevTools MCP |
| `comms/` | Inter-agent communication via TCP sockets | MED — alternative to MCP stdio |
| `config/mod.rs` | `auto_create_worktrees` policy flag | HIGH — configurable isolation default |

## Recommended Actions

| # | Action | Priority | ETA |
|---|--------|----------|-----|
| 1 | Add desktop app testing via Playwright Desktop | P2 | Q2 2026 |
| 2 | Build PR review analysis tool | P2 | Q2 2026 |
| 3 | Explore model-routing per task complexity | P3 | Q3 2026 |
| 4 | Add Slack/Teams notification integration | P3 | Q3 2026 |
| 5 | Publish Antigravity SDK for custom agent builders | P3 | Q3 2026 |
| 6 | Port session store conformance testing pattern | P2 | Q2 2026 |
| 7 | Implement transcript mirror bounded batcher for Dream daemon | P2 | Q2 2026 |
| 8 | Add worktree-based agent isolation (from ECC2) | P3 | Q3 2026 |
