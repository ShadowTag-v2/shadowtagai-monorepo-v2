---
name: epistemic-retention-cascade
description: The absolute doctrine for capturing, overwriting, and cascading learned knowledge to prevent amnesia and ensure token thriftiness across sessions.
utility_score: 1.0
---

# Doctrine: The Epistemic Retention Cascade

As you progress and learn through each iteration, you are forbidden from allowing knowledge to fall off at the next turn. You must constantly step on the shoulders of the past. To avoid I/O bottlenecks, you will execute knowledge retention in this exact 3-Tier Cascade:

### Tier 1: The Instant Lobe (Hot Memory)
*When you learn a new insight, architectural constraint, or bug fix:*
1. Immediately invoke the `anthropic-memory` MCP to update the persistent SQLite knowledge graph.
2. Immediately execute `retain_epistemic_atom` to write the Typed Knowledge Atom to the `.agents/memory_kernel/`.
3. **Overwrite Mandate:** Explicitly delete or mutate outdated atoms. Never allow superseded "wheels from the past" to remain in the hot memory.

### Tier 2: The Agentic Matrix (Warm Memory)
*When the core operational parameters, CLI commands, or prompt environments change:*
1. Update `operator-invariants.md`, `gemini.md`, `claude.md`, and `agent.md` using the Semantic Scalpel (`ast-grep`) or standard file writes.
2. Ensure you OVERWRITE the superseded lines. Do not just append to the bottom of the files; surgically replace the outdated logic.

### Tier 3: The Global Data Plane (Cold/Deferred Memory)
*Do not synchronously write to Google Drive API, Spanner, or BigQuery during a reasoning turn.*
1. Instead, rely on the `dream_consolidation.py` daemon. Because you successfully executed Tier 1, the background daemon will automatically sweep the `memory_kernel`, validate it, and push it to Spanner, BigQuery, and Google Drive asynchronously via the Spreading Activation core.

By following this cascade, you ensure zero data loss, zero regression, and maximum token thriftiness without crashing the execution loop.
