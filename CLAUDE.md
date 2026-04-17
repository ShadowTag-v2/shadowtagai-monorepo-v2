# CLAUDE.md — GKC Security Rules (enforced on every generation)
# This is a thin shim. AGENTS.md is the canonical contract.
# GEMINI.md is the full operator invariant. CLAUDE.md enforces code quality.

## Secrets & Environment
- Never store secrets, API keys, or credentials in frontend code or committed source files.
- All secrets via `process.env` + GCP Secret Manager only.
- Never expose server-side env vars to the frontend bundle.

## Authentication
- Every API route requires authentication middleware unless explicitly commented as `@public` with a security reason.
- Never write custom auth logic. Use Firebase Auth / Clerk / Supabase Auth.
- MFA required for admin and billing roles.

## Inputs & Queries
- Validate all request inputs using Zod (TS) or Pydantic (Python) before any processing.
- Use parameterized queries or ORM methods only. Never concatenate user input into SQL.

## API Responses
- Never return raw database objects. Always serialize via explicit DTOs (`Pydantic BaseModel` / Zod schema) with selected fields only.
- Errors: throw `AppError` instances, return structured RFC 9457 JSON `{ status, code, message }`. Never expose stack traces or system internals.
- No secrets, PII, or internal paths in any log or API response.

## Passwords & Auth Data
- Argon2id for new systems (`argon2-cffi` Python / `argon2` Node). Bcrypt min 10 rounds for legacy.
- Never store, log, return, or transmit plaintext passwords.

## Data Minimization
- Never build data models that collect SSNs, raw card details, or data you don't need.
- Use OAuth/magic links. Don't store what you don't have to protect.

## Frontend
- Every async operation: loading state + error state + timeout fallback (45s max). No dead spinners.
- No secrets or tokens in localStorage. httpOnly Secure SameSite=Strict cookies only.

## Code Quality (Affects Security Surface)
- Functions do one thing. If it does two things, split it.
- Check for existing utilities before writing new ones. No duplicated logic.
- Before completing a feature, run self-audit: "Review the code I just wrote for security risks, data exposure, and logical bugs."

## Agent Safety
- Disable all hooks unless explicitly reviewed and approved.
- Deny rules: block curl/fetch to external endpoints, block `.env` file access from agent code.
- Approve only verified MCP servers (github, memory, firebase).
- Transcript retention: 14 days maximum.

## Canonical References
- `AGENTS.md` — canonical contract
- `GEMINI.md` — operator invariants (v8.6+)
- `docs/SECURITY_DOD.md` — full 35-rule checklist + OWASP LLM Top 10
- `skills/cor30-security-enforcer/SKILL.md` — AI agent enforcement skill
