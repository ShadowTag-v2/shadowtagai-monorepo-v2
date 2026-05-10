# Rule 11: Context Compaction Pipeline (4-Layer Architecture)

Context compaction is a 4-layer pipeline that runs on every single turn:

## Layer 1: Microcompact
Silently clears old tool results without an LLM call. If your cache is cold, it rewrites in-place. If warm, it sends cache_edits to the API so the cached prefix survives. This is invisible — no LLM cost, just cache management.

## Layer 2: Session Memory Compact
Skips the LLM entirely by reusing a pre-extracted session memory file as the summary. Keeps your last ~10-40K tokens of messages verbatim. This is the cheapest "real" compaction — no summarization, just memory file reuse.

## Layer 3: Full LLM Compaction
Forks an agent to summarize the entire conversation into 9 structured sections, then re-injects your 5 most recent files, active plan, skill content, and MCP instructions. This is the expensive one — it burns tokens to create the summary but recovers working context.

### Post-Compact Token Budgets (Source: compact.ts:122-130)
```
POST_COMPACT_MAX_FILES_TO_RESTORE   = 5       # max files re-injected
POST_COMPACT_TOKEN_BUDGET           = 50,000  # total file budget
POST_COMPACT_MAX_TOKENS_PER_FILE    = 5,000   # per-file cap
POST_COMPACT_MAX_TOKENS_PER_SKILL   = 5,000   # per-skill cap
POST_COMPACT_SKILLS_TOKEN_BUDGET    = 25,000  # SEPARATE skill pool
```
Key insight: file restoration (50K) and skill restoration (25K) are **separate budgets**. Skills are sorted most-recent-first so budget pressure drops the least-relevant skills first.

The 9 structured sections are:
1. Current task/objective
2. Key decisions made
3. Files modified
4. Errors encountered
5. Patterns established
6. Dependencies identified
7. Remaining work
8. Important context
9. Active constraints

## Layer 4: Reactive Compact
If the API still returns a 413 (payload too large), it withholds the error, compacts on the fly, and retries. You never see it. Recursion guards prevent the compactor from compacting itself. Post-compact cleanup resets 9 separate caches.

## The 250K Wasted API Calls Fix
From autoCompact.ts (lines 68-70): "BQ 2026-03-10: 1,279 sessions had 50+ consecutive failures (up to 3,272) in a single session, wasting ~250K API calls/day globally." The fix: MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3. After 3 consecutive failures, compaction is disabled for the rest of the session.

## Actionable Rules
- Compact AFTER research, before implementation
- Compact AFTER debugging, before new features
- Compact AFTER milestones
- NEVER compact mid-implementation (you lose variable names, file paths, partial state)
- Keep phases under 5 files to avoid triggering compaction mid-task
- Dead code accelerates compaction — always clean first
- Use /compact at natural breakpoints only
- AUTOCOMPACT_PCT_OVERRIDE=0.95 delays auto-compact trigger (set in env)

## Prompt Cache Economics
promptCacheBreakDetection.ts tracks 14 cache-break vectors with "sticky latches" that prevent mode toggles from busting the cache. Tool ordering matters: built-in tools are sorted as a contiguous prefix BEFORE MCP tools so adding/removing MCPs doesn't invalidate the cache. One function is annotated DANGEROUS_uncachedSystemPromptSection(). When you're paying per token, cache invalidation is an accounting problem, not a CS joke.
