# DESIGN: AGNT Context Compaction System

**Objective:** Implement a 4-layer context compaction architecture modeled on CC's pipeline to preserve LLM token budgets and maintain semantic continuity across prolonged sessions.

## Architecture Layers

### Layer 1: Micro-Compaction (Pipe Truncation)
**Responsibility:** Immediate token defense during tool execution.
- Intercepts \`stdout\` / \`stderr\` output.
- Enforces strict upper bounds (e.g., 2000 lines, 20MB) at the tool interface.
- Summarizes excessive outputs dynamically using an embedded "fast" model or naive regex truncator before passing the result to the main context.

### Layer 2: Temporal Branch Deduplication
**Responsibility:** Eliminating overlapping execution pathways.
- Replaces flat history logs with conversational graphs.
- Identifies identical origin points (root prompts).
- Prunes redundant branches by measuring \`user_message_count\` and session duration, preserving only the most successful traversal path (similar to \`deduplicateSessionBranches\`).

### Layer 3: Consolidation (Dream & Extract)
**Responsibility:** Transforming raw events into structured epistemic knowledge.
- Periodic daemon (\`loop_steward\` or nightly \`dream_consolidation\`).
- Extracts project areas, friction points, and capabilities using specialized summarization prompts.
- Synthesizes findings into dense, high-signal artifacts (e.g., \`MEMORY.md\`, \`DESIGN.md\`) that provide high-value context at minimal token cost.

### Layer 4: Pruning (Cold Storage)
**Responsibility:** Historical archiving and index eviction.
- Archiving sessions inactive past a defined TTL (e.g., 30 days) to cold storage (\`_archive_*\` directories).
- Offloading massive text arrays to an external vector store (like ChromaDB or LanceDB) that can be accessed via semantic search instead of occupying the live LLM context window.

## Integration Plan
- Implement the Layer 1 truncate hooks directly into the Bash and File Read tools.
- Bind the Layer 3 Consolidation routine to the existing \`dream_consolidation.py\` daemon.
- Use the Epistemic Knowledge pattern to handle Layer 4 structured retrievals.
