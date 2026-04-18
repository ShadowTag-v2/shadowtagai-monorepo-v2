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

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Monorepo-Uphillsnowball** (445205 symbols, 685812 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Monorepo-Uphillsnowball/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Monorepo-Uphillsnowball/clusters` | All functional areas |
| `gitnexus://repo/Monorepo-Uphillsnowball/processes` | All execution flows |
| `gitnexus://repo/Monorepo-Uphillsnowball/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
