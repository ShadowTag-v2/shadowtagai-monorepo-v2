# 4-Layer Context Compaction Pipeline — Architecture Specification

> Source: Claude Code v2.1.91 source leak (src.zip), `services/compact/`, `services/compress/`
> Intelligence classification: Adopted pattern, adapted for ShadowTag/Antigravity

## Overview

Claude Code implements a **4-layer context compression pipeline** that manages token budget
pressure within the ~200K context window. This document specifies each layer and maps it
to our equivalent (or recommended) implementation.

## Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Layer 0: Microcompact (within-message pruning)         │
│  Trigger: Every message cycle                           │
│  Action: Strip stale tool results, collapsed thinking   │
│  Token cost: ~0 (editing, not regenerating)              │
├─────────────────────────────────────────────────────────┤
│  Layer 1: Session Memory (autoCompact)                  │
│  Trigger: Context pressure crosses ~167,000 tokens      │
│  Action: Keep 5 files (5K tokens each), summarize rest  │
│  Output: Single 50K-token summary + fresh context       │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Full LLM Compaction (reactive_compact)        │
│  Trigger: Explicit /compact or extreme pressure (>90%)  │
│  Action: Full LLM summarization of conversation history │
│  Output: Condensed conversation + preserved file reads  │
├─────────────────────────────────────────────────────────┤
│  Layer 3: History Snipping (HISTORY_SNIP)               │
│  Trigger: Post-task, between natural breakpoints        │
│  Action: Cut old conversation turns entirely            │
│  Output: Clean context with only recent turns           │
└─────────────────────────────────────────────────────────┘
```

## Layer 0: Microcompact (CACHED_MICROCOMPACT)

**Feature flag**: `CACHED_MICROCOMPACT`
**Source**: `services/compact/microCompact.ts`

Within-message pruning that runs on EVERY cycle:
1. **Stale tool results**: Tool outputs older than N turns are replaced with `[Result cached: <hash>]`
2. **Collapsed thinking**: Extended `<thinking>` blocks are collapsed to single-line summaries
3. **Duplicate file reads**: If the same file was read multiple times, keep only the most recent

**Cache preservation**: Microcompact edits messages in-place, preserving the KV cache prefix.
This is the key innovation — it doesn't regenerate context, it surgically removes dead weight.

### Our Implementation
- **Status**: 🔴 NOT IMPLEMENTED
- **Recommendation**: Add to Antigravity's context optimization layer
- **Mapping**: The `context-optimization` skill documents the concept but doesn't implement it

## Layer 1: Auto-Compact (Session Memory)

**Feature flag**: Always active (can be tuned via `COMPACT_THRESHOLD`)
**Source**: `services/compact/autoCompact.ts`

Auto-compact fires when context pressure crosses ~167,000 tokens (~83% of 200K):

1. **File retention**: Keeps the 5 most recently accessed files (capped at 5K tokens each)
2. **Summarization**: Everything else → single 50,000-token summary via LLM call
3. **Destruction**: All file reads, reasoning chains, intermediate decisions are discarded

### Critical Finding: The Death Spiral
Auto-compaction is the root cause of "context decay" after 10+ messages:
- Dirty code (dead imports, unused exports) accelerates compaction
- Each compaction loses variable names, file paths, and partial state
- The agent starts hallucinating post-compaction (29-30% false claim rate)

### Our Implementation
- **Status**: 🟡 PARTIAL — `~/.claude/CLAUDE.md` documents awareness rules
- **Mitigation**: Rule 6 (Context Decay Awareness) in user CLAUDE.md
- **Gap**: We have no equivalent for Antigravity sessions

## Layer 2: Reactive Compact

**Feature flag**: `REACTIVE_COMPACT`
**Source**: `services/compact/reactiveCompact.ts`

Full LLM compaction triggered by:
- Explicit `/compact` slash command
- Extreme pressure (>90% context utilization)
- Post-error recovery (agent stuck in loop)

Unlike auto-compact, reactive compact uses the LLM itself to summarize:
1. Conversation history → structured summary with key decisions preserved
2. File reads → condensed to function signatures + key findings
3. Error traces → compressed to root cause + resolution

### Our Implementation
- **Status**: 🟡 PARTIAL — `/compact` timing rules in CLAUDE.md Layer 1
- **Rule**: Compact AFTER milestones, NEVER mid-implementation

## Layer 3: History Snipping

**Feature flag**: `HISTORY_SNIP`
**Source**: `services/compact/historySnip.ts`

Nuclear option — cuts old conversation turns entirely:
1. Preserves only the last N turns (configurable, default ~10)
2. Generates a "conversation genesis" summary as the new turn 0
3. Used between natural breakpoints (after research, before implementation)

### Our Implementation
- **Status**: 🔴 NOT IMPLEMENTED
- **Equivalent**: KI system provides cross-session persistence but not within-session pruning

## Circuit Breaker Integration

```
context_utilization() → percentage
  if < 50%:  NO-OP
  if 50-83%: MICROCOMPACT (Layer 0)
  if 83-90%: AUTO-COMPACT (Layer 1)
  if 90-95%: REACTIVE-COMPACT (Layer 2)
  if > 95%:  HISTORY-SNIP (Layer 3) + EMERGENCY flag
```

Key insight: The circuit breaker is **monotonic** — once a higher layer fires,
lower layers are no longer effective until the next natural breakpoint.

## Prompt Cache Economics

**Source**: `services/cache/cacheManager.ts`

### 14 Cache-Break Vectors
1. Adding/removing MCP server tools
2. Changing tool ordering
3. Modifying system prompt dynamic section
4. User message content variation
5. Different conversation turn counts
6. File content injection into context
7. Tool result size variation
8. Compaction (resets entire cache)
9. Sub-agent fork (creates new cache branch)
10. Model switch (different KV dimensions)
11. Temperature/top-p changes (some providers)
12. Memory file updates
13. Skill file loading (appends to tool list)
14. Feature flag changes (modify system prompt)

### `DANGEROUS_uncachedSystemPromptSection()`
Explicitly annotated function in the source that warns developers about the cache cost
of dynamic prompt content. Everything after this boundary flushes the KV cache.

### Sticky Latches
Certain features, once activated, permanently modify the cached prefix:
- `COORDINATOR_MODE` adds delegation schemas
- `TORCH` adds safety escalation rules
- `BUDDY` adds personality tuning

These are **append-only** to preserve cache — they cannot be removed mid-session.

## ShadowTag/Antigravity Integration Points

| CC Pattern | Our Equivalent | Gap |
|-----------|---------------|-----|
| Microcompact | None | Need within-action context pruning |
| Auto-compact (~167K) | KI persistence layer | No within-session equivalent |
| Reactive compact | KI + session wrap-up | Manual, not automated |
| History snip | Conversation truncation (platform-level) | No agent-level control |
| Cache economics | No prompt caching (Antigravity) | Platform handles caching |
| Circuit breaker | None | Need token pressure monitoring |

## Recommendations

1. **For Antigravity**: Token pressure is handled by the platform. Document awareness rules in skills.
2. **For Claude Code sessions**: The CLAUDE.md layers already enforce compaction discipline.
3. **For CounselConduit**: Implement token budget monitoring in LiteLLM routing (OWASP LLM10).

---

*Document version: 1.0 | Source: CL4R1T4S competitive intelligence + src.zip forensics*
*Last updated: 2026-04-18*
