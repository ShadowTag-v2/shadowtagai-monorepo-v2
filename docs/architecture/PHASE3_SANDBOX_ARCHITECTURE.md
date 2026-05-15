# Phase 3: Sandbox Isolation Architecture

> Status: PLANNING | Target: Phase 3 (Day 46+)
> Depends on: Phase 2 ✅ LIVE

## Overview

Phase 3 introduces tenant-isolated sandbox execution for CounselConduit,
enabling secure tool runners, read-only filesystem access, and ephemeral
proxy tokens for each law firm tenant.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Client (Lawyer / Client Portal)                        │
├─────────────────────────────────────────────────────────┤
│  Cloud Run: CounselConduit API (existing)               │
│  ├── Auth Middleware (JWT validation)                    │
│  ├── Tenant Context (firm_id extraction)                │
│  └── Sandbox Router                                     │
│       ├── Tool Sandbox (gVisor / Cloud Run Jobs)        │
│       ├── LiteLLM Proxy (short-lived tokens)            │
│       └── File Sandbox (read-only /tmp mount)           │
├─────────────────────────────────────────────────────────┤
│  Firestore: Per-tenant collections (existing)           │
│  Cloud Tasks: GDPR + async operations (existing)        │
│  Secret Manager: Tenant BYOK keys (new)                 │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Sandbox Router
- Routes each request through tenant context + permission check
- Enforces per-tenant resource quotas (CPU, memory, API calls)
- Logs all tool invocations to audit trail

### 2. Tool Sandbox (gVisor)
- Cloud Run Jobs with gVisor runtime for untrusted code execution
- 5-minute maximum execution time
- No network access except allowlisted endpoints
- Read-only filesystem (code supplied via environment)

### 3. LiteLLM Proxy Tokens
- Ephemeral token per session: `{tenant_id}:{session_id}:{ttl}`
- TTL: 15 minutes (matches access token lifetime)
- Token is bound to specific model + max_tokens budget
- Token is revoked on session end or user logout
- No master API keys in sandbox — only proxy tokens

### 4. Tenant Isolation
- Firestore: `/firms/{firm_id}/**` — existing tenant scoping
- Storage: `gs://shadowtag-omega-v4-{firm_id}/` — per-tenant buckets
- Secret Manager: `{firm_id}-*` — BYOK encryption keys
- IAM: Per-tenant service account (optional, Enterprise tier)

### 5. BYOK / BYOC (Enterprise Tier)
- Customer provides their own API keys for LLM providers
- Keys stored in Secret Manager under customer namespace
- CounselConduit acts as pure proxy (no key exposure)
- Customer-billed: tokens charged to their account directly

## Security Invariants

1. Sandbox MUST NOT access other tenants' data
2. Proxy tokens MUST expire within 15 minutes
3. Tool execution MUST be gVisor-isolated
4. Network egress MUST be allowlisted (LLM APIs only)
5. All tool invocations MUST be audit-logged
6. BYOK keys MUST be accessible only to owning tenant

## Migration Path

1. Deploy Sandbox Router as middleware (no breaking changes)
2. Deploy Cloud Run Jobs for tool execution
3. Deploy LiteLLM proxy token issuance
4. Enable per-tenant Storage buckets (Enterprise)
5. Enable BYOK key management (Enterprise)

## Dependencies

- Cloud Run Jobs (GA)
- gVisor runtime (GA on Cloud Run)
- Cloud Tasks GDPR queue (✅ deployed)
- Firestore tenant collections (✅ deployed)
- LiteLLM v1.83+ (✅ installed)
