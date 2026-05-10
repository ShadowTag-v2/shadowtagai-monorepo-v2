# TASK: Phase 3 — Sandbox Integration

**Status:** PLANNING
**Created:** 2026-05-04
**Owner:** Antigravity Agent
**Priority:** P0 — Next milestone after v2.2.x stabilization

---

## Objective

Build the CounselConduit Sandbox — attorney-reviewed speculative edit environment
that enables privilege-preserving AI suggestions under Heppner (S.D.N.Y. 2026)
compliance. Three core subsystems.

## Architecture

```
┌─────────────────────────────────────────┐
│           Sandbox Session API            │
│  POST /sandbox/session                   │
│  GET  /sandbox/session/{id}/preview      │
│  POST /sandbox/session/{id}/approve      │
│  POST /sandbox/session/{id}/reject       │
└──────────┬──────────┬──────────┬────────┘
           │          │          │
    ┌──────▼──┐ ┌─────▼────┐ ┌──▼────────┐
    │Spec Prev│ │Att'y Gate│ │Audit Trail│
    │ Engine  │ │ (Review) │ │(Firestore)│
    └─────────┘ └──────────┘ └───────────┘
```

## Deliverables

### D1: Sandbox Session API
- **Endpoint**: `POST /sandbox/session` — create a new sandbox session
- **Endpoint**: `GET /sandbox/session/{id}/preview` — render speculative preview
- **Endpoint**: `POST /sandbox/session/{id}/approve` — attorney approves
- **Endpoint**: `POST /sandbox/session/{id}/reject` — attorney rejects
- **State Machine**: `CREATING → SPECULATING → PREVIEW_READY → APPROVED | REJECTED → ARCHIVED`
- **Security**: JWT-authenticated, attorney role required for approve/reject
- **Storage**: Firestore `sandbox_sessions` collection

### D2: Speculation Preview Engine
- **Integration**: Wire `speculation_engine` (agnt_services stub) to sandbox API
- **Forked Agent**: Use `forked_agent.py` to run speculative edits in isolation
- **Diff Engine**: Generate structured diffs for attorney review
- **Timeout**: 120s max speculation time, circuit breaker on failures

### D3: Attorney Gate (Review Workflow)
- **Two-Factor Approval**: Require attorney + system confirmation
- **Privilege Preservation**: Under Heppner — AI suggestions don't create discoverable work product until attorney approves
- **Audit Trail**: Every approve/reject logged to Firestore with timestamp, attorney ID, and session state
- **Notification**: Terminal notifier + email webhook on session ready for review

## Dependencies

| Dependency | Status | Blocking? |
|------------|--------|-----------|
| speculation_engine port | ⬜ Unported | Yes — D2 |
| forked_agent.py | ✅ Ready | No |
| conversation_recovery.py | ✅ Ready | No |
| Firestore sandbox_sessions schema | ⬜ Not created | Yes — D1 |
| Attorney role in Firebase Auth | ⬜ Not configured | Yes — D3 |
| CounselConduit API /sandbox routes | ⬜ Not created | Yes — D1 |

## Acceptance Criteria

- [ ] Sandbox session lifecycle test (CREATING → ARCHIVED) passes
- [ ] Speculative edit produces reviewable diff within 120s
- [ ] Attorney approve/reject state transitions are idempotent
- [ ] Audit trail entries are queryable by session ID
- [ ] 100% test coverage on state machine transitions
- [ ] Lighthouse SEO/A11y on sandbox preview page ≥ 90
- [ ] Heppner privilege preservation validated (no discoverable edits pre-approval)

## Estimated Effort

| Phase | Hours |
|-------|-------|
| D1: Session API | 8h |
| D2: Speculation Engine | 12h |
| D3: Attorney Gate | 6h |
| Integration Tests | 4h |
| **Total** | **30h** |

## Risk Register Entries

- **Risk #36**: Sandbox escape — speculative edits must be fully isolated
- **Risk #37**: Attorney notification latency — webhook delivery SLA
- **Risk #38**: Firestore write contention under concurrent sessions
