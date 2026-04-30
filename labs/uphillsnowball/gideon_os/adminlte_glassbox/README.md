# AdminLTE GlassBox

> Gideon OS Block 11 — Transparent Admin Dashboard

## Purpose

AdminLTE GlassBox is the administrative monitoring and control dashboard for the Gideon OS sovereign infrastructure. It provides a transparent ("glass box") view into all system operations, replacing opaque admin panels with full observability into every subsystem.

## Architecture

```
┌──────────────────────────────────────────────┐
│           AdminLTE GlassBox Dashboard        │
├──────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Metrics  │  │ Alerts   │  │ Controls │  │
│  │ Panel    │  │ Stream   │  │ Console  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
├──────────────────────────────────────────────┤
│  WebSocket Backbone → Panopticon Telemetry   │
│  RBAC via Vault Constitution                 │
│  CSP: strict-dynamic, no unsafe-eval         │
└──────────────────────────────────────────────┘
```

## Key Components

| Component | Purpose |
|-----------|---------|
| Metrics Panel | Real-time system metrics (CPU, memory, Firestore ops, Cloud Run latency) |
| Alert Stream | Live feed from Panopticon anomaly detection |
| Controls Console | Administrative actions with RBAC enforcement |
| Audit Log Viewer | Searchable `.beads/issues.jsonl` browser |
| Feature Flag Manager | Runtime toggle for AGNT_FC_OVERRIDES (Gates tab) |

## Security

- All admin routes require `roles/admin` from Vault Constitution
- CSP headers enforced: `script-src 'strict-dynamic'`
- HSTS with preload, 1-year max-age
- Audit logging for every administrative action
- No `unsafe-eval` — all scripts are hash-verified

## Integration Points

- **Panopticon**: Receives telemetry streams via WebSocket
- **Kairos Supervisor**: Task queue monitoring and control
- **Vault Constitution**: RBAC policy enforcement
- **Sovereign Infra TF**: Infrastructure state display

## Status

🔶 Scaffolded — UI framework selected, awaiting integration with live telemetry feeds.
