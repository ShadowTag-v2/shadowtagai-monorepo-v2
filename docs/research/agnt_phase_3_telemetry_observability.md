# Phase 3: Telemetry & Observability (Deep Map)

## Overview
Phase 3 of the AGNT STATE B Implementation focuses on bringing Claude Code's extensive observability (Tengu metrics) into the local, zero-trust AGNT ecosystem. This ensures we have high-fidelity debugging data without exfiltrating telemetry to external servers.

## Components

### 1. `tengu_*` Telemetry Catalog Port
We will map the 34+ internal Claude Code telemetry events to our local `.beads/telemetry.jsonl` sink. 
**Implementation Target**: `packages/agnt_telemetry/sink.py`
- Events will be strictly typed via Pydantic (`TelemetryEvent`).
- Rotation policy: `.jsonl` files rotated daily and capped at 50MB.

### 2. `antModels.ts` Codename Mapping
Accurate billing and latency predictions rely on mapping the internal codenames (e.g., `claude-3-7-sonnet-20250219`) to their exact capabilities.
**Implementation Target**: `packages/agnt_telemetry/models.py`
- We will track model costs internally using `tengu_api_request_completed` and calculate exact token costs dynamically.

### 3. Omni-Linter Telemetry Integration
We need to capture AST mutations during the TACSOP 5 self-healing process.
**Implementation Target**: `packages/omni_linter/telemetry_plugin.py`
- Every time `ruff --fix` or `ast-grep` mutates a file, we log a `tengu_file_written` equivalent event, capturing the diff size and rule triggered.

### 4. VCR Record/Replay
The deterministic testing subsystem already implemented in `agnt_vcr` will be instrumented.
**Implementation Target**: `packages/agnt_vcr/` (Integration)
- We will log `tengu_vcr_recorded` and `tengu_vcr_replayed` events to understand test suite coverage.
- Full API payloads (sanitized of secrets) will be stored in `.beads/cassettes/`.

## Log Rotation Policy (Local)
To prevent disk bloat from the telemetry sink:
1. Active file: `.beads/telemetry.jsonl`
2. At midnight (or 50MB): gzip to `.beads/telemetry_YYYY-MM-DD.jsonl.gz`
3. Retention: Keep 7 days, auto-delete older archives via the `Dream Consolidation Engine`.
