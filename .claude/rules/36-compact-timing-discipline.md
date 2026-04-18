# Rule 36: Compact Timing Discipline

> Source: Nathan Wilbanks analysis + ECC strategic-compact skill + CC autoCompact.ts

## Mandate

Compact at **natural breakpoints**, never mid-implementation.

## Approved Compact Points

| Timing | Why | Risk if violated |
|--------|-----|-----------------|
| AFTER research, BEFORE implementation | Research context is summarizable; implementation state is not | Lose file paths, variable names, partial AST state |
| AFTER debugging, BEFORE new features | Bug context is resolved; new feature needs clean slate | Hallucinate previously-fixed bugs as still broken |
| AFTER milestones (commit/deploy) | Work is committed; context can be reconstructed from git | N/A — low risk |
| AFTER hook pipeline modification | Hook state is quiescent | Race with active hook; stale hook reference |

## NEVER Compact

- Mid-implementation (lose variable names, file paths, partial state)
- During active debugging (lose error context, stack traces)
- While awaiting user feedback (lose the question context)
- During tool execution chains (break tool_use/tool_result pairing)

## Source-Verified Auto-Compact Thresholds (autoCompact.ts:62-65)

```
AUTOCOMPACT_BUFFER_TOKENS     = 13,000
WARNING_THRESHOLD_BUFFER      = 20,000
ERROR_THRESHOLD_BUFFER        = 20,000
MANUAL_COMPACT_BUFFER         = 3,000
MAX_CONSECUTIVE_FAILURES      = 3 (circuit breaker)
MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20,000 (p99.99 = 17,387)
```

## /compact Command Discipline

When manually triggering `/compact`:
1. Ensure all pending tool results are processed
2. Commit any in-progress file changes
3. Note the current task state in a comment
4. Compact
5. Re-read the 5 most critical files post-compact
6. Verify the active plan survived

## Integration with Suggest-Compact Hook

The `suggest-compact.js` PreToolUse hook tracks call count and suggests compaction at 50-call threshold. This aligns with "after milestones" — 50 tool calls typically represents a research or implementation phase boundary.
