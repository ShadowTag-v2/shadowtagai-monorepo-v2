# NotebookLM IPI Ingestion Pipeline

## Overview
As per the `Cor.NotebookLM TACSOP` and `Dream Consolidation Engine` requirements, all untrusted external data must be routed through NotebookLM for Initial Public Intelligence (IPI) quarantine before it enters the agent context.

## Pipeline Architecture

1. **Collection (`dream_consolidation.py`)**:
   - The daemon collects `.beads/logs/` from the past 24 hours.
   - External inputs (e.g., transcripts, web scrapes) are aggregated.

2. **Quarantine (`vault/quarantine/`)**:
   - The raw text is written to a designated quarantine directory.

3. **NotebookLM Validation**:
   - A sub-agent invokes the NotebookLM MCP to read the quarantined files.
   - The MCP executes strict sanitization:
     - Strips external image URLs and tracking pixels.
     - Neutralizes executable commands (e.g., stripping `curl` payloads).

4. **Consolidation**:
   - The clean intelligence is consolidated into Obsidian-formatted markdown.
   - Written to the `knowledge/` directory as a permanent Knowledge Item (KI).

## Execution Flow
This pipeline ensures the agent never auto-executes or acts directly on poisoned context.
