# Kairos Supervisor

> Gideon OS Block 2 — Autonomous Task Orchestration Engine

## Purpose

Kairos Supervisor is the central task orchestration engine for Gideon OS. It implements the Tri-Partite Cognitive Architecture (TACSOP 4) by coordinating the Brainstem (MCP servers), Hippocampus (NotebookLM + Obsidian), and Motor Cortex (skill acquisition) layers.

## Architecture

```
┌──────────────────────────────────────────────────┐
│              Kairos Supervisor                    │
├──────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │         Task Queue (Cloud Tasks)            │  │
│  │  • Priority ordering                        │  │
│  │  • Retry with exponential backoff           │  │
│  │  • Dead letter queue for failures           │  │
│  └──────────────┬──────────────────────────────┘  │
│                 │                                  │
│  ┌──────────────▼──────────────────────────────┐  │
│  │         Daemon Fleet Manager                │  │
│  │  • Dream Consolidation (nightly KI)         │  │
│  │  • Loop Steward (5-min task continuation)   │  │
│  │  • Omni-Autolint (daily 3-5AM)             │  │
│  │  • pnkln-evolve (skill evolution)           │  │
│  └──────────────┬──────────────────────────────┘  │
│                 │                                  │
│  ┌──────────────▼──────────────────────────────┐  │
│  │       Zero-Day Matrix (TACSOP 4)            │  │
│  │  • Dynamic skill acquisition                │  │
│  │  • Capability gap detection                 │  │
│  │  • Auto-install from google/skills          │  │
│  └─────────────────────────────────────────────┘  │
│                                                   │
└──────────────────────────────────────────────────┘
```

## Daemon Fleet

| Daemon | Script | Schedule | Purpose |
|--------|--------|----------|---------|
| Dream Consolidation | `scripts/dream_consolidation.py` | Nightly | KI maintenance |
| Loop Steward | `scripts/loop_steward.py` | 5-min cycles | Task continuation |
| Omni-Autolint | `scripts/gca_autolint_daemon.py` | Daily 3-5AM | Lint + push |
| pnkln-evolve | `scripts/pnkln_evolve.py` | Background | Skill evolution |
| COR.COR.KAIROS | `scripts/kairos_daemon.py` | Background | Autonomous agent |

## Key Features

| Feature | Description |
|---------|-------------|
| Google Cloud Tasks | Exclusive queue broker (BullMQ banned) |
| Execution Ledger | Numbered CP-IDs with timestamps in task.md |
| Asynchronous Cascade | 5+ steps execute without stopping |
| Circuit Breaker | Auto-disables failing subsystems |
| State Machine | STATE A (YOLO) ↔ STATE B (Clutch) transitions |

## Integration Points

- **Panopticon**: Receives task execution telemetry
- **Vault Constitution**: Task-level authorization checks
- **Genesis Bootstrapper**: Initial daemon fleet provisioning
- **AdminLTE GlassBox**: Daemon status monitoring

## Status

🟢 Active — Daemon fleet operational. 5 daemons registered and running.
