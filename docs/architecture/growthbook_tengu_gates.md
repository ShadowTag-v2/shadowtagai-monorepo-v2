# GrowthBook Feature Flags — `tengu_*` Namespace Documentation

> Source: Claude Code source leak (`cc_feature_flags_catalog.md`, Rule 16)

## Overview

Claude Code uses GrowthBook (server-side) with the `tengu_*` prefix namespace for all feature flags.
This document catalogues the 44 known flags for competitive intelligence purposes.

## Flag Categories

### Model Routing (6 flags)
| Flag | Purpose | Default |
|------|---------|---------|
| `tengu_model_tier` | Select model tier (opus/sonnet/haiku) | sonnet |
| `tengu_thinking_budget` | Max thinking tokens | varies |
| `tengu_max_output_tokens` | Output token limit | 16384 |
| `tengu_context_window_size` | Effective context window | 200000 |
| `tengu_extended_thinking` | Enable extended thinking mode | true |
| `tengu_model_routing_version` | Routing algorithm version | v3 |

### Context Management (8 flags)
| Flag | Purpose | Default |
|------|---------|---------|
| `tengu_auto_compact` | Enable automatic compaction | true |
| `tengu_compact_threshold` | Token count trigger | ~167000 |
| `tengu_microcompact_enabled` | Stale tool result pruning | true |
| `tengu_history_snip_enabled` | Nuclear truncation | true |
| `tengu_max_retained_files` | Files kept post-compact | 5 |
| `tengu_summary_budget` | Summary generation token budget | 50000 |
| `tengu_cache_prefix_strategy` | Prompt cache ordering | static_first |
| `tengu_prompt_cache_enabled` | Enable prompt caching | true |

### Memory (5 flags)
| Flag | Purpose | Default |
|------|---------|---------|
| `tengu_memory_enabled` | Enable memory persistence | true |
| `tengu_dream_enabled` | Enable Dream consolidation | true |
| `tengu_dream_schedule` | Dream cycle timing | nightly |
| `tengu_memory_max_entries` | Max memory items | 200 |
| `tengu_memory_poisoning_check` | Enable poisoning detection | true |

### Security (7 flags)
| Flag | Purpose | Default |
|------|---------|---------|
| `tengu_security_monitor_version` | BLOCK/ALLOW rules version | v4 |
| `tengu_permission_tier` | Default permission level | ask |
| `tengu_composite_eval_depth` | Chain evaluation depth | 50 |
| `tengu_encoding_detection` | Detect base64/xxd bypass | true |
| `tengu_anti_distillation` | Enable output markers | true |
| `tengu_copyright_check_enabled` | Copyright gate | true |
| `tengu_secret_scan_enabled` | Scan for leaked secrets | true |

### Agent Loop (8 flags)
| Flag | Purpose | Default |
|------|---------|---------|
| `tengu_autonomous_mode` | Enable autonomous loop | false |
| `tengu_steward_interval` | Loop cycle interval (ms) | 300000 |
| `tengu_max_idle_cycles` | Idle before scale-back | 3 |
| `tengu_tool_search_enabled` | Lazy tool discovery | true |
| `tengu_explore_mode` | Read-only sub-agent | true |
| `tengu_worker_fork_enabled` | Fork parallel workers | false |
| `tengu_max_tool_calls_per_turn` | Per-turn tool limit | 25 |
| `tengu_agent_timeout` | Autonomous mode timeout (min) | 60 |

### UI/UX (6 flags)
| Flag | Purpose | Default |
|------|---------|---------|
| `tengu_fast_mode` | Enable fast mode indicator | true |
| `tengu_ultrathink_indicator` | Show thinking progress | true |
| `tengu_markdown_rendering` | Render markdown in terminal | true |
| `tengu_progress_bar_enabled` | Show operation progress | true |
| `tengu_buddy_enabled` | Enable Buddy assistant | false |
| `tengu_undercover_mode` | Stealth operation mode | false |

### Experimental (4 flags)
| Flag | Purpose | Default |
|------|---------|---------|
| `tengu_lsp_integration` | LSP queries | false |
| `tengu_computer_use` | Computer use tool | false |
| `tengu_skillify_enabled` | Session-to-skill conversion | true |
| `tengu_batch_api_enabled` | Batch API mode | false |

## Our Analogues

| GrowthBook Flag | Our Implementation |
|-----------------|-------------------|
| `tengu_auto_compact` | `.claude/rules/11-compaction-pipeline.md` |
| `tengu_memory_enabled` | KI system + brain/ session persistence |
| `tengu_dream_enabled` | `scripts/dream_consolidation.py` |
| `tengu_security_monitor_version` | `docs/architecture/judge6_block_allow_spec.md` |
| `tengu_autonomous_mode` | `scripts/loop_steward.py` |
| `tengu_permission_tier` | State A/B machine in GEMINI.md |
| `tengu_anti_distillation` | `/etc/claude-code/CLAUDE.md` UNDERCOVER section |

## Recommendation

We do NOT need a feature flag system for the current monorepo. Our `.claude/rules/` modular files serve the same purpose — each rule can be toggled by adding/removing the file. If we need runtime toggling for CounselConduit production, use Google Cloud Remote Config (Firebase-native) instead of GrowthBook.
