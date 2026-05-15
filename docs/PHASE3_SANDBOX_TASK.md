# Phase 3: Sandbox Session API — TASK.md

> **Status**: PLANNING | **Activation**: Requires STATE B Board Review
> **Created**: 2026-05-04
> **Effort Estimate**: 4h implementation + 1h board review

## Objective

Build the attorney-reviewed speculative edit sandbox for CounselConduit Phase 3. This enables lawyers to preview AI-generated document edits in a controlled environment before committing them to the official record.

## Architecture

```
┌──────────────────────────────────────┐
│ CounselConduit Dashboard (Next.js)   │
│  └─ SandboxPanel component           │
│     └─ Diff viewer (Monaco)          │
├──────────────────────────────────────┤
│ Sandbox Session API (Cloud Run)      │
│  ├─ POST /sandbox/sessions           │
│  ├─ GET  /sandbox/sessions/:id       │
│  ├─ POST /sandbox/sessions/:id/apply │
│  └─ DELETE /sandbox/sessions/:id     │
├──────────────────────────────────────┤
│ Firestore: sandbox_sessions/{id}     │
│  ├─ attorney_id (ref → users)        │
│  ├─ matter_id (ref → matters)        │
│  ├─ original_doc (text)              │
│  ├─ proposed_edit (text)             │
│  ├─ diff_html (computed)             │
│  ├─ status: DRAFT|REVIEW|APPROVED    │
│  ├─ reviewed_at (timestamp)          │
│  └─ applied_at (timestamp|null)      │
└──────────────────────────────────────┘
```

## Deliverables

| # | Task | Target | Status |
|---|------|--------|--------|
| D1 | Firestore schema: `sandbox_sessions` collection | `firestore.rules` + collection design | ⬜ |
| D2 | Sandbox Session API endpoints (CRUD) | `services/counselconduit/sandbox.py` | ⬜ |
| D3 | Attorney review workflow (DRAFT→REVIEW→APPROVED) | State machine in API | ⬜ |
| D4 | Diff computation engine (Firestore-backed) | `packages/diff_engine/` | ⬜ |
| D5 | Privilege-preserving LLM routing integration | Heppner compliance gate | ⬜ |
| D6 | SandboxPanel frontend component | `apps/counselconduit-dashboard/` | ⬜ |

## Security Requirements

- Attorney identity verified via Firebase Auth + GCIP SAML
- All sandbox sessions scoped to `matter_id` with attorney-level ACL
- No sandbox data persisted beyond 72h without explicit attorney approval
- Audit trail: every sandbox action logged to `audit_events` collection
- Privilege assertion: LLM cannot see documents outside the sandbox scope

## STATE B Activation Checklist

Before implementation begins, the 8-Agent Board must review:

- [ ] CTO: Architecture approval (Cloud Run + Firestore)
- [ ] DX: Developer experience for sandbox API consumers
- [ ] Security: Privilege boundary review (Heppner compliance)
- [ ] Money: Cost impact (Firestore reads/writes per session)
- [ ] Infra: Cloud Run scaling parameters
- [ ] QA: Test strategy (Hypothesis + integration)
- [ ] Legal: Data retention policy (72h default)
- [ ] UX: Attorney review workflow usability

## Dependencies

- GCIP multi-tenant SAML/OIDC (Enterprise SSO)
- CounselConduit Dashboard (Next.js app, 4h build)
- Firestore matter collection migration (E2E xfails blocker)
