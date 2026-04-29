# Rule 16: Feature Flags and Environment Variables

## Build-Time Feature Flags (via bun:bundle feature())
Dead-code eliminated at build time. 85+ flags discovered.

### Active in External Builds
- REACTIVE_COMPACT — 413 auto-retry with compaction
- CONTEXT_COLLAPSE — intelligent context management
- FORK_SUBAGENT — cache-sharing subagent spawn
- VERIFICATION_AGENT — built-in verification agents
- TOKEN_BUDGET — task-level token budgets
- EXTRACT_MEMORIES — auto memory extraction
- COMMIT_ATTRIBUTION — git attribution
- PROMPT_CACHE_BREAK_DETECTION — cache break logging
- TREE_SITTER_BASH — parsed bash security

### Internal-Only (ant builds)
- COR.KAIROS, COR.KAIROS_BRIEF, COR.KAIROS_CHANNELS, COR.KAIROS_DREAM
- COORDINATOR_MODE, PROACTIVE
- BUDDY (companion pet system)
- ULTRAPLAN (remote parallel planning)
- CACHED_MICROCOMPACT, PERFETTO_TRACING
- ANTI_DISTILLATION_CC, NATIVE_CLIENT_ATTESTATION

## Critical Environment Variables

### Performance
- CLAUDE_CODE_EFFORT_LEVEL — low|medium|high|max
- CLAUDE_CODE_AUTO_COMPACT_WINDOW — override context window
- CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY — parallel tool limit
- CLAUDE_CODE_SUBAGENT_MODEL — override subagent model

### Security / Privacy
- CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS — anti-distillation
- CLAUDE_CODE_UNDERCOVER — force undercover mode (ant-only)
- CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC — privacy mode
- CLAUDE_CODE_SUBPROCESS_ENV_SCRUB — scrub env in subprocesses

### Session Control
- CLAUDE_CODE_DISABLE_AUTO_MEMORY — skip memory extraction
- CLAUDE_CODE_SM_COMPACT — session memory compaction
- CLAUDE_CODE_DISABLE_CRON — disable cron tasks
- CLAUDE_CODE_DISABLE_BACKGROUND_TASKS — no background tasks

### Identity
- USER_TYPE — 'ant' (internal) or 'external' (build-time define)
- CLAUDE_CODE_ENTRYPOINT — entry point identifier
- CLAUDE_CODE_ENVIRONMENT_KIND — local|remote environment type
