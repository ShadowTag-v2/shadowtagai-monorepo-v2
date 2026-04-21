# Phase 3: Tenant Isolation Scope Document
# CounselConduit — Sandbox Architecture

## Overview

Phase 3 implements full tenant isolation for CounselConduit, ensuring each law firm
operates in a cryptographically separated sandbox with independently metered resources.

## Architecture

### 1. Tenant Context Layer (IMPLEMENTED)
- `sandbox_router.py` — SandboxMiddleware extracts tenant context from JWT/headers
- Per-tier quotas: trial (50/hr), solo (200/hr), practice (1K/hr), enterprise (10K/hr)
- Request-level quota enforcement via Starlette middleware

### 2. Data Isolation (PLANNED)
- Firestore: Per-firm document paths (`firms/{firm_id}/...`)
- Storage: Per-firm bucket prefixes (`firms/{firm_id}/exports/...`)
- Cloud Tasks: Per-firm queue namespacing
- All cross-firm queries blocked at Firestore rules level

### 3. Compute Isolation (PLANNED)
- Cloud Run Jobs with gVisor runtime for tool execution
- Read-only filesystem (except /tmp)
- Network policy: egress restricted to LiteLLM proxy only
- Resource limits: 2 vCPU, 2Gi RAM, 30s timeout per tool invocation

### 4. Proxy Token Architecture (IMPLEMENTED)
- Ephemeral tokens: 15-min TTL, bound to firm_id + session_id + model
- Token format: `ctx_{sha256_hash[:48]}`
- Token budget: per-session max_tokens enforced at middleware level
- No master keys in sandbox — all tokens scoped and revocable

### 5. LiteLLM Proxy Integration (PLANNED)
- Per-tenant virtual keys via LiteLLM's team/key management
- Model allowlist per tier (trial: flash-lite only, solo: flash+pro, etc.)
- Token counting and budget enforcement at proxy level
- Automatic key rotation on session close

## Security Controls

| Control | Implementation | Status |
|---------|---------------|--------|
| Request isolation | SandboxMiddleware | ✅ LIVE |
| Quota enforcement | Per-tier rate limiting | ✅ LIVE |
| Proxy tokens | Ephemeral, scoped, TTL'd | ✅ LIVE |
| Firestore RLS | Per-firm document rules | 🔧 IN PROGRESS |
| Compute sandbox | Cloud Run Jobs + gVisor | 📋 PLANNED |
| Network policy | Egress firewall | 📋 PLANNED |
| Key rotation | Auto-expire + revoke | 📋 PLANNED |

## Implementation Phases

### Phase 3a: Data Isolation (Current Sprint)
1. ✅ SandboxMiddleware deployed
2. ✅ Per-tier quota enforcement
3. ✅ Proxy token generation
4. 🔧 Firestore per-firm security rules
5. 📋 Storage per-firm bucket prefixes

### Phase 3b: Compute Isolation (Next Sprint)
1. Cloud Run Jobs configuration
2. gVisor runtime selection
3. Tool execution sandboxing
4. Network egress restrictions

### Phase 3c: LiteLLM Integration (Sprint +2)
1. LiteLLM team/key management
2. Per-tenant virtual keys
3. Model allowlist enforcement
4. Token counting at proxy level

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tenant escape via shared memory | CRITICAL | gVisor runtime isolation |
| Quota bypass via header spoofing | HIGH | JWT verification mandatory |
| Proxy token theft | HIGH | 15-min TTL + session binding |
| Cross-firm data leak | CRITICAL | Firestore rules + query scoping |
| Resource exhaustion | MEDIUM | Per-tier quotas + circuit breaker |
