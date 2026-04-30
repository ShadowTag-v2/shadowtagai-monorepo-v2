# Panopticon

> Gideon OS Block 7 — Full-Stack Observability Engine

## Purpose

Panopticon provides unified observability across the entire Gideon OS stack. It collects, correlates, and surfaces metrics, logs, and traces from all 14 blocks, enabling proactive anomaly detection and incident response.

## Architecture

```
┌───────────────────────────────────────────────────┐
│                Panopticon                          │
├───────────────────────────────────────────────────┤
│                                                    │
│  ┌────────────────────────────────────────────┐   │
│  │          Telemetry Collector               │   │
│  │  • AGNT Event Catalog (34+ events)        │   │
│  │  • Cloud Run metrics (latency, 5xx rate)  │   │
│  │  • Firestore operation counts             │   │
│  │  • MCP server health probes               │   │
│  └──────────────┬─────────────────────────────┘   │
│                 │                                   │
│  ┌──────────────▼─────────────────────────────┐   │
│  │        Correlation Engine                  │   │
│  │  • Cross-service trace linking             │   │
│  │  • Anomaly detection (3σ deviation)        │   │
│  │  • Regression detection (VCR diff mode)    │   │
│  └──────────────┬─────────────────────────────┘   │
│                 │                                   │
│  ┌──────────────▼─────────────────────────────┐   │
│  │          Alert Router                      │   │
│  │  → AdminLTE GlassBox (dashboard)          │   │
│  │  → .beads/issues.jsonl (audit trail)      │   │
│  │  → GCP Alert Policies (8 active)          │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
└───────────────────────────────────────────────────┘
```

## Event Categories

| Category | Events | Source |
|----------|--------|--------|
| API | `agnt_api_success/error/retry` | Gemini API calls |
| Compaction | `agnt_compact_started/success/failed` | Context compaction |
| Tool | `agnt_tool_use_success/error` | Tool execution |
| Classifier | `agnt_classifier_outcome` | Permission decisions |
| Shell | `agnt_bash_classifier` | Bash security |
| Memory | `agnt_memory_compact` | Session memory |
| VCR | `agnt_vcr_record/replay/diff` | Record/replay |
| Session | `agnt_session_started/ended` | Session lifecycle |

## Sink Architecture

Events are emitted through a killswitch-enabled sink pipeline:
1. **Buffer**: Events accumulated (default: 10 events)
2. **Sink**: Writes to JSONL files in `.beads/telemetry/`
3. **Killswitch**: Feature-flag controlled per-event-type suppression
4. **Export**: Optional forward to GCP Cloud Monitoring

## Integration Points

- **Telemetry Catalog**: `packages/telemetry/catalog.py` (468 lines, 34+ events)
- **AdminLTE GlassBox**: Real-time dashboard display
- **Kairos Supervisor**: Daemon health monitoring
- **GCP Alert Policies**: 8 active policies for production alerting

## Status

🟢 Active — Event catalog implemented, sink pipeline operational, GCP alerts configured.
