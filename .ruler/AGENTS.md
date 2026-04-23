# AGENTS.md — Ruler Single Source

This is the canonical agent instruction source. `ruler apply` distributes these rules
to all configured AI coding agents (Claude, Copilot, Cursor, Gemini, Cline, Aider,
Windsurf, Kiro, JetBrains AI, etc.)

## Mission

Keep the monorepo structurally truthful, Google-native, and latest-only.

## Repo Truth

- `monorepo_manifest.yaml` is the canonical workspace truth.
- `antigravity-mcp-config.json` is the canonical MCP truth.
- `BUSINESS_CONTEXT_LOCKED.md` is pricing and architecture truth.
- `RISK_REGISTER.md` is operational risk truth.

## Architecture

- Active project: `shadowtag-omega-v4`
- Runtime: Google Cloud (Cloud Run, Firestore, Cloud Tasks)
- Model: `gemini-3.1-flash-lite-preview-thinking`
- Database: Firestore (canonical, Supabase rejected)
- Queue: Google Cloud Tasks (BullMQ banned)

## Product Split

### kovelai
- Path: `apps/kovelai`
- Runtime: Google Cloud, Firebase Hosting
- Sites: kovelai.web.app, shadowtagai.web.app

### counselconduit
- Path: `apps/counselconduit`
- Runtime: Cloud Run
- Status: v3.2.0 LIVE, 23 modules

### uphillsnowball
- Path: `labs/uphillsnowball`
- Runtime: local Apple Silicon
- Purpose: R&D only

## Core Technical Truths (DO NOT HALLUCINATE OVERRIDES)

1. **uuid7 Fallback:** Cloud Run container `counselconduit-00015-mmq` uses an old image. We MUST use `try/except ImportError` for `uuid7` resolution between monorepo and container paths.
2. **.NET Environment:** .NET 8.0.419 IS CONFIRMED INSTALLED (`dotnet --version` = `8.0.419`, runtime 8.0.25). Semantic Kernel target framework: `net8.0`. Previous claims of 10.0.x and 11.0.x were FABRICATED — verified 2026-04-23.
3. **Semantic Kernel Process.cs:** `OnExternalEvent` is the CORRECT API for `Microsoft.SemanticKernel.Process.Core v1.21.0-alpha`. Do NOT apply the `OnInputEvent` rename until Process.Core >= v1.30+.
4. **Skill Fleet:** We maintain 182 cherry-picked community skills inside our local Matrix.
5. **Prompt Repetition (arXiv 2512.14982):** Applies ONLY to non-reasoning model tiers (flash, lite, mini) to boost accuracy 1–8%. Do NOT apply to thinking/extended-thinking models.
6. **daScript MCP Reference:** The 29-tool MCP server in the daScript repository is the gold-standard reference architecture for compiler-backed tools. Use it as a blueprint for routing tools.
7. **Lighthouse-CI:** Use Lighthouse-CI for budget assertions in CI pipelines.
8. **V10 Epistemic Airgap:** Corporate monorepo lives in `./external_repos/corp-monorepo/` (gitignored + AI-excluded). DLP Circuit Breaker prohibits passing proprietary identifiers into public search. Supply chain protection prevents blind `pip install` of internal package names. Skill: `.agents/skills/epistemic-airgap/SKILL.md`.

## Open Infrastructure Blockers

- MAGIC_LINK_SECRET needs creation via GCP Secret Manager.
- ~~Firebase Storage needs console initialization~~ — ✅ RESOLVED (2026-04-23): `storage.rules` deployed with deny-all rules.
- ~~`lead-capture-router` requires a `firebase-admin` upgrade~~ — ✅ RESOLVED: Already at `^13.8.0` (latest major).
- `NotebookLM MCP` CLI needs installation (`uv tool install notebooklm-mcp-cli`).
- Cloud Run redeploy needed for uuid7 fix (container `counselconduit-00015-mmq`).

## Guardrails

- Never introduce a second source of truth for MCP
- Never commit real secrets
- Never treat duplicate recovered trees as canonical
- Fix root truth first, tooling second, runtime third
- Never COMPLECT orthogonal concerns

## Security (Non-Negotiable)

1. No secrets in code, logs, or chat. Environment variables and GCP Secret Manager only.
2. Every API route authenticated by default. Public routes documented with reason.
3. All inputs validated with Pydantic/Zod. Never trust user input.
4. Never return raw database objects. Serialize and select fields explicitly.
5. Errors via RFC 9457. Never expose stack traces.
6. Parameterized queries only. Never concatenate user input into SQL.
7. Short-lived access tokens (15-60 min). Rotating refresh tokens.
8. No auth from scratch. Firebase Auth or managed providers only.
9. Rate limit by IP, user, and endpoint.
10. CSP, HSTS, CSRF protections everywhere.

## Dev Standards

- Python: Google style, CPython 3.14.3, ruff + vulture at 90%
- TypeScript: Google style, biome linting
- Go: Google style
- Shell: Google style
- Step 0 of any refactor is DELETION
- Think through edge cases before writing code
- Consider 2+ approaches before committing
- For changes >100 LOC: outline first, then implement
