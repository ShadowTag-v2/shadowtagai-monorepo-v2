# Cor.30 Security Audit Report — KovelAI Sprint 1

> **Item #14**: Security audit across all 12 backend modules.
>
> **Date**: 2026-04-22
> **Auditor**: Antigravity (automated, Cor.30 6-pillar framework)

---

## Summary

| Pillar | Score | Status |
|--------|-------|--------|
| 1. Identity & Session | 9/10 | ✅ PASS |
| 2. Secrets & Supply Chain | 8/10 | ✅ PASS |
| 3. API Hardening | 9/10 | ✅ PASS |
| 4. Storage & Uploads | 8/10 | ⚠️ PASS (minor) |
| 5. Payments & Webhooks | 10/10 | ✅ PASS |
| 6. Ops & Audit | 7/10 | ⚠️ PASS (minor) |

**Overall: PASS (85/100)**

---

## Pillar 1: Identity & Session

### ✅ S.E.U. Token (`lib/auth/seu-token.ts`)
- [x] R1: Short-lived access tokens — **300s TTL**, hash-chain derived
- [x] R2: Sandbox-bound with tenant + IP binding
- [x] R13: CSRF protection via token binding
- [x] R32: Session tokens are ephemeral (single-use)
- ⚠️ RECOMMEND: Add MFA gate for attorney dashboard access

### ✅ Dead Man's Switch (`components/DeadManSwitch.tsx`)
- [x] Auto-logout on 5-min inactivity
- [x] Tab blur detection
- [x] Session wipe on timeout

---

## Pillar 2: Secrets & Supply Chain

### ✅ `.env` Handling
- [x] R3: No hardcoded API keys in any module
- [x] R4: All secrets via `process.env`
- [x] R5: No secrets in git (`.gitignore` verified)
- ⚠️ R6: Gitleaks pre-commit hook present but terraform hook broken (unrelated)

### ✅ BYOK Client (`lib/crypto/byok-client.ts`)
- [x] R33: AES-256-GCM encryption
- [x] R34: PBKDF2 key derivation (600K iterations)
- [x] R35: WebCrypto API (no custom crypto)

---

## Pillar 3: API Hardening

### ✅ Zod Validation (All Route Handlers)
- [x] R9: Every route uses `z.object()` validation
- [x] Privileged search: query length capped at 500 chars
- [x] CLE endpoint: integer validation on attendance minutes
- [x] Bridge API: UUID validation on all IDs

### ✅ Rate Limiting (`lib/middleware/rate-limiter.ts`)
- [x] R12: Token bucket with firm-scoped quotas
- [x] R14: Per-user rate limits
- [x] R31: Security headers (CSP, HSTS, XCTO)

### ✅ Token Budget (`lib/middleware/token-budget.ts`)
- [x] R15: Per-tier daily/monthly enforcement
- [x] R16: Hard caps with grace period
- [x] R23: Server-side authorization on all budget checks

---

## Pillar 4: Storage & Uploads

### ✅ Firestore Separation
- [x] R10: Tenant isolation via `firms/{firmId}/` namespace
- [x] R19: Per-firm storage paths
- ⚠️ R20: No file upload endpoints exist yet — N/A for Sprint 1
- ⚠️ RECOMMEND: Add magic-byte validation when file uploads are added

---

## Pillar 5: Payments & Webhooks

### ✅ Stripe Connect (`lib/billing/stripe-connect.ts`)
- [x] R21: HMAC signature verification on all webhook events
- [x] R22: Idempotency check before processing
- [x] R30: Test/production separation via `STRIPE_SECRET_KEY`

### ✅ Webhook Handler (`app/api/webhooks/stripe/route.ts`)
- [x] `stripe.webhooks.constructEvent()` used correctly
- [x] Idempotency dedup before handler dispatch
- [x] All event types properly typed

---

## Pillar 6: Ops & Audit

### ✅ SOC 2 Evidence (`lib/compliance/soc2-evidence.ts`)
- [x] R24: Structured logging (no PII in logs)
- [x] R25: Token budget caps
- [x] R26: Audit log framework

### ⚠️ Gaps
- R11: Structured logging partially implemented (console.* used in some handlers)
- R17: GDPR deletion flow created but Cloud Tasks queue not provisioned yet
- R27: Backup/restore drill not yet conducted
- R28: No automated monitoring alerts configured

---

## OWASP LLM Top 10 Assessment

| # | Risk | Status | Control |
|---|------|--------|---------|
| LLM01 | Prompt Injection | ✅ | System prompts in `lib/prompts/legal-prompts.ts` isolated from user input |
| LLM02 | Sensitive Info | ✅ | PII stripped via Intent Vault preprocessing |
| LLM05 | Improper Output | ✅ | All LLM output treated as untrusted (no `dangerouslySetInnerHTML`) |
| LLM06 | Excessive Agency | ✅ | Minimum-permission tool manifests |
| LLM07 | Prompt Leakage | ✅ | System prompts not in responses/logs |
| LLM10 | Unbounded Consumption | ✅ | Token budget middleware enforces per-tier caps |

---

## Recommendations (Priority Order)

1. **HIGH**: Provision Cloud Tasks GDPR queue in `us-central1`
2. **HIGH**: Replace `console.*` with structured logger in webhook/bridge handlers
3. **MEDIUM**: Configure Cloud Monitoring alerting policies
4. **MEDIUM**: Add MFA gate for attorney dashboard login
5. **LOW**: Schedule backup/restore drill for Firestore
6. **LOW**: Add magic-byte file validation when upload feature ships

---

## Module-by-Module Audit

| Module | File | Zod | Auth | Rate Limit | Secrets |
|--------|------|-----|------|------------|---------|
| Stripe Connect | `lib/billing/stripe-connect.ts` | ✅ | ✅ | ✅ | ✅ |
| S.E.U. Token | `lib/auth/seu-token.ts` | ✅ | ✅ | ✅ | ✅ |
| Intent Vault | `lib/vault/intent-vault.ts` | ✅ | ✅ | N/A | ✅ |
| Token Budget | `lib/middleware/token-budget.ts` | ✅ | ✅ | ✅ | ✅ |
| SOC 2 Evidence | `lib/compliance/soc2-evidence.ts` | ✅ | ✅ | N/A | ✅ |
| Kovel Receipt | `lib/attestation/kovel-receipt.ts` | ✅ | ✅ | N/A | ✅ |
| BYOK Client | `lib/crypto/byok-client.ts` | ✅ | N/A | N/A | ✅ |
| Legal Search | `lib/connectors/legal-search.ts` | ✅ | ✅ | ✅ | ✅ |
| CLE Cert | `lib/compliance/cle-certificate.ts` | ✅ | ✅ | N/A | ✅ |
| Cloud Armor | `lib/security/cloud-armor.ts` | ✅ | N/A | ✅ | ✅ |
| Oracle Memo | `lib/oracle/memo-pdf.ts` | ✅ | ✅ | N/A | ✅ |
| SSE Client | `lib/streaming/sse-client.ts` | ✅ | ✅ | N/A | ✅ |

---

*Audit generated by Antigravity Cor.30 Security Enforcer. Next audit scheduled: Sprint 2 completion.*
