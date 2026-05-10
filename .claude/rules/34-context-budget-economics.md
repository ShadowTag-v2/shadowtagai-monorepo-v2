# Rule 34 — Context Budget Economics

Source: `claude-agent-sdk-python` ContextUsageResponse, `everything-claude-code` context-budget skill

## Context Usage API (SDK-Verified)

The `ContextUsageResponse` provides authoritative telemetry:

```python
class ContextUsageResponse(TypedDict):
    categories: list[ContextUsageCategory]   # Per-section breakdown
    totalTokens: int                         # Current context window usage
    maxTokens: int                           # Effective max (may be reduced by autocompact)
    rawMaxTokens: int                        # Raw model window size
    percentage: float                        # Usage percentage (0-100)
    model: str                               # Model name
    isAutoCompactEnabled: bool               # Autocompact status
    memoryFiles: list[dict]                  # CLAUDE.md + memory files with token counts
    mcpTools: list[dict]                     # MCP tools with name, server, tokens, isLoaded
    agents: list[dict]                       # Agent defs with type, source, tokens
    autoCompactThreshold: int                # Optional threshold
    deferredBuiltinTools: list[dict]         # Deferred tool schemas
    systemPromptSections: list[dict]         # System prompt sections with tokens
    messageBreakdown: dict                   # Message tokens by type
    apiUsage: dict | None                    # Cumulative API usage
```

## Token Cost Model (ECC-Verified)

### Estimation Formulas
- **Prose**: `words × 1.3` tokens
- **Code-heavy files**: `chars / 4` tokens
- **MCP tool schema**: ~500 tokens per tool

### Component Overhead Classification

| Component | Token Range | Always Loaded? |
|-----------|------------|----------------|
| CLAUDE.md chain | 500-3000 | YES — every turn |
| Agent descriptions | 200-2000/agent | YES — in Task tool context |
| Skills (SKILL.md) | 1000-5000/skill | YES — when referenced |
| Rules (per file) | 200-1500 | YES — all loaded |
| MCP tool schemas | ~500/tool | YES (unless deferred) |
| Conversation history | Variable | YES — grows per turn |
| Tool results | Variable | YES — until compacted |

### Budget Classification Buckets

| Bucket | Criteria | Action |
|--------|----------|--------|
| Always needed | Referenced in CLAUDE.md, backs active command, matches project type | Keep |
| Sometimes needed | Domain-specific, not referenced in CLAUDE.md | On-demand activation |
| Rarely needed | No command reference, overlapping content, no project match | Remove or lazy-load |

## Problem Patterns (5 Classes)

1. **Bloated agent descriptions** — description >30 words loads into every Task invocation
2. **Heavy agents** — files >200 lines inflate Task context on every spawn
3. **Redundant components** — skills duplicating agent logic, rules duplicating CLAUDE.md
4. **MCP over-subscription** — >10 servers, or servers wrapping free CLI tools
5. **CLAUDE.md bloat** — verbose explanations, outdated sections, instructions that should be rules

## Budget Report Template

```
Context Budget Report
═══════════════════════════════════════
Total estimated overhead: ~XX,XXX tokens
Context model: [model] ([maxTokens] window)
Effective available: ~XXX,XXX tokens (XX%)

Component Breakdown:
│ Component    │ Count │ Tokens  │
│ Agents       │ N     │ ~X,XXX  │
│ Skills       │ N     │ ~X,XXX  │
│ Rules        │ N     │ ~X,XXX  │
│ MCP tools    │ N     │ ~XX,XXX │
│ CLAUDE.md    │ N     │ ~X,XXX  │

Top 3 Optimizations:
1. [action] → save ~X,XXX tokens
2. [action] → save ~X,XXX tokens
3. [action] → save ~X,XXX tokens
```

## The MCP Lever

MCP is the single biggest token consumer:
- A 30-tool server costs MORE than all skills combined
- Each tool schema ≈ 500 tokens
- CLI-replaceable servers (gh, git, npm) waste budget on tool schemas you don't need
- Solution: Kill CLI-replaceable MCP servers, use direct bash

## Strategic Compaction Decision Table

| Phase Transition | Compact? | Rationale |
|-----------------|----------|-----------|
| Research → Planning | YES | Research context is bulky; plan is the distilled output |
| Planning → Implementation | YES | Plan is in files; free context for code |
| Implementation → Testing | MAYBE | Keep if tests reference recent code |
| Debugging → Next feature | YES | Debug traces pollute unrelated work |
| Mid-implementation | NO | Losing file paths and partial state is costly |
| After failed approach | YES | Clear dead-end reasoning |

## What Survives Compaction

| Persists | Lost |
|----------|------|
| CLAUDE.md instructions | Intermediate reasoning |
| TodoWrite task list | File contents previously read |
| Memory files | Multi-step conversation context |
| Git state (commits, branches) | Tool call history and counts |
| Files on disk | Verbal user preferences |

## Operational Rule

Before adding ANY new MCP server, agent, or skill:
1. Run context budget audit
2. Check if overhead exceeds 40% of effective window
3. If yes, remove lower-priority components FIRST
4. Never exceed 50% overhead — leaves too little for conversation
