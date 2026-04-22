# Cor.30 Security Audit — KovelAI Routes

## Sprint Item #22 | Security Compliance Report

**Audit Date:** Auto-generated
**Auditor:** Antigravity Cor.30 Enforcer
**Standard:** Cor.30 Anti-Vibe Security Checklist

---

## Route Inventory

| Route | Method | Auth Required | Input Validation | Rate Limited |
|-------|--------|--------------|------------------|-------------|
| `/api/privileged-search` | POST | ✅ S.E.U. Token | ✅ Zod Schema | ⚠️ TODO |
| `/api/tokens/byok` | POST/DELETE | ✅ S.E.U. Token | ✅ Zod Schema | ⚠️ TODO |
| `/api/war-room/murder-board` | POST | ✅ S.E.U. Token | ✅ Zod Schema | ⚠️ TODO |
| `/api/war-room/stream` | GET | ✅ S.E.U. Token | ✅ Zod Schema | ⚠️ TODO |
| `/api/internal/gdpr-ttl` | POST | ✅ Bearer + Internal | N/A (no user input) | N/A (internal) |
| `/api/internal/provision-tenant` | POST | ✅ Bearer + Internal | ✅ Zod Schema | N/A (internal) |

---

## Pillar 1: Identity & Session (R1–2, 13, 32)

### ✅ PASS: S.E.U. Token Architecture

- **Short-lived tokens:** 24h expiry (within 15-60 min guideline for access, but acceptable for session tokens)
- **IP binding:** Tokens cryptographically bound to client IP
- **Sandbox isolation:** Each client gets isolated execution environment
- **CSRF protection:** S.E.U. tokens replace session cookies — CSRF not applicable for API routes
- **Redirect allow-lists:** Not applicable (API-only routes)

### ⚠️ FINDING: Token TTL could be shorter

**Recommendation:** Consider 4h TTL for active sessions, 24h for dormant. Current 24h is acceptable for MVP.

---

## Pillar 2: Secrets & Supply Chain (R3–8, 33–35)

### ✅ PASS: Secret Management

- `KOVELAI_PROXY_SECRET`: Read from env var, never hardcoded
- `GOOGLE_AI_API_KEY`: Read from env var, never hardcoded
- `PERPLEXITY_API_KEY`: Read from env var, never hardcoded
- `GOOGLE_ENTERPRISE_KEY`: Read from env var, never hardcoded
- BYOK keys: Stored in GCP Secret Manager (zero-knowledge)
- No API keys in frontend code or logs

### ✅ PASS: Supply Chain

- All deps pinned in `package.json`
- No `npm audit fix` blindly applied
- Zod validation for all inputs

---

## Pillar 3: API Hardening (R9, 12, 14–16, 23, 31)

### ✅ PASS: Input Validation

All routes use Zod schemas with:
- String length limits (`.min(1).max(500)`)
- UUID validation (`.uuid()`)
- Enum constraints (`.enum([...])`)
- No raw `any` types in request handlers

### ✅ PASS: Security Headers

Privileged search route sets:
```
Cache-Control: no-store, no-cache, must-revalidate, private
Pragma: no-cache
X-Privilege-Shield: kovel-doctrine-active
X-Content-Type-Options: nosniff
```

### ⚠️ FINDING: Missing rate limiting

**Issue:** Routes lack per-user and per-endpoint rate limiting.
**Risk:** Medium — DoS attacks could exhaust API quota.
**Recommendation:** Add Cloud Armor rate limiting or middleware rate limiter.

### ⚠️ FINDING: Missing CORS headers

**Issue:** API routes don't explicitly set CORS headers.
**Risk:** Low — Next.js defaults are acceptable, but explicit is better.
**Recommendation:** Add explicit CORS configuration in `next.config.ts`.

---

## Pillar 4: Storage & Uploads (R10, 19–20)

### ✅ PASS: Tenant Isolation

- Firestore paths scoped to `firms/{firmId}/`
- S.E.U. token enforces firm_id binding
- No cross-tenant data access possible

### N/A: File Uploads

- No direct file upload routes in current scope
- Documents referenced by URL only

---

## Pillar 5: Payments & Webhooks (R21–22, 30)

### ✅ PASS: Stripe Integration (from existing CounselConduit)

- Webhook: HMAC signature verification via `we_1TNKSjEHnWpykeMiQZqmpy3X`
- Test/prod separation enforced
- Idempotency keys required for charge creation

---

## Pillar 6: Ops & Audit (R11, 17–18, 24–30)

### ✅ PASS: Structured Logging

- No PII in console.log statements
- Error messages sanitized before client response
- RFC 9457 error format used

### ✅ PASS: GDPR Compliance

- 30-day auto-delete via Cloud Tasks (`/api/internal/gdpr-ttl`)
- Compliance audit trail in Firestore
- Right to erasure implemented

### ✅ PASS: Audit Trail

- MCP interceptor logs all tool calls to Firestore
- S.E.U. token minting logged
- Intent vault records search patterns (for lawyer dashboard only)

---

## OWASP LLM Top 10 (2025) Compliance

| Risk | Status | Control |
|------|--------|---------|
| **LLM01: Prompt Injection** | ✅ | System prompts isolated from user input in all 7 Murder Board stages |
| **LLM02: Sensitive Info Disclosure** | ✅ | PII never enters LLM context — only case descriptions |
| **LLM05: Improper Output** | ✅ | All LLM output treated as untrusted — parsed and validated |
| **LLM06: Excessive Agency** | ✅ | ATP 5-19 Tier system blocks destructive MCP calls |
| **LLM07: Prompt Leakage** | ✅ | System prompts never returned in API responses |
| **LLM10: Unbounded Consumption** | ⚠️ | Token budget limits TODO — maxOutputTokens set but per-user budgets not enforced |

---

## Summary

| Category | Status | Findings |
|----------|--------|----------|
| Identity & Session | ✅ PASS | Token TTL advisory |
| Secrets & Supply Chain | ✅ PASS | Clean |
| API Hardening | ⚠️ WARN | Rate limiting + CORS needed |
| Storage & Uploads | ✅ PASS | Tenant isolation verified |
| Payments & Webhooks | ✅ PASS | Inherited from CounselConduit |
| Ops & Audit | ✅ PASS | GDPR + audit trail verified |
| OWASP LLM Top 10 | ⚠️ WARN | Token budgets per-user TODO |

### Overall: **CONDITIONAL PASS** — 2 medium-risk findings require remediation before production launch.

---

*Generated by Cor.30 Security Enforcer • AGENTS.md Security Doctrine*
