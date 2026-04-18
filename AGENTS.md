# AGENTS.md

## Mission

Keep the monorepo structurally truthful, Google-native, and latest-only.

## Repo truth

- `monorepo_manifest.yaml` is the canonical workspace truth.
- `antigravity-mcp-config.json` is the canonical MCP truth.
- Historical adapter files are not sources of truth.

## Product split

### kovelai
- product path: `apps/kovelai`
- runtime: Google Cloud
- project: `shadowtag-omega-v4`
- model: `gemini-3.1-flash-lite-preview`
- note: formerly CounselConduit. `apps/counselconduit` retained as operational backend.

### uphillsnowball
- lab path: `labs/uphillsnowball`
- runtime: local Apple Silicon
- purpose: R&D and local experimentation
- must not redefine counselconduit product truth

## Merge truth

All four repo roots must remain canonical:
- `apps/aiyou_stack/aiyou-fastapi-services`
- `apps/aiyou_stack/cosmic-crab-payload`
- `apps/aiyou_stack/Pipeline`
- `apps/aiyou_stack/nascent-apollo`

## Guardrails

- never introduce a second source of truth for MCP
- never commit real secrets
- never mark a live repo archived
- never treat duplicate recovered trees as canonical
- fix root truth first, tooling second, runtime third
- never COMPLECT orthogonal concerns (see `docs/doctrine/SIMPLICITY_DOCTRINE.md`)

## Security + App Contract (Non-Negotiable)

1. Never store secrets, API keys, or credentials in frontend code, committed files, or chat logs. Use environment variables and managed secrets only.
2. Every API route is authenticated by default. Public routes must be explicitly documented with a reason.
3. Validate all request inputs with schema validation (Zod/Pydantic) before processing. Never trust user input.
4. Never return raw database objects. Always serialize and explicitly select exposed fields.
5. Handle errors through a single structured app error contract (RFC 9457). Never expose stack traces or system internals to clients.
6. If passwords are ever handled locally, hash with bcrypt/argon2 under the approved minimum work factor. Never store, log, or return plaintext passwords.
7. Use parameterized queries or ORM methods only. Never concatenate user input into SQL.
8. Every async UI operation must have both loading and error states.
9. Write small, focused functions. Split functions that do more than one thing.
10. Before writing new code, check for an existing utility, hook, service, or action. Do not duplicate logic.

## Security Defaults

11. Access tokens must be short-lived (15–60 min). Refresh tokens must rotate and be revocable. Absolute session timeout required.
12. Never build auth from scratch unless explicitly approved. Use managed auth providers (Firebase Auth, Clerk) by default.
13. Secrets rotate on exposure, incident, or personnel change; prefer short-lived credentials where possible.
14. Run dependency audit on every PR. Never apply blind security fixes (`npm audit fix --force`) to main without review and tests.
15. Use strict CORS, redirect allow-lists, and per-route authz checks server-side.
16. Rate limit by IP, user, and endpoint. Stricter limits for auth, payment, reset, export, and AI-costly routes.
17. Enable RLS / tenant isolation from day one for multi-tenant systems.
18. Lock down storage buckets and validate uploads by signature, size, and policy.
19. Verify webhook signatures and enforce idempotency.
20. No secrets or PII in logs. Use structured logging with severity and correlation IDs.
21. Enforce backups, restore tests, test/prod separation, and account deletion flows.
22. Enable CSP, HSTS, Referrer-Policy, X-Content-Type-Options, and CSRF protections where applicable.
23. Run secrets scanning in pre-commit and CI (Gitleaks + detect-private-key).
24. Use lockfiles, pinned dependencies, and least-privilege service roles.
25. Every LLM timeout must fail gracefully in the UI and server responses.

## Architectural philosophy

- `docs/doctrine/SIMPLICITY_DOCTRINE.md` is the CANONICAL architectural philosophy
- Simple (one-fold, unentangled) over Easy (familiar, at-hand) — always
- Hammock Protocol: think BEFORE coding for any architectural decision
- Problems over Puzzles: if it doesn't serve the user, don't build it
- AI as Junior Dev: pair with AI, review output, never accept AI architecture unchecked

## Strategic note

Highest-value sequence:
1. truth surfaces
2. recovered operational code
3. commercial MVP hardening

## Reasoning depth

- think through edge cases before writing code
- consider at least 2 alternative approaches before committing to one
- for changes >100 LOC: outline the approach first, then implement
- never take the "simplest approach" — take the most robust one
- use sequential-thinking MCP for multi-step architectural decisions
- re-read files before editing; re-read after to confirm

## Immutable zones

The following files constitute the control plane. Agents MUST NOT modify them
unless the user explicitly directs a control plane change:

- `AGENTS.md` — canonical contract
- `GEMINI.md` — operator invariants
- `monorepo_manifest.yaml` — workspace truth
- `antigravity-mcp-config.json` — MCP truth
- `BUSINESS_CONTEXT_LOCKED.md` — pricing and architecture truth
- `RISK_REGISTER.md` — operational risk truth
- `scripts/dead-code-audit.sh` — guillotine
- `scripts/pnkln_root_guard.sh` — root guard
- `.gitignore` — debris prevention

## Hardened state

- v9.3 canonicalized: 2026-04-18
- Commit: `e21af38f05f`
- CI Python: 3.13 (all 3 workflows)
- venv primary: CPython 3.14.3
- Firestore: 2 databases (`(default)`, `shadowtag-engine`)
- Firestore rules: zero-trust deployed (default deny-all, admin-only access)
- Firebase deployment: MCP-first doctrine enforced (see `GEMINI.md` v9.0)
- Semantic Kernel: .NET 11.0 Preview 2
- Tests: 77 passed, 5 E2E skipped (live Cloud Run endpoints — expected)
- Lighthouse: P93+ / A93+ / BP100 / SEO100
- Dead code: clean (vulture + ruff — Kosmos dead code noted, production paths clean)
- CSP headers: full parity across kovelai + shadowtagai (unsafe-eval removed)
- Infrastructure: shadowtagai.web.app + kovelai.web.app + shadowtag-omega-v4.web.app deployed
- Nested `.git` directories: 0 (reference_architectures/ clones are gitignored)
- Ruff violations: 1211 total, 33 F401 (ruff 0.11.8 — expanded rule set)
- CounselConduit: v3.1.0 on Cloud Run (Phase 1 + 2 LIVE, 33 API modules)
- Cloud Armor WAF: `apps/counselconduit/cloud_armor_policy.yaml`
- Prompt Repetition: wired into Oracle Studio + Vent Mode (arXiv 2512.14982)
- OG Social Images: generated + deployed for both sites
- Pre-commit: Gitleaks + Ruff + Bandit + detect-private-key
- OpenTofu: 19 resources provisioned (IAM + alerts + log metrics)
