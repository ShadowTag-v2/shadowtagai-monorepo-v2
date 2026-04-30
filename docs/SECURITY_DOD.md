# Security Definition of Done (DoD) — CounselConduit

> Cor.30 Anti-Vibe Security Manifesto | OWASP LLM Top 10 (2025)
> Version: 2.0 | Last Updated: 2026-04-18

## Overview

Every feature, PR, and deployment MUST pass this 6-Pillar security checklist before
shipping. No exceptions. AI velocity does not excuse missing security hygiene — it
**multiplies the cost** of skipping it.

---

## Pillar 1: Identity & Session (R1–2, R13, R32)

- [ ] Access tokens: short-lived (15–60 min), rotated refresh tokens
- [ ] MFA enforced for admin and billing operations
- [ ] CSRF protection on all state-changing endpoints
- [ ] Redirect/callback URLs use strict allow-lists (no open redirects)
- [ ] Firebase Auth JWT verified server-side (`firebase-admin` SDK)
- [ ] Session inactivity timeout ≤ 30 minutes (client portal: 5 min dead-man's switch)
- [ ] No session tokens in URL query parameters
- [ ] Cookie flags: `HttpOnly`, `Secure`, `SameSite=Strict`

## Pillar 2: Secrets & Supply Chain (R3–8, R33–35)

- [ ] All secrets in Google Secret Manager (never in `.env` in production)
- [ ] Cloud Run: secrets mounted via `--set-secrets` (not env vars in YAML)
- [ ] Secret Manager audit logging: ADMIN_READ + DATA_READ + DATA_WRITE enabled
- [ ] Secret rotation: Stripe keys rotated every 90 days (Terraform `rotation` block)
- [ ] Secret access: only `secretAccessor` role, scoped to specific SAs
- [ ] Secret IaC: all secrets declared in `infra/terraform/secrets.tf`
- [ ] Betterleaks pre-commit hook active (`.pre-commit-config.yaml`)
- [ ] Dependencies pinned with exact versions in `requirements.txt`
- [ ] No `npm audit fix --force` (manual review only)
- [ ] Package provenance verified (PyPI/npm signatures)
- [ ] `.env` deleted from production workstations (Secret Manager is source of truth)
- [ ] No hardcoded API keys, connection strings, or JWTs in source
- [ ] Stripe keys: only `STRIPE_PUBLISHABLE_KEY` in frontend HTML
- [ ] Org policy `storage.publicAccessPrevention` enforced

## Pillar 3: API Hardening (R9, R12, R14–16, R23, R31)

- [ ] All input validated with Pydantic models (server-side)
- [ ] Per-IP rate limiting: `RateLimitMiddleware` (60 req/min default)
- [ ] Per-attorney rate limiting: sliding window (100 req/hr default)
- [ ] Server-side authorization on every endpoint (no client-trust)
- [ ] Security headers on all responses (Cor.30 R31):
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Content-Security-Policy` (strict, script-src whitelist)
  - `Strict-Transport-Security` (HSTS, 2-year max-age)
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy` (camera, microphone, geolocation denied)
- [ ] CORS: explicit origin allow-list (no `*` in production)
- [ ] OpenAPI schema published but `/docs` disabled in production
- [ ] Cloud Armor WAF: XSS + SQLi rules active

## Pillar 4: Storage & Uploads (R10, R19–20)

- [ ] Tenant isolation: all Firestore queries scoped by `firm_id`
- [ ] Signed URLs for any file access (no public bucket URLs)
- [ ] File uploads: magic-byte validation (not just extension check)
- [ ] Upload size limits enforced server-side
- [ ] No direct Firestore/Storage access from client (server proxy only)

## Pillar 5: Payments & Webhooks (R21–22, R30)

- [ ] Stripe webhook: HMAC signature verification (`stripe-signature` header)
- [ ] Stripe Connect webhook: separate endpoint, separate secret
- [ ] Idempotency keys on all payment mutations
- [ ] Test/production Stripe key separation enforced
- [ ] Email: SPF/DKIM/DMARC configured for sending domain
- [ ] Resend webhook: signature verification on delivery events
- [ ] Billing state never trusted from client — always server-verified

## Pillar 6: Ops & Audit (R11, R17–18, R24–30)

- [ ] Structured logging (JSON, no PII in logs)
- [ ] Audit log: immutable `audit_log` Firestore collection
- [ ] Token budget caps: per-session and per-tenant limits
- [ ] GDPR Article 17: deletion request → Cloud Tasks 30-day hard delete
- [ ] GDPR Article 20: data export endpoint with tenant scoping
- [ ] Backup + restore drills: Firestore export tested quarterly
- [ ] Cloud Monitoring: 5xx alert policy active
- [ ] Discord alerts for payment failures and security events

---

## OWASP LLM Top 10 (2025) — Mandatory Controls

| # | Risk | Control | Status |
|---|------|---------|--------|
| LLM01 | Prompt Injection | System prompts isolated from user input in `_EXTRACTION_SYSTEM_PROMPT` | ✅ |
| LLM02 | Sensitive Info Disclosure | PII stripped from context windows; no client data in prompts | ✅ |
| LLM05 | Improper Output Handling | All LLM output treated as untrusted; sanitized before display | ✅ |
| LLM06 | Excessive Agency | Minimum-permission tool manifests; no autonomous actions | ✅ |
| LLM07 | Prompt Leakage | System prompts never in API responses or client logs | ✅ |
| LLM10 | Unbounded Consumption | Token budget + per-attorney rate limits + circuit breaker | ✅ |

---

## Vibe-Coding Anti-Patterns (Prohibited)

1. **No deny-by-default routing bypass**: Every route must have explicit auth
2. **No raw DB serialization**: Always use Pydantic models, never `dict` pass-through
3. **No missing UI async states**: Every API call must show loading/error/success states
4. **Never trust AI-generated auth code without manual review**
5. **No `eval()` or `exec()` on any user-provided or LLM-generated content**
6. **No shared secrets across environments** (staging ≠ production keys)
7. **No `console.log` of tokens, keys, or PII**
8. **No client-side privilege checks** (always server-verified)
9. **No `innerHTML` with unsanitized content**
10. **No blind dependency updates** (`npm audit fix --force` is banned)

---

## Pre-Merge CI Gate

- Betterleaks scan (pre-commit + CI)
- Ruff lint (E9, F63, F7, F82)
- Bandit scan (Python security)
- npm audit (advisory check, no auto-fix)
- Lighthouse (Performance ≥ 90, BP = 100, SEO = 100)

## Sign-Off

Every PR touching auth, payments, LLM integration, or deployment config
MUST include this checklist as a PR comment with items checked.

---

*Generated: 2026-04-18 | Doctrine: Cor.30 v2.5 + OWASP LLM10 2025*
