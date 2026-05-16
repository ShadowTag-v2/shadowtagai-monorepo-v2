# AGENTS.md — v11.5 Sovereign Hardened State (2026-05-15)

## Core Technical Truths
1. **Canonical Repo**: `git@github.com:ShadowTag-v2/shadowtagai-monorepo-v2.git` (sovereign primary)
2. **Archived**: `Monorepo-Uphillsnowball` — READ-ONLY. **NEVER push.**
3. **Local Workspace**: `/Users/pikeymickey/.gemini/mono-fresh`
4. **Fleet Governance**: `docs/SYSTEM_OVERRIDE.md` V29 — Dual-Plane Fleet (7 Plane 1 + 14 Plane 2 = 21 servers, 99+ tools)
5. **Lint Delegation**: `gca_autolint_daemon.py` (TACSOP 5). Manual linter invocation **prohibited**.
6. Cloud Run: MUST use `try/except ImportError` for `uuid7` fallback.
7. .NET 11.0.100-preview.3 INSTALLED. SK 1.74.0. `OnExternalEvent` is correct SK Process.Core API. **AiYou.Kernel csproj removed from active tree** (GitNexus test fixtures only).
8. Semantic Kernel Process.cs: `OnExternalEvent` is CORRECT for v1.21.0-alpha.
9. **Runtimes**: Python 3.14.5 (py313), Node v26.0.0, .NET 11.0.100-preview.3, Bun 1.3.14.
10. We maintain 247 active skills (54 workspace + 210 global − 17 overlap).
11. **Prompt Repetition (arXiv 2512.14982):** Applies ONLY to non-reasoning tiers to boost accuracy.
12. **GitHub Auth**: App PEM exclusive (ID 3018200). SSH primary transport. No PATs, no `gh auth login`.
13. **Credential Hygiene**: Maps API key migrated to `${GOOGLE_MAPS_API_KEY}` env ref. Chrome CrUX key is upstream vendor code (allowlisted).
