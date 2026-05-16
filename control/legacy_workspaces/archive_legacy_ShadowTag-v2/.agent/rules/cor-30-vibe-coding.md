# COR.30: Security Rules for AI Vibe Coding (2026 Edition)

> **"Ship fast, but lock it down like Fort Knox."**
> These rules act as OWASP-flavored guardrails for rapid builders. They must be applied by all agents to ensure AI-generated code survives in production.

## 1. Identity & Session

1. **Sessions:** Access tokens short-lived (15–60 min). Refresh tokens: rotated, revocable, bound to device/session. Absolute session max (7-14 days).
2. **Auth Generation:** Never use AI-built auth. Use Clerk, Supabase Auth, or Auth0 with MFA mandates.
3. **Redirects:** Validate all redirect URLs against a strict allow-list.

## 2. Secrets & Supply Chain

4. **Environment Variables:** Never paste API keys into AI chats. Use `process.env`. Treat keys like nukes.
2. **Git Hygiene:** `.gitignore` is your first file in every project, not the last. Include `.env`, `node_modules`, etc.
3. **Secret Rotation:** Rotate immediately on suspected exposure; prefer short-lived credentials. Automate with Vault or KMS.
4. **Secrets Scanning:** Run Gitleaks/TruffleHog pre-commit + CI. Block merges on findings.
5. **Package Verification:** Verify every package the AI suggests actually exists before installing (`npm search` / `pip check`).
6. **Package Versions:** Specify "latest secure version" in prompts. Pin dependencies + use lockfile discipline. No floating versions.
7. **Auditing:** Run `npm audit` on every PR; remediate with review. Avoid blind `audit fix` on main without tests.

## 3. API Hardening

11. **Input Sanitization:** Sanitize every input. Use parameterized queries always. Force prompts for Zod/Pydantic validation to prevent SQLi/XSS.
2. **CORS:** CORS should only allow your production domain. Never wildcard. Use strict-origin-when-cross-origin.
3. **Rate Limiting:** Rate limit by IP + user + endpoint; stricter for auth/payment/export (e.g., 3 password resets per email/hour).
4. **Endpoint Protection:** Apply auth + rate limits + server-side permission checks to *every* endpoint. UI-level checks are security theater.
5. **DDoS Protection:** Add DDoS protection via Cloudflare or Vercel edge config. Edge WAFs block prompt injections.
6. **CSP & Headers:** Implement Content Security Policy (CSP), HSTS, X-Content-Type-Options, Referrer-Policy by default.
7. **CSRF:** If using cookie sessions, employ CSRF tokens + SameSite, or get owned.

## 4. Storage & Uploads

18. **Row-Level Security (RLS):** Enable Row-Level Security from day one (e.g., Postgres/Supabase built-ins).
2. **Bucket Lockdown:** Lock down storage buckets. Users should only access their own files via row-level checks + signed URLs.
3. **Upload Validation:** Limit upload sizes (e.g. 10MB limit) and validate file type by signature (magic bytes), not extension.

## 5. Payments & Webhooks

21. **Webhook Signatures:** Verify webhook signatures before processing any payment data. Non-negotiable.
2. **Sandbox Separation:** Keep test and production environments completely separate. Never let test webhooks touch real systems.

## 6. Ops & Audit

23. **Logging:** Avoid secrets/PII in logs. Use structured logging with severity (Winston/Sentry). Strip debug/console logs in client bundles.
2. **Audit Trails:** Log critical actions: deletions, role changes, payments, exports. Support anomaly detection.
3. **Data Deletion:** Build a real account deletion flow to avoid GDPR fines. Automate + confirm deletion.
4. **Backups:** Automate backups and test restoration. An untested backup is nothing.
5. **Privilege:** Enforce least privilege for service roles. Separate keys for admin tasks vs user actions.
6. **Email Spooofing:** Use Resend or SendGrid with proper SPF/DKIM records.
7. **Cost Brakes:** Cap AI API costs in your dashboard AND in your code.
8. **Red Teaming:** Ask the AI to act as an ethical hacker/security engineer to review and hack your code. Pair this with real SAST (CodeQL/Semgrep).
