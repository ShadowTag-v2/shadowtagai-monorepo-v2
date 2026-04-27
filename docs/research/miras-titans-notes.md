# MIRAS & Titans — Research Notes

> **Status:** Reference | **Category:** Architecture Research
> **Source:** Google DeepMind publications + internal design sessions
> **Last updated:** 2026-04-27

## Overview

MIRAS (Multi-scale Information Retention and Adaptive Selection) and Titans are
architectures for efficient long-context processing in transformer models. These
notes capture the four key design choices relevant to our Monorepo OS memory layer.

## The Four Design Choices (MIRAS)

### 1. Surprise-Based Memory Triage

- **Principle:** Not all information is equally important. Memory should prioritize
  "surprising" inputs — those that deviate from the model's current predictions.
- **Mechanism:** Compute a surprise score (prediction error) for each input chunk.
  High-surprise chunks are written to long-term memory; low-surprise chunks are
  compressed or discarded.
- **Our application:** `.memory/atoms/` acts as our long-term store. The
  `beads-capture.sh` script's type system (fact/decision/event/issue) maps to
  different surprise thresholds — decisions and issues are inherently high-surprise
  (they change behavior), while events and facts may be routine.

### 2. Multi-Scale Retention

- **Principle:** Memory operates at multiple time horizons simultaneously:
  working memory (current context), episodic memory (session-level), and
  semantic memory (permanent knowledge).
- **Mechanism:** Maintain parallel memory stores with different retention policies
  and access patterns.
- **Our application:**
  | Layer | Store | Retention | Access Pattern |
  |-------|-------|-----------|----------------|
  | Working | `.beads/session_handoff.json` | Per-session | Read on boot |
  | Episodic | `.beads/issues.jsonl` + `.memory/events.ndjson` | Append-only | Query by status/type |
  | Semantic | `.memory/atoms/` + KI system | Permanent | Search by topic |

### 3. Adaptive Context Selection

- **Principle:** When context budget is limited, dynamically select which stored
  memories to inject into the active context.
- **Mechanism:** Relevance scoring between the current task and stored memories,
  with a retrieval budget.
- **Our application:** The `repo-oracle` script implements this — given a task
  description, it searches across atoms, beads, and KIs to surface relevant
  context before the agent starts coding. The `context-budget-discipline` skill
  enforces the 4-layer microcompact pipeline.

### 4. Hierarchical Compression

- **Principle:** Older memories should be progressively compressed — retaining
  key signals while reducing storage cost.
- **Mechanism:** Periodic consolidation passes that summarize clusters of
  memories into higher-level abstractions.
- **Our application:** The `dream_consolidation.py` daemon runs nightly to
  merge daily append-only logs into persistent KIs. The
  `ag-context-compactor` skill manages the 4-layer pipeline:
  raw events → session summaries → KIs → doctrinal truths.

## Titans Architecture Relevance

Titans extends MIRAS with:

1. **Memory as a neural module** — Separate trainable memory modules that
   persist across forward passes. For us, this maps to the MCP sequential-thinking
   server's ability to maintain reasoning chains across tool calls.

2. **Attention over memory banks** — Rather than fixed retrieval, use learned
   attention to dynamically weight stored memories. Our `repo-oracle` implements
   a simplified version using keyword + semantic search.

3. **Forgetting mechanism** — Active forgetting prevents memory bloat. Our
   `dream_consolidation.py` implements this via the prune phase, and
   `.memory/config.yaml` defines retention windows.

## References

- Behrouz et al., "Titans: Learning to Memorize at Test Time" (2024)
- MIRAS framework: multi-scale information retention in transformers
- ShadowTag implementation: `docs/UPHILLSNOWBALL_ARCHITECTURE.md`
- Memory config: `.memory/config.yaml`
- Dream consolidation: `scripts/dream_consolidation.py`
