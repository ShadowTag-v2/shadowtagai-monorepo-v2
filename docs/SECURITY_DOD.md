# Cor.30 — Security Definition of Done

**Stack:** Next.js frontend · FastAPI backend · Cloud Run · Firestore · Stripe · GCP Secret Manager
**Version:** 1.0.0 — April 17, 2026
**Authority:** This document is the canonical security gate for every PR, deployment, and AI-generated feature.

> [!CAUTION]
> No code ships to production unless EVERY applicable item below is checked.
> AI velocity does not excuse missing security hygiene — it multiplies the cost of skipping it.

---

## 1. Identity & Session (Rules 1–2, 13, 32)

- [ ] **R1** Access tokens: 15–60 min, signed. Refresh tokens: rotated on every use, revocable, device-bound. Absolute session ceiling: 7–14 days.
- [ ] **R1** Mandatory re-auth for sensitive actions (role changes, payments, exports, Oracle Studio runs).
- [ ] **R1** Token versioning or revocation blocklist implemented — expiry alone does not cover forced logout.
- [ ] **R2** Auth provider: Firebase Auth / Clerk / Supabase Auth ONLY. Never AI-built auth.
- [ ] **R2** MFA mandated for admin and billing roles.
- [ ] **R13** All redirect URLs validated against explicit allow-list.
- [ ] **R32** CSRF protection: `SameSite=Strict` cookies + CSRF double-submit tokens (if cookie-based sessions).

---

## 2. Secrets & Supply Chain (Rules 3–8, 33–35)

- [ ] **R3** No API keys in AI chats. All via `process.env` + GCP Secret Manager.
- [ ] **R4** `.gitignore` is the first file. Includes `.env`, `.env.local`, `node_modules`, `__pycache__`.
- [ ] **R5** Event-driven rotation: rotate immediately on exposure/incident/departure. 60-day max floor.
- [ ] **R5** Prefer short-lived credentials (OIDC Workload Identity on Cloud Run over static SA keys).
- [ ] **R6** Every AI-suggested package verified on npm/PyPI before install (name, download count, publish date).
- [ ] **R7** Prompt for "latest stable, non-deprecated version" — never use AI training-data defaults.
- [ ] **R8** `npm audit` on every PR. Remediate with review — never blind `audit fix` on main.
- [ ] **R33** Gitleaks pre-commit hook installed. TruffleHog in CI for verified credential detection.
- [ ] **R34** Dependencies pinned. No floating versions (`^`, `~`, `*`). Lockfile diffs reviewed on every PR.
- [ ] **R35** Least privilege: separate GCP SAs for database, secrets, storage, pub/sub. No god-mode keys.

---

## 3. API Hardening (Rules 9, 12, 14–16, 23, 31)

- [ ] **R9** Every input sanitized via Zod (TS) or Pydantic (Python). Parameterized queries always.
- [ ] **R9** Validation covers webhook bodies, query params, path variables — not just forms.
- [ ] **R12** CORS locked to production domains only. No wildcard. Ever.
- [ ] **R14** Auth + rate limits on every endpoint, including mobile APIs.
- [ ] **R15** Rate limit by IP + authenticated user + route. Stricter for auth/payment/export/reset.
- [ ] **R15** Exponential backoff + CAPTCHA on repeated violations.
- [ ] **R16** Password reset: 3 attempts/email/hour. Links expire in 15 min, single-use, new link invalidates prior.
- [ ] **R23** Server-side permission checks on every request via FastAPI dependency injection.
- [ ] **R31** Security headers set: CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy.

---

## 4. Storage & Uploads (Rules 10, 19–20)

- [ ] **R10** Row-Level Security / tenant isolation from day one (Firestore security rules or Postgres RLS).
- [ ] **R19** Storage bucket access per-user only. Signed URLs with short TTLs (15 min).
- [ ] **R20** File type validated by magic bytes (signature), not extension. Upload cap: 10 MB default.
- [ ] **R20** Uploaded files scanned for malware before accessibility.

---

## 5. Payments & Webhooks (Rules 21–22, 30)

- [ ] **R21** Webhook signatures verified cryptographically (constant-time comparison, 5-min timestamp tolerance).
- [ ] **R21** Idempotency keys on every payment action.
- [ ] **R22** Email via Resend/SendGrid with SPF + DKIM + DMARC (`p=reject`). Verify via MXToolbox.
- [ ] **R30** Test webhooks NEVER touch production systems. Environment check at handler entry point.

---

## 6. OWASP LLM Top 10 (2025) — AI-Specific

- [ ] **LLM01** Prompt Injection: System prompts structurally isolated from user input at API layer.
- [ ] **LLM02** Sensitive Info Disclosure: PII/secrets stripped from LLM context windows. Outputs filtered before client.
- [ ] **LLM03** Supply Chain: Pinned deps, lockfiles, SBOM, min-release-age validation.
- [ ] **LLM04** Data Poisoning: No custom fine-tuning on untrusted data. Lawyer-approved corpora only.
- [ ] **LLM05** Improper Output: All LLM output treated as untrusted. Escape before rendering. No server-side exec.
- [ ] **LLM06** Excessive Agency: Every agent on minimum-permission tool manifest. Destructive actions require human confirm.
- [ ] **LLM07** System Prompt Leakage: Prompts stored encrypted, never returned in API responses, never in logs.
- [ ] **LLM08** Vector Weaknesses: Embeddings lawyer-curated and version-controlled. No untrusted documents.
- [ ] **LLM09** Misinformation: Mandatory inline citations + hover-to-verify. Multi-model consensus at premium tier.
- [ ] **LLM10** Unbounded Consumption: Hard token budget per request. Per-user rate limits. Circuit breaker for upstream.

---

## 7. Ops & Audit (Rules 11, 17–18, 24–30)

- [ ] **R11** No secrets/PII in any log. Structured logging (structlog/Winston) with severity. Debug stripped from client bundles.
- [ ] **R17** AI API costs capped at provider dashboard AND in code (token budget middleware).
- [ ] **R18** DDoS: Cloud Armor WAF + rate-based rules at edge.
- [ ] **R24** AI security engineer review on every major PR. Paired with automated SAST (Semgrep/CodeQL).
- [ ] **R25** AI red-team: "Act as offensive security engineer" prompts. Human pen test before Series A.
- [ ] **R26** Append-only audit log for: deletions, role changes, payments, exports, Oracle Studio runs.
- [ ] **R27** GDPR: Full account deletion flow (30-day deadline, automated, email receipt).
- [ ] **R28** Automated backups + monthly restore drill. Untested backup = no backup.
- [ ] **R29** Test/prod completely separated (VPCs, DB instances, service accounts).

---

## Threat Model Coverage

| Threat | Defense | Rule(s) |
|--------|---------|---------|
| Voice AI IDOR/BAC | Tenant isolation + server-side authz + opaque IDs | R10, R23, R35 |
| Perplexity .npmrc preload | Sandbox-bound ephemeral tokens + no shared FS + user-billed | R35, LLM03, LLM06 |
| Vibe-coded sinking ship | This entire checklist | R1–R35 |
| OWASP LLM Top 10 | Dedicated LLM section above | LLM01–LLM10 |

---

## Enforcement

- **Pre-commit:** Gitleaks blocks secrets before git history
- **CI/CD:** Security audit workflow blocks PR merge on findings
- **Code review:** Every PR must reference applicable rules
- **Quarterly:** Backup restore drill + secret rotation audit
