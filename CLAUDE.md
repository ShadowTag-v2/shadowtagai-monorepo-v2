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

This project is indexed by GitNexus as **Monorepo-Uphillsnowball** (311360 symbols, 540470 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/Monorepo-Uphillsnowball/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Monorepo-Uphillsnowball/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Monorepo-Uphillsnowball/clusters` | All functional areas |
| `gitnexus://repo/Monorepo-Uphillsnowball/processes` | All execution flows |
| `gitnexus://repo/Monorepo-Uphillsnowball/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

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
