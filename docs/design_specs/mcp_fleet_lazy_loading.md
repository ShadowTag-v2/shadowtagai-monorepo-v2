# MCP Fleet Vanguard - Tool Search & Lazy Loading Pattern

## Overview
Informed by the Claude Code intelligence leak (Opus 4.7), we can drastically reduce context window pressure by adopting a `tool_search` and lazy-loading discovery pattern for our MCP Fleet Vanguard.

## Current State vs. Target State
- **Current State**: MCP tools are loaded ahead-of-time (AOT) and their schemas consume significant token budgets in the context window.
- **Target State**: Tools are deferred. The system prompt contains only the `tool_search` function. Tools are loaded via `tool_search` dynamically, preserving the prompt cache prefix.

## Implementation Plan
1. **Tool Registry**: Implement a central, lightweight tool registry in the MCP Vanguard that only maps tool descriptions to their endpoints, without loading the full parameter schemas.
2. **`tool_search` Capability**: Expose a single `tool_search` tool that allows the agent to query tools by keyword, intent, or domain (e.g., "database", "ui", "github").
3. **Lazy Schema Resolution**: When `tool_search` returns a match, the agent requests the full schema via an AOT-append mechanism, ensuring the token budget is only consumed for tools genuinely required by the task at hand.
4. **Cache Awareness**: The implementation must append (not swap) the schemas to maintain explicit prompt breakpoints for optimal caching.
