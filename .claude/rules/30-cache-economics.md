# Rule 30: Prompt Cache Economics & 14-Vector Tracking
# Source: promptCacheBreakDetection.ts + systemPromptSections.ts + compact.ts

## The Accounting Problem
When you're paying per-token, cache invalidation is an accounting problem,
not a CS joke. Claude Code tracks **14 cache-break vectors** with sticky
latches that prevent mode toggles from busting the cache.

## 14 Cache-Break Vectors (Source: promptCacheBreakDetection.ts)
Any of these invalidate the prompt cache and force a full re-tokenization:

1. Tool schema additions/removals (77% of breaks per BigQuery 2025-03-22)
2. System prompt text changes (DANGEROUS_uncachedSystemPromptSection)
3. MCP tool registration order changes
4. CLAUDE.md edits (loaded every turn, not session start)
5. Temperature/top-p parameter changes
6. Model changes (within session)
7. Permission mode toggles (mitigated by sticky latches)
8. Feature flag flips
9. Conversation history prefix changes
10. Skill content changes (re-injected post-compact)
11. Context window overflow triggering compact
12. Tool name sorting order changes
13. Rules file additions/removals (.claude/rules/*.md)
14. @include directive resolution changes

## Mitigation Strategies (Source-Verified)

### Tool Schema Deferred Loading
Claude Code mitigates the #1 vector by **deferred loading**: sends only tool
names to the API initially, loads full schemas on demand via `ToolSearchTool`.
This means adding MCP tools doesn't invalidate the cache until the tool is
actually invoked.

### Contiguous Prefix Ordering
Built-in tools are sorted as a **contiguous prefix** BEFORE MCP tools. This
means adding/removing MCP tools only invalidates the suffix, not the prefix.
Tool ordering matters for cache stability.

### Sticky Latches
Permission mode toggles (e.g., auto-approve → ask → auto-approve) use
"sticky latches" that prevent the mode change from busting the cache.
Once a permission mode is latched, it persists for the session.

### DANGEROUS_uncachedSystemPromptSection (Source: systemPromptSections.ts:63)
```typescript
function DANGEROUS_uncachedSystemPromptSection(): UncachedSystemPromptSection
```
This function is the explicit cache-break marker. Content returned by this
function is NEVER cached — it sits in the "uncached" section of the system
prompt. Used for volatile content that changes frequently (timestamps,
dynamic state). Everything else is cached aggressively.

## Compact-at-Milestones Doctrine
From autoCompact.ts — the 250K wasted API calls fix:
- MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3 (circuit breaker)
- After 3 consecutive failures, compaction disabled for session
- Compact AFTER research, AFTER debugging, AFTER milestones
- NEVER compact mid-implementation (loses variable names, file paths, partial state)
- AUTOCOMPACT_PCT_OVERRIDE=0.95 delays auto-compact trigger

## Subagent KV Cache Forking
When a subagent is spawned:
1. Parent's KV cache prefix is inherited (not recomputed)
2. Subagent appends its own context to the inherited prefix
3. On subagent completion, only the result summary is merged back
4. This avoids paying the full prompt re-tokenization cost per subagent

## Antigravity Cache Economics
Map to Gemini's context caching:
- Use `cachedContent` in Vertex AI for system instructions
- Avoid modifying CLAUDE.md / KIs mid-session (breaks cache)
- Group MCP tools as a contiguous prefix in `antigravity-mcp-config.json`
- Use the "write once, leave alone" doctrine for instruction files
