# TASK.md — Claude Code → Antigravity Porting (STATE B)

> **Status**: ACTIVE | **Phase**: 2A — Services Business Logic
> **Last Updated**: 2026-05-03
> **Source**: `/Users/pikeymickey/Downloads/Claude_Source_Code`
> **Target**: `.agents/skills/` + `packages/`

## Architecture Decision

**Approach**: Selective Pattern Extraction — extract core business logic and orchestration patterns from TypeScript source, port to Python skills and daemon modules. Discard all TUI/Ink/React rendering. Map tools to MCP fleet endpoints.

## Phase Breakdown

### Phase 1 — Utils Foundation Layer
Extract platform-agnostic utilities as Python modules/skills.

| CP | Module | Source Size | Target | Status |
|----|--------|-------------|--------|--------|
| CP-01 | `forkedAgent.ts` | 24KB | `packages/agnt_forked_agent/` | ⬜ |
| CP-02 | `cronScheduler.ts` | 21KB | `packages/cron_scheduler/` | ⬜ |
| CP-03 | `conversationRecovery.ts` | 21KB | `packages/session_recovery/` | ⬜ |
| CP-04 | `toolSearch.ts` | 26KB | `.agents/skills/dynamic-tool-discovery/` | ⬜ |
| CP-05 | `tokenBudget.ts` + `tokens.ts` | 12KB | `packages/token_budget/` | ⬜ |
| CP-06 | `thinking.ts` | 5KB | `packages/thinking_config/` | ⬜ |
| CP-07 | `sessionRestore.ts` | 20KB | `packages/session_recovery/` | ⬜ |
| CP-08 | `config.ts` | 63KB | `.agents/skills/config-management/` | ⬜ |

### Phase 2 — Services Business Logic
Extract service-layer orchestration patterns.

| CP | Module | Source Size | Target | Status |
|----|--------|-------------|--------|--------|
| CP-09 | `services/MagicDocs/` | ~dir | `.agents/skills/magic-docs/` | ⬜ |
| CP-10 | `services/vcr.ts` | 12KB | `packages/vcr_fixtures/` | ⬜ |
| CP-11 | `services/SessionMemory/` | ~dir | `packages/agnt_services/session_memory.py` | ✅ |
| CP-12 | `services/extractMemories/` | ~dir | `packages/agnt_services/extract_memories.py` | ✅ |
| CP-13 | `services/tokenEstimation.ts` | 16KB | `packages/token_budget/` | ⬜ |
| CP-14 | `services/autoDream/` | ~dir | verify vs `dream_consolidation.py` | ⬜ |

### Phase 3 — Tools Architecture
Map tool patterns to MCP fleet.

| CP | Module | Target | Status |
|----|--------|--------|--------|
| CP-15 | `tools/BashTool/` | security model skill | ⬜ |
| CP-16 | `tools/AgentTool/` | subagent orchestration | ⬜ |
| CP-17 | `tools/FileEditTool/` | diff engine patterns | ⬜ |

### Phase 4 — AI Modes (Orchestration)
Map to KAIROS daemon states.

| CP | Module | Target | Status |
|----|--------|--------|--------|
| CP-18 | `buddy/` | KAIROS STATE mappings | ⬜ |
| CP-19 | `coordinator/` | multi-agent orchestration | ⬜ |
| CP-20 | `assistant/` | default mode patterns | ⬜ |

### Phase 5 — Hooks/Components (Headless Adapters)
Strip React, extract lifecycle logic.

| CP | Module | Target | Status |
|----|--------|--------|--------|
| CP-21 | Permission hooks | headless permission gates | ⬜ |
| CP-22 | State management hooks | daemon state machines | ⬜ |

## Exclusions (SKIP)
- All `.tsx` React/Ink rendering components
- Windows-specific paths/PowerShell utilities
- AWS-specific auth modules
- Claude Desktop integration
- Theme/fullscreen/UI animation code

## Already Implemented (VERIFIED)
- Context compaction → `packages/context_compactor/`
- Speculation engine → `packages/speculation_engine/`
- AutoDream → `scripts/dream_consolidation.py` (verify parity in CP-14)
- Ant gates analysis → KI `cor_ant_source_code_gates`
- Feature flags → KI `ccleaks_deep_fold_in_part_3`
- **StreamingWatchdog** → `packages/agnt_services/watchdog.py` (10 tests)
- **AgentSummarizer** → `packages/agnt_services/agent_summary.py` (12 tests)
- **SessionMemoryManager** → `packages/agnt_services/session_memory.py` (9 tests) — CP-11
- **MemoryExtractor** → `packages/agnt_services/extract_memories.py` (17 tests) — CP-12
