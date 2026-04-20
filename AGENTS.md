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

## Capability ownership

- Every operational capability must have exactly one primary owner.
- Shared capability claims are forbidden in steady state.
- Human-readable doctrine may describe capability ownership, but executable ownership lives only in `antigravity-mcp-config.json`.
- If prose doctrine conflicts with MCP truth, `antigravity-mcp-config.json` wins.
- Verification capabilities and debugging capabilities must not be co-owned unless MCP truth defines an explicit fallback path.

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

- v9.6 canonicalized: 2026-04-20
- Commit: `02f2659f61`
- CI Python: 3.13 (all 3 workflows)
- venv primary: CPython 3.14.3
- Firestore: 2 databases (`(default)`, `shadowtag-engine`)
- Firestore rules: zero-trust deployed (default deny-all, admin-only access)
- Firebase deployment: MCP-first doctrine enforced (see `GEMINI.md` v9.5)
- Semantic Kernel: .NET 11.0 Preview 2 (UNVERIFIED — see GEMINI.md v9.6)
- Tests: 87 unit passed (E2E skipped — live Cloud Run endpoints)
- Lighthouse: shadowtagai P89/A100/BP100/SEO100, kovelai P89/A96/BP100/SEO100 (PageSpeed Insights verified 2026-04-20)
- Dead code: clean (vulture + ruff — 0 violations at 80%+ confidence in gitleaks_guardian.py)
- CSP headers: full parity across kovelai + shadowtagai (unsafe-eval removed)
- Infrastructure: shadowtagai.web.app + kovelai.web.app + shadowtag-omega-v4.web.app deployed
- Nested `.git` directories: 0 (reference_architectures/ clones are gitignored)
- Ruff violations: 0 in counselconduit (ruff 0.11.8, `--fix --unsafe-fixes` applied)
- CounselConduit: v3.1.0 on Cloud Run (Phase 1 + 2 LIVE, 27 endpoints, revision `counselconduit-00015-mmq`)
- Cloud Armor WAF: `apps/counselconduit/cloud_armor_policy.yaml`
- Prompt Repetition: wired into Oracle Studio + Vent Mode (arXiv 2512.14982)
- OG Social Images: generated + deployed for both sites
- Pre-commit: Gitleaks + Ruff + Bandit + detect-private-key
- OpenTofu: 19 resources provisioned (IAM + alerts + log metrics)
- GitNexus: 445,205 nodes | 685,812 edges | 6,090 clusters | 300 flows (indexed 2026-04-18)
- Risk Register: 46 risks tracked (0 critical open, Risk #46 resolved GCP sprawl audit)
- Gitleaks Guardian: 686 third-party findings audited → 0 risk confirmed, .gitleaksignore (668 fingerprints)
- CL4R1T4S: competitive intel archived, 6 adoptable patterns identified, source code (1,902 files) extracted
- Architecture docs: 7 specs + 229 Cor.Atlantis recovered docs
- Daemons: Dream consolidation (nightly) + Loop steward (5-min) — both tested
- Reference architectures: purged from disk (4.3GB freed), 29 repos documented in THIRD_PARTY_TAPESTRY.json
- CLAUDE.md: 4-layer hierarchy (global 13KB + user 4.8KB + project 5.3KB + 51 rules)
- MCP Fleet Vanguard: v11.0 (secrets_manager_doctrine, no inline routing tables)
- Model refs: all aiyou_stack purged from deprecated gemini-1.5/2.5 → gemini-3.1-flash-lite-preview
- Secrets doctrine: `secrets_manager_doctrine` replaces `env_master_doctrine` in GEMINI.md v9.5
- ANE NPU: ane_bridge.py scaffolded, libane_bridge.dylib exists in archive/third_party only (not compiled in-tree), INT8 benchmark UNVERIFIED
- ANE GGML: llama.cpp-ane compiled (GGML_ANE=ON), libggml-ane.dylib + llama-server at libs/cyberpunk_stack/llama.cpp-ane/build/bin/ (Apr 5), runtime benchmark UNVERIFIED
- Semantic Kernel: ShadowTagV4.Kernel .csproj exists (net11.0, SK 1.74.0), OnExternalEvent→OnInputEvent fix NOT applied to surviving Process.cs:144, SKEXP0080 suppressed, dotnet not in PATH
- Aegaeon Protocol: context_cache.py + swarm_router.py scaffolded (core/aegaeon/), no active slab (data/aegaeon/ empty), 90% discount available via implicit caching on Gemini 2.5+ models
- Sovereign MLX: kv_cache_slab.py scaffolded (core/sovereign_mlx/), slab_prompt.txt exists (26KB corpus), no kv_cache_slab.bin built
- Intelligence Pipeline: 9 scripts (domain_tagger → github_sync), retriever.py LanceDB search wired
- Drive Ingest: 2,860 docs extracted, 897 vectorized to data/lancedb/workspace_knowledge
- Zero CPU Router: 4-tier dispatch cascade (ANE→Metal/MLX→Vertex AI), vulture fixes applied
- KAIROS Daemon: datetime.UTC→datetime.timezone.utc fix, --once test passes
- .venv: CPython 3.14.3 + mlx + litellm 1.83.7 + lancedb 0.30.2 + scipy 1.17.1 + numpy 2.4.3
- Cor.Autoresearch: Karpathy evidence-based ML loop (val_bpb metric, 5-min budget, git reset on failure)
- Operator Invariants: v2 with full sovereign compute topology, Aegaeon protocol, intelligence pipeline state
- Governance Recovery: 7 packages from Claude mono-fresh (control/pnkln/governance, core/governance, core/zt1, core/lawtrack, src/lawtrack, infra/migrations, apps/lawtrack-ui)
- Judge6 Engine: judge6_core + judge_architecture + judge6_factory (2,057 LOC governance control plane)
- RKILL Protocol: rkill.py + judge6_rkill_bridge.py + rkill_daemon.py (circuit breaker against hallucination)
- SilentDetector: silent_detector.py (secret/credential leak detection in AI outputs)
- ZT1 Deadlines: frcp_calculator.py + test_frcp_calculator.py (FRCP Rule 6 date calculator)
- LawTrack: core/lawtrack (schema + API + services) + src/lawtrack (enforcement + rules_database + timeline_engine) — 1,305 LOC
- 50-State Holidays: infra/migrations/003_jurisdiction_holidays_50_states.sql (339 LOC, all 50 state judicial holidays)
- LawTrack UI: apps/lawtrack-ui (React + Vite + TypeScript case dashboard)
- Ruff: 62,221 unsafe-fixes applied (v9.6), tools/ excluded in pyproject.toml, 830 remaining (non-critical style)
- Vulture: 0 findings at 90%+ confidence across recovered Python
- Tests: 10 passed (test_judge6.py — 10/10, test_dispatch_compute.py — 5/5)
- CI/CD: 10x_vibe_matrix.yml (4-phase: Gitleaks → ruff+vulture+biome → UI audit → auto-commit)
- GCP Cleanup: 9 APIs disabled, 3 Cloud Run deleted, 5 secrets purged (2026-04-20)
- Veo 3.1 Pipeline: veo_pipeline.py operational (6 presets, Veo 3.1/3.1-Fast/3.1-Lite/3.0/2.0), google-genai SDK 1.66.0+, GCS bucket gs://shadowtag-omega-v4-media, frame extraction via ffmpeg 8.1
- Video Compression: 52MB → 20MB kovelai (10 videos), 19MB → 8.8MB shadowtagai (7 videos), CRF 30, H.264, faststart
- Branded Billboards: KovelAI (cyan neon) + ShadowTag AI (magenta neon) composited onto hero-drift via ffmpeg overlay
- Billboard Assets: kovelai-billboard.png, shadowtag-billboard.png, og-billboard-branded.png, promo-screenshot.png
- Firebase Preview Channels: kovelai--staging (7d TTL)
- Security Headers: CSP + HSTS (preload) + XFO (DENY) + CORP + COOP + Permissions-Policy — all 8 verified live
- Multi-site Deploy: kovelai.web.app + shadowtagai.web.app + shadowtag-omega-v4.web.app — all 3 live (2026-04-20)
- Launchd Daemons: com.pnkln.kairos (5-min) + com.pnkln.dream-consolidation (nightly 03:00) — loaded via launchctl
- LanceDB Retriever Bridge: retriever_lancedb.py (local-first RAG, Vertex AI fallback, hybrid search)
- Ruff Unsafe Fixes: 1 hidden fix applied (995→994 remaining, all in tools/mcp-toolbox third-party)
- Gitleaks Production Sweep: 173 findings (all in docs/CANONICALIZATION_REPORT — third-party token samples, not real secrets)
- Staging Channel: kovelai--staging-zjaqs7fe.web.app (7d TTL, deployed 2026-04-20)
- Cloud Run Health: CounselConduit 200 OK, Stripe webhook endpoint LIVE (400 on invalid payload = correct)

- Gemma-4 31B Sovereign: gemma-4-31B-it-Q4_K_M.gguf (17GB) at ~/models/, served via llama-server (ANE build) on 127.0.0.1:8080, OpenAI-compat API, thinking mode active, inference verified (2026-04-20)
- GEPA Router: dspy_gepa_router.py (118 LOC) at tools/orchestrator/, sidekick :8080 + auditor :8081 endpoints configured
- Nested .git purge: 30 dirs removed from external_repos/ (was 30 → 0), verified clean (2026-04-20)
- .env quarantine: 5 Kosmos test configs untracked from git index, *.env in .gitignore
- Vulture whitelist: vulture_whitelist.py added (NotebookLM dynamic import false positive)
- Dead code sweep: 10 vulture findings fixed (judge_architecture.py, fabric.py, judge_six_pipeline.py, governance_tools.py)

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Monorepo-Uphillsnowball** (455599 symbols, 701179 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

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
