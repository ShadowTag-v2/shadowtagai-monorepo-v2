# AGNT Comparison — Claude Code vs Antigravity Architecture

> Source: `/etc/claude-code/CLAUDE.md` (lines 60-73), CC leaks analysis 2026-04-18

## Architecture Comparison

| Dimension | Claude Code (AGNT) | Antigravity/ShadowTag |
|-----------|-------------------|----------------------|
| **Prompt Architecture** | Single monolithic system prompt (150K+ chars) inserted via API | 4-layer hierarchy: `/etc/` + `~/.claude/` + `./CLAUDE.md` + `.claude/rules/` (51 files) |
| **Context Management** | 4-layer compaction (micro/auto/reactive/snip) with 167K threshold | Platform-level truncation + KI pointer system |
| **Memory** | `/memories` directory + Dream consolidation (auto-save + dream cycle) | KI system (metadata.json + artifacts/) + brain/ session persistence |
| **Security Gate** | Inline security monitor (BLOCK/ALLOW, ~14K chars in system prompt) | Judge 6 spec (external, compiled binary target) |
| **Permission Tiers** | 4-tier: always/allow/ask/deny per tool | State A/B machine: YOLO + Clutch |
| **Autonomous Loop** | Timer-based steward (reversibility heuristic, 3-idle scaling) | Loop steward daemon (`scripts/loop_steward.py`) |
| **Sub-agents** | Explore mode, Worker Fork | model-delegation skill + browser_subagent |
| **Tool Discovery** | Lazy loading via `tool_search` | All skills loaded at session start (no lazy discovery yet) |
| **Feature Flags** | 44 GrowthBook flags (`tengu_*`) + model tier routing | No feature flag system (direct config) |
| **Anti-Distillation** | `__claude_agentic_type` markers, output salting | Undercover mode (`/etc/claude-code/CLAUDE.md`) |
| **Prompt Cache** | Explicit awareness, static-first ordering, 14 break vectors | No API-level caching (no direct API access) |
| **LSP Integration** | Via Cursor (not Claude Code native) | Not implemented (PoC planned) |

## Unique Strengths — Antigravity

1. **Multi-model routing** — Not locked to Anthropic. Can delegate to Gemini, Claude, GPT, Grok.
2. **Compiled security binary (Judge 6)** — External, auditable, not inlined in system prompt.
3. **Skills system** — 90+ modular skills vs Claude Code's monolithic prompt.
4. **SOVEREIGN_GOLD_MASTER tagging** — Immutable codebase snapshots for rollback.
5. **Dream consolidation** — Automated KI maintenance (Claude Code's Dream is manual `/dream` command).
6. **GitNexus code intelligence** — 445K symbols, 685K relationships, 6K clusters.

## Unique Strengths — Claude Code

1. **Prompt cache optimization** — 90% discount on cached tokens, explicit ordering strategy.
2. **4-layer compaction** — Handles 200K+ token sessions gracefully.
3. **tool_search lazy discovery** — Context-efficient skill loading.
4. **GrowthBook feature flags** — A/B testing with server-side rollout.
5. **Native Explore mode** — Read-only sub-agent for research without side effects.
6. **Built-in copyright gate** — ~200 lines of copyright protection logic.

## Adoptable Patterns (Priority Order)

1. ✅ **BLOCK/ALLOW security monitor** — Implemented in Judge 6 spec
2. ✅ **Autonomous loop steward** — Implemented in `scripts/loop_steward.py`
3. ✅ **Dream memory consolidation** — Implemented in `scripts/dream_consolidation.py`
4. 📋 **tool_search lazy discovery** — Planned (Work Stream 6b)
5. 📋 **LSP integration** — Planned (Work Stream 6d)
6. ❌ **Prompt cache optimization** — Not applicable (no direct API access)
