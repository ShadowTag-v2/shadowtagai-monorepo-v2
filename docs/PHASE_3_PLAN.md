# Phase 3 — CounselConduit Sandbox Integration

> Status: **PLANNING** | Started: 2026-04-30 | Target: 2026-05-15

## Objective

Integrate the speculation engine's CoW overlay into CounselConduit's sandbox
execution model, enabling attorneys to preview AI-generated document edits in
an isolated environment before committing to the production database.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              CounselConduit Sandbox                   │
│                                                       │
│  ┌───────────┐   ┌──────────────┐   ┌────────────┐  │
│  │ Attorney   │──▶│ Speculation  │──▶│ CoW Overlay │  │
│  │ UI Review  │   │ Orchestrator │   │ (Isolated)  │  │
│  └───────────┘   └──────────────┘   └──────┬─────┘  │
│                                             │        │
│  ┌───────────┐   ┌──────────────┐          ▼        │
│  │ Accept/    │──▶│ Firestore    │   ┌───────────┐  │
│  │ Reject     │   │ Commit       │◀──│ Diff View  │  │
│  └───────────┘   └──────────────┘   └───────────┘  │
└─────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Sandbox Session API (`/api/sandbox/session`)
- Create isolated CoW overlay for each attorney review session
- Bind to CounselConduit matter ID for privilege tracking
- TTL: 30 minutes (auto-abort on expiry)

### 2. Document Preview (`/api/sandbox/preview`)
- Render speculative document edits in diff view
- Attorney reviews AI suggestions before committing
- Privilege metadata preserved through overlay

### 3. Accept/Reject Flow (`/api/sandbox/commit`)
- Accept: Merge overlay files to Firestore document store
- Reject: Discard overlay, log rejection reason for model tuning
- Partial accept: Cherry-pick specific edits from overlay

### 4. Telemetry Pipeline
- Speculation events → `.beads/speculation_telemetry.jsonl`
- Kairos dashboard reads telemetry for latency monitoring
- Attorney acceptance rate feeds back to suggestion quality tuning

## Security Constraints

1. **Trust Level 0** — Sandbox sessions NEVER use `bypass_permissions`
2. **Matter-scoped isolation** — Each overlay is bound to exactly one matter ID
3. **Attorney-only accept** — Only verified attorneys can commit overlay changes
4. **Audit trail** — All sandbox operations logged to `.beads/` with attorney UID
5. **Privilege preservation** — AI-generated content inherits privilege status from source documents

## Dependencies

- `packages/speculation_engine/orchestrator.py` — SpeculativeResearchOrchestrator
- `packages/speculation_engine/engine.py` — CoW overlay isolation
- `apps/counselconduit/api/` — Existing matter/document APIs
- `firebase-admin` — Firestore document commit
- `packages/context_compactor/` — Context window management for long documents

## Milestones

| # | Milestone | Est. Effort | Status |
|---|-----------|-------------|--------|
| 1 | Sandbox Session API scaffold | 4h | Not started |
| 2 | CoW overlay ↔ Firestore bridge | 8h | Not started |
| 3 | Attorney diff review UI | 6h | Not started |
| 4 | Accept/reject commit flow | 4h | Not started |
| 5 | Telemetry + dashboard wiring | 3h | Not started |
| 6 | Integration tests (12 cases) | 4h | Not started |
| 7 | Security audit + privilege tests | 3h | Not started |

**Total estimated: 32 hours**
