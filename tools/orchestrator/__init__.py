"""Orchestrator tools — context management and session orchestration layer.

Modules:
    memory_indexer   - Three-Layer Context Memory (hot/warm/cold)
    compaction_engine - Context compaction with circuit breakers
    session_forking  - Horizontal work unit chunking for dense edits
    in_process_mcp   - Native MCP bypass for zero-IPC tool execution
"""
