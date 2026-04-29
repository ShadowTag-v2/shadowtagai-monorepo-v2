# Digital Privilege Shield — Architecture Document

> **Version**: v1.0 | **Last Updated**: 2026-04-22
> **Classification**: Internal Architecture — Not for external distribution
> **Legal Basis**: *United States v. Heppner*, S.D.N.Y., Feb. 10, 2026

---

## Overview

The Digital Privilege Shield (DPS) is the technical infrastructure that preserves attorney-client privilege across AI-assisted client communications. It is the core differentiator that separates CounselConduit from every other legal AI product: **we are the only platform with cryptographic proof of privilege**.

---

## Privilege Flow Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     DIGITAL PRIVILEGE SHIELD                         │
│                                                                      │
│  ┌─────────┐    ┌─────────────┐    ┌───────────┐    ┌────────────┐  │
│  │ Client   │───▶│ Intake Gate │───▶│ Privilege │───▶│ Kovel      │  │
│  │ Browser  │    │ (S.E.U.)   │    │ Envelope  │    │ Attestation│  │
│  └─────────┘    └─────────────┘    └───────────┘    └────────────┘  │
│       │               │                  │                │         │
│       │          ┌────┴────┐        ┌───┴────┐      ┌───┴────┐    │
│       │          │ Empathy │        │ Judge 6│      │ HMAC   │    │
│       │          │ Layer   │        │ Policy │      │ SHA256 │    │
│       │          └─────────┘        └────────┘      └────────┘    │
│       │                                                   │         │
│       ▼                                                   ▼         │
│  ┌─────────┐    ┌─────────────┐    ┌───────────┐    ┌────────────┐  │
│  │ Dead-   │    │ LLM Router  │    │ Oracle    │    │ Privileged │  │
│  │ Man's   │───▶│ (NadirClaw) │───▶│ Studio    │───▶│ Transcript │  │
│  │ Switch  │    │             │    │ 7-Stage   │    │            │  │
│  └─────────┘    └─────────────┘    └───────────┘    └────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Component Deep Dives

### 1. Kovel Attestation Engine (`kovel_attestation.py`)

**Purpose**: Generate cryptographic proof that a communication occurred under attorney-client privilege.

**How It Works**:
1. Attorney registers with CounselConduit via Stripe Connect (establishes retention)
2. Client accesses portal through attorney's branded link (establishes the relationship)
3. Every session generates a Kovel attestation receipt containing:
   - `session_id` (UUIDv7)
   - `tenant_id` (firm identifier)
   - `attorney_bar_number` (verified)
   - `session_start` / `session_end` timestamps
   - `communication_purpose: "legal_advice"` (Kovel requirement)
   - `hmac_signature` (HMAC-SHA256 of all fields)
4. Receipt is stored immutably in Firestore `kovel_attestations/{tenant_id}/{session_id}`
5. Receipt is exportable for litigation hold or privilege log

**HMAC-SHA256 Flow**:
```python
payload = f"{session_id}:{tenant_id}:{attorney_bar}:{start}:{end}:legal_advice"
signature = hmac.new(secret_key, payload.encode(), hashlib.sha256).hexdigest()
```

**Attestation Receipt JSON**:
```json
{
  "attestation_version": "1.0",
  "session_id": "01926e4a-7b3c-7def-8901-234567890abc",
  "tenant_id": "firm_smith_associates",
  "attorney_bar_number": "NY-123456",
  "communication_purpose": "legal_advice",
  "kovel_basis": "United States v. Kovel, 296 F.2d 918 (2d Cir. 1961)",
  "heppner_authority": "United States v. Heppner, S.D.N.Y. (Feb. 10, 2026)",
  "session_start": "2026-04-22T10:00:00Z",
  "session_end": "2026-04-22T10:47:23Z",
  "message_count": 14,
  "hmac_sha256": "a3f8c2d1e4b5a6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1",
  "privilege_status": "ACTIVE",
  "export_allowed": true,
  "retention_days": 2555
}
```

---

### 2. Dead-Man's Switch (`silent_detector.py` + client-side)

**Purpose**: Ensure ephemeral session integrity — no orphaned active sessions.

**Architecture**:
```
Client Browser                    Server
     │                              │
     │── heartbeat (30s interval) ──▶│
     │                              │── update session_pins.last_seen
     │                              │
     │   [user inactive 5 min]      │
     │                              │── detect silence
     │                              │── trigger auto-logout
     │                              │── wipe client-side state
     │                              │── generate session summary
     │                              │── close Kovel attestation
     │                              │
     │◀── screen wipe signal ───────│
     │                              │
```

**Key Properties**:
- No "are you still there?" prompts (breaks the Invisible Meter)
- Client-side JavaScript wipes all state on disconnect
- Server-side Firestore TTL cleans up session_pins
- Attorney is notified of completed session via Google Workspace alerts

---

### 3. Privilege Envelope (Transport Layer)

**Purpose**: Every LLM interaction is wrapped in a privilege envelope that prevents privilege-breaking outputs.

**Envelope Structure**:
```
┌─ Privilege Envelope ──────────────────────────────────┐
│                                                        │
│  [HEADER]                                              │
│  • session_id: UUIDv7                                  │
│  • tenant_id: firm identifier                          │
│  • privilege_status: ACTIVE                            │
│  • kovel_attestation_id: receipt reference              │
│                                                        │
│  [S.E.U. WRAPPER]                                      │
│  • SAFETY: Judge 6 directives                          │
│  • EMPATHY: Randomized acknowledger (24+ variants)     │
│  • UTILITY: Actual legal query                         │
│                                                        │
│  [MODEL ROUTING]                                       │
│  • provider: gemini-2.5-flash                          │
│  • fallback: claude-sonnet-4                           │
│  • circuit_breaker: CLOSED                             │
│                                                        │
│  [JUDGE 6 GATE]                                        │
│  • scope_check: PASS                                   │
│  • privilege_check: PASS                               │
│  • ethics_check: PASS                                  │
│  • risk_score: 0.12 (LOW)                              │
│                                                        │
│  [FOOTER]                                              │
│  • response_hmac: [signature of response content]      │
│  • empathy_fingerprint: [verification hash]            │
│  • timestamp: ISO 8601                                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 4. Privilege Metadata Chain

**Purpose**: Complete audit trail from session initiation to privileged document export.

```
Session Created
    │
    ▼
Kovel Attestation Generated
    │
    ▼
S.E.U. Intake (Safety → Empathy → Utility)
    │
    ▼
Oracle Studio 7-Stage Processing
    │
    ▼
Judge 6 Policy Gate
    │
    ▼
Privileged Response Delivered
    │
    ▼
Empathy Fingerprint Verified
    │
    ▼
Transcript Stored (Firestore, encrypted at rest)
    │
    ▼
Session Closed (Dead-Man's Switch or explicit)
    │
    ▼
Attestation Finalized (HMAC sealed)
    │
    ▼
Attorney Notified (Google Workspace)
    │
    ▼
Brief Available (Privileged Export)
```

---

### 5. Threat Model

| Threat | Mitigation | Implementation |
|--------|-----------|----------------|
| Opposing counsel subpoenas AI logs | Privilege applies per Heppner; attestation receipts prove basis | `kovel_attestation.py` |
| Prompt injection strips empathy layer | Empathy fingerprinting detects mutation | `empathy_templates.py` |
| Client session hijacked | UUIDv7 session IDs + tenant-scoped auth + Dead-Man's Switch | `auth.py` + `silent_detector.py` |
| LLM returns privilege-breaking content | Judge 6 policy gate blocks before delivery | `Claude_Code_6.py` |
| Data breach exposes transcripts | Firestore encryption at rest + per-tenant namespace isolation | `firestore_client.py` |
| AI impersonates attorney | S.E.U. wrapper explicitly identifies as AI assistance | `empathy_templates.py` |
| Unauthorized transcript export | Kovel attestation required for export; GDPR 30-day TTL | `gdpr.py` |

---

## Production Status

| Component | File | Status | Lines |
|-----------|------|--------|-------|
| Kovel Attestation | `api/kovel_attestation.py` | ✅ LIVE | 7,684 B |
| Dead-Man's Switch | `api/silent_detector.py` | ✅ LIVE | 2,121 B |
| Judge 6 Gate | `api/Claude_Code_6.py` | ✅ LIVE | 6,828 B |
| Empathy Templates | `api/empathy_templates.py` | ✅ LIVE | 9,033 B |
| S.E.U. Wrapper | `api/empathy_templates.py:wrap_seu_prompt()` | ✅ LIVE | — |
| Oracle Studio | `api/oracle_studio.py` | ✅ LIVE | 14,226 B |
| NadirClaw Router | `api/dispatch_router.py` | ✅ LIVE | 37,723 B |
| Session Pin Monitor | `api/session_pin_monitor.py` | ✅ LIVE | 2,823 B |
| Model Router | `api/model_router.py` | ✅ LIVE | 17,144 B |
| Vent Mode | `api/vent_mode.py` | ✅ LIVE | 12,662 B |
