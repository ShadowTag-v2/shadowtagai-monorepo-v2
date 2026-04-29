# Claude Code Feature Flags & Secret Environment Variables Catalog

> Source: ccleaks.com, src.zip forensics, GrowthBook tengu_* namespace
> Intelligence classification: Competitive roadmap analysis

## Feature Flags (44 identified)

### Tier 1: Shipped & Active
| Flag | Purpose | Status |
|------|---------|--------|
| `COORDINATOR_MODE` | Multi-agent delegation (dispatch to sub-agents) | ✅ Active via env var |
| `COR.KAIROS` | Background daemon for autonomous task continuation | ✅ Active via env var |
| `ULTRAPLAN` | Enhanced planning/architecture mode | ✅ Active via env var |
| `DREAM` | Memory consolidation daemon (nightly aggregation) | ✅ Active via env var |
| `BUDDY` | Personality tuning / conversational warmth | ✅ Shipped (opt-in) |
| `SKILL_SEARCH` | On-demand skill file loading via search | ✅ Shipped |
| `FORK_SUBAGENT` | Fork context for parallel sub-agent execution | ✅ Shipped |
| `WEB_BROWSER` | Browser-based web search and interaction | ✅ Shipped |

### Tier 2: Feature-Gated (GrowthBook)
| Flag | Purpose | Status |
|------|---------|--------|
| `TORCH` | Safety escalation for high-risk operations | 🟡 Gated (tengu_torch) |
| `WORKFLOW_SCRIPTS` | Bash/Python workflow automation scripts | 🟡 Gated |
| `VOICE_MODE` | Voice input/output for conversational coding | 🟡 Gated |
| `TEMPLATES` | Project template generation from session patterns | 🟡 Gated |
| `UDS_INBOX` | Unix Domain Socket inter-process messaging | 🟡 Gated |
| `REACTIVE_COMPACT` | Explicit context compaction on pressure | 🟡 Gated |
| `CONTEXT_COLLAPSE` | Aggressive context reduction for long sessions | 🟡 Gated |
| `HISTORY_SNIP` | Cut old conversation turns entirely | 🟡 Gated |
| `CACHED_MICROCOMPACT` | Within-message tool result pruning | 🟡 Gated |
| `TOKEN_BUDGET` | Per-session token spending limits | 🟡 Gated |
| `EXTRACT_MEMORIES` | Auto-extract learnings from session to memory dir | 🟡 Gated |
| `TERMINAL_PANEL` | Split terminal panel in VS Code integration | 🟡 Gated |
| `SELF_HOSTED` | Self-hosted model backend (non-Anthropic) | 🟡 Gated |
| `MONITOR_TOOL` | Security monitor as a formal tool (not just prompt) | 🟡 Gated |

### Tier 3: Internal/Experimental
| Flag | Purpose | Status |
|------|---------|--------|
| `ABLATION_BASE` | Disables ALL safety features for A/B testing | 🔴 Internal |
| `BYOC_RUNNER` | Bring Your Own Container sandbox execution | 🔴 Internal |
| `CCR_AUTO` | Automated Claude Code Review integration | 🔴 Internal |
| `MEM_SHAPE_TEL` | Memory shape telemetry collection | 🔴 Internal |
| `TRANSCRIPT_CLASSIFIER` | ML classifier for auto-permission (YOLO) | 🔴 Internal |

### Tier 4: Unreleased (ccleaks.com discoveries)
| Flag | Purpose | Status |
|------|---------|--------|
| `AGENTS_BETA` | Multi-agent orchestration beta | 🔴 Unreleased |
| `TOOL_VERSIONING` | Per-tool version pinning | 🔴 Unreleased |
| `CONTEXT_PREVIEW` | Preview context state before compaction | 🔴 Unreleased |
| `SESSION_REPLAY` | Replay past sessions for debugging | 🔴 Unreleased |
| `COST_OPTIMIZER` | Automatic model tier selection by task complexity | 🔴 Unreleased |
| `PARALLEL_TOOLS` | Parallel tool execution within single turn | 🔴 Unreleased |
| `STRUCTURED_OUTPUT` | Force JSON schema output mode | 🔴 Unreleased |
| `STREAMING_EDIT` | Streaming file edit display | 🔴 Unreleased |

---

## Secret Environment Variables (Key Findings)

### Permission Bypass
| Variable | Effect | Risk Level |
|----------|--------|------------|
| `USER_TYPE="ant"` | Bypasses ALL permission prompts | 🔴 CRITICAL |
| `CLAUDE_CODE_ABLATION_BASELINE="1"` | Disables ALL safety features | 🔴 CRITICAL |
| `DISABLE_COMMAND_INJECTION_CHECK="1"` | Skips command injection guard | 🔴 HIGH |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS` | Override context window size | 🟡 MEDIUM |

### Debug & Telemetry
| Variable | Effect | Risk Level |
|----------|--------|------------|
| `DISABLE_TELEMETRY=1` | Stops analytics collection | 🟢 SAFE |
| `DISABLE_ERROR_REPORTING=1` | Stops crash reporting | 🟢 SAFE |
| `DISABLE_FEEDBACK_COMMAND=1` | Removes /feedback command | 🟢 SAFE |
| `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1` | Stops post-session survey | 🟢 SAFE |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` | Stops GrowthBook/analytics polling | 🟡 MEDIUM |

### Operational
| Variable | Effect | Risk Level |
|----------|--------|------------|
| `CLAUDE_CODE_COORDINATOR_MODE=1` | Enable multi-agent dispatch | 🟢 SAFE |
| `CLAUDE_CODE_API_KEY` | API key override | 🟡 MEDIUM |
| `CLAUDE_CODE_DEFAULT_MODEL` | Default model override | 🟢 SAFE |
| `CLAUDE_CODE_MAX_TURN_TOKENS` | Per-turn token limit | 🟢 SAFE |

---

## GrowthBook `tengu_*` Namespace

The GrowthBook feature flag service uses the `tengu_*` prefix for Claude Code flags:
- `tengu_torch` — Safety escalation
- `tengu_coordinator` — Multi-agent mode
- `tengu_voice` — Voice mode
- `tengu_dream` — Memory consolidation
- `tengu_kairos` — Background daemon

GrowthBook polls require network access. If `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`
is set, these gates fall back to **env var overrides** (which take precedence).

---

## 26 Hidden Slash Commands

| Command | Purpose |
|---------|---------|
| `/compact` | Manual context compaction |
| `/ctx-viz` | Context utilization visualization |
| `/btw` | Inject side-note without tool call |
| `/good-claude` | Positive reinforcement (adjusts generation style) |
| `/ultraplan` | Switch to enhanced planning mode |
| `/dream` | Trigger memory consolidation |
| `/bughunter` | Dedicated debugging mode |
| `/cost` | Show API cost breakdown |
| `/token-count` | Show token utilization |
| `/model` | Switch model mid-session |
| `/memory` | View/edit memory directory |
| `/skill` | Load or create skill |
| `/plan` | Start planning mode |
| `/review` | Code review mode |
| `/test` | Testing mode |
| `/deploy` | Deployment mode |
| `/config` | View/edit configuration |
| `/permissions` | View permission state |
| `/mcp` | MCP server management |
| `/doctor` | Diagnose session health |
| `/login` | Authentication management |
| `/logout` | Clear authentication |
| `/bug` | Bug report mode |
| `/feedback` | Submit feedback (disableable) |
| `/help` | Help menu |
| `/clear` | Clear context |

---

## Adversa AI 50-Subcommand Bypass

**Source**: Adversa AI security audit (public)
**Severity**: 🔴 CRITICAL (for our Judge 6)

The attack chains 50+ benign-looking subcommands that individually pass the
BLOCK/ALLOW security monitor but collectively perform a harmful action:

```
# Each subcommand looks benign:
echo "part1" > /tmp/stage1.txt    # ALLOW: writing to temp
echo "part2" >> /tmp/stage1.txt   # ALLOW: appending to file
cat /tmp/stage1.txt | base64 -d   # ALLOW: reading temp file
# ... (50 more steps)
# Final step reconstructs and executes malicious payload
```

### Implications for Judge 6
Our current BLOCK/ALLOW spec (Cor.Claude_Code_6_block_allow_spec.md) evaluates actions individually.
The Composite Action Evaluation rule (line 83-86) is theoretically sound but lacks:

1. **Chain depth limit**: No maximum command chain length before escalation
2. **Temporal analysis**: No correlation between sequential commands
3. **Reconstruction detection**: No check for incremental file assembly patterns

### Recommended Mitigations
1. Add chain depth limit (>10 sequential shell commands → auto-ESCALATE)
2. Implement file assembly detection (multiple writes to same path → flag)
3. Add base64/encoding detection in command chains → auto-BLOCK
4. Correlate sequential BashTool calls within rolling 5-minute window

---

*Document version: 1.0 | Source: CL4R1T4S + ccleaks.com + Adversa AI public reports*
*Last updated: 2026-04-18*
