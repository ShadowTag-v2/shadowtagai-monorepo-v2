# Rule 15: Ultrathink, Fast Mode, and Model Routing

## Ultrathink (Source: utils/thinking.ts)
- Keyword trigger: `/\bultrathink\b/i` in user message
- When detected: effort bumps from medium → high
- Gated by build flag ULTRATHINK + GrowthBook tengu_turtle_carbon
- Rainbow shimmer animation plays in UI

## Ultraplan (Source: commands/ultraplan.ts)
- Remote parallel planning sessions
- Build-gated: feature('ULTRAPLAN')
- Session state tracked via ultraplanSessionUrl and ultraplanLaunching

## Fast Mode (Source: utils/fastMode.ts)
- Routes to Opus 4.6: `getFastModeModel() = 'opus' + (isOpus1mMergeEnabled() ? '[1m]' : '')`
- Only supports models containing 'opus-4-6'
- Cooldown system: rate-limited → cooldown period → auto re-enable
- Org status: prefetched from `/api/claude_code_penguin_mode`
- Ant users default to enabled on prefetch failure
- Env: CLAUDE_CODE_DISABLE_FAST_MODE=1 to disable
- Env: CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS=1 to bypass proxy issues

## Model Routing (Source: constants/prompts.ts)
- Frontier: Claude Opus 4.6
- Aliases: sonnet → claude-sonnet-4-6, opus → claude-opus-4-6, haiku → claude-haiku-4-5-20251001
- Special aliases: 'best', 'sonnet[1m]', 'opus[1m]', 'opusplan'
- Subagent model override: CLAUDE_CODE_SUBAGENT_MODEL env var

## Effort Level Precedence (Source: utils/effort.ts)
```
ENV CLAUDE_CODE_EFFORT_LEVEL → appState.effortValue → model default
```
- 'max' downgraded to 'high' on non-Opus-4.6 models
- 'max' session-scoped for external users; ants can persist
- 'unset' or 'auto' → no effort param sent (API defaults to high)
- Numeric values (ant-only): ≤50=low, ≤85=medium, ≤100=high, >100=max
