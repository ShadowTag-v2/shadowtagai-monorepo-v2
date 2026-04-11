# Rule 22: Tool Deferral & Prompt Cache Scoping
# Source: Claude Code Source (ToolSearchTool.ts, promptCacheBreakDetection.ts, systemPromptSections.ts)

## Tool Deferral (Pattern #1)
When MCP tool count exceeds threshold (e.g., >20 tools), defer tool schemas:
- Send only tool NAMES to the API, not full schemas
- Use `ToolSearchTool` to discover and load full schemas on demand:
  - `select:<tool_name>` — direct selection, supports comma-separated multi-select
  - Keyword search — scoring algorithm: part match (10-12pts), substring (5-6pts),
    description word-boundary match (2pts), searchHint match (4pts)
  - Exact-name fast path: bare tool name → direct return (no scoring needed)
  - MCP prefix matching: `mcp__server` → all tools from that server
- Saves 10-50K+ tokens per request with many MCP connections
- Cache invalidation: track deferredToolNames, clear description cache on change
- Memoize tool descriptions by name (compute once per session)

## Prompt Cache Break Detection (Pattern #3)
Two-phase system — pre-call snapshot, post-call comparison:
- **Phase 1 (pre-call)**: Hash system prompt, tool schemas (per-tool!), cache_control fields,
  model, fast mode state, beta headers, effort value, extra body params
- **Phase 2 (post-call)**: Check if `cache_read` tokens dropped >5% AND >2,000 tokens absolute
- If break detected, diff pre/post hashes to identify EXACTLY what caused it:
  - "Tool X schema changed" (per-tool hashing pinpoints which MCP tool)
  - "System prompt grew by 342 chars"
  - "TTL expired (62 min gap, no client changes)"
  - "Likely server-side (prompt unchanged, <5min gap)"
- Eviction cap: MAX_TRACKED_SOURCES = 10 (prevents unbounded memory from subagents)
- Cache deletion handling: cached microcompact deletions are expected drops, not breaks

## System Prompt Cache Scoping (Pattern #15)
The system prompt splits at `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`:
- **Static prefix** → `cacheScope: 'global'` (shared across users, 1-hour TTL)
- **Dynamic suffix** → `cacheScope: null` (changes per turn, never cached)
- MCP tools force entire prompt to `cacheScope: 'org'` (can't globally cache user tools)
- **ONE** `cache_control` marker per request (multiple → inefficient page eviction)
- Sections computed via `systemPromptSection()` — memoized, cleared on /clear or /compact
- Volatile sections use `DANGEROUS_uncachedSystemPromptSection()` — name IS the warning

## Applicability to Antigravity/MCP
- Defer MCP tool schemas across 7+ connected servers (chrome-devtools, firebase, etc.)
- Maintain stable system prompt prefix for Gemini context caching
- Hash tool schemas per-server to detect which MCP server caused cache invalidation
- Single cache marker discipline applies to Gemini `cachedContent` API
