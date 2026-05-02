# AGNT Context Compaction Design

## Overview
This document specifies the 4-layer context compaction architecture for the AGNT platform, directly informed by the forensic analysis of Claude Code's `src/services/compact/` module. The goal is to achieve a ~30% context efficiency advantage by proactively stripping intermediate reasoning, tool use history, and transient logs from the LLM context window.

## The 4-Layer Architecture

### Layer 1: API Micro-Compaction (Server-Side)
*Equivalent to CC's `apiMicrocompact.ts:90`*
- **Mechanism**: Pre-flight stripping of context payloads before transmission to the inference engine.
- **Targets**: `clear_tool_uses`, `clear_thinking`.
- **Implementation**: The agent interceptor evaluates if previous `thinking` blocks and `tool_calls` (where output is already incorporated into the environment) can be stripped from the message history. 
- **Advantage**: Saves raw input tokens and prevents the model from overly anchoring on its past reasoning traces.

### Layer 2: Session Memory Compaction
*Equivalent to CC's `sessionMemoryCompact.ts`*
- **Mechanism**: Summarization and deduplication of the active conversation buffer.
- **Targets**: Redundant error loops, repeated `list_dir` or `view_file` calls.
- **Implementation**: A background `AutoDream` process runs asynchronously when token budget hits 60%. It generates a dense summary of "What was learned/done" and replaces the raw turns with this summary.

### Layer 3: Reactive History Snip
*Equivalent to CC's `historySnip.ts`*
- **Mechanism**: Hard truncation or sliding window optimization when nearing the absolute context limit.
- **Targets**: The oldest N turns in the conversation.
- **Implementation**: Drops the oldest turns but preserves the initial `SYSTEM` prompt, the `USER` goal, and the summarized `Session Memory` from Layer 2.

### Layer 4: Dynamic Token Budget Allocation
*Equivalent to CC's `tokenBudget.ts`*
- **Mechanism**: Resource allocator that reserves specific token pools for different cognitive functions.
- **Targets**: Output generation vs. Context retention.
- **Implementation**: Ensures that even deep in a session, there is always a guaranteed buffer for `thinking` (e.g., reserving 20% of the window for generation and reasoning).

## Implementation Plan (P0)

1. **Scaffold `agnt/services/compact/`**: Create the core utility functions for manipulating the message history list.
2. **Implement `api_microcompact.py`**: Add a hook just before the Gemini API call to strip `<thought>` blocks from prior turns.
3. **Integrate with `Loop Steward`**: Have the 5-minute loop steward proactively trigger Session Memory Compaction during idle cycles.
