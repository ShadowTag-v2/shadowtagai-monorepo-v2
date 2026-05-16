# AGENTS.md — v11.6 Sovereign Hardened State (2026-05-15)

## Core Technical Truths
1. **Canonical Repo**: `git@github.com:ShadowTag-v2/shadowtagai-monorepo-v2.git` (sovereign primary)
2. **Archived**: `Monorepo-Uphillsnowball` — READ-ONLY. **NEVER push.**
3. **Local Workspace**: `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball`
4. **Fleet Governance**: `docs/SYSTEM_OVERRIDE.md` V26.3 — Dual-Plane Fleet (6 Plane 1 + 13 Plane 2 = 19 servers, 91 Plane 1 tools, 9 headroom)
5. **Lint Delegation**: `gca_autolint_daemon.py` (TACSOP 5). Manual linter invocation **prohibited**.
6. Cloud Run: MUST use `try/except ImportError` for `uuid7` fallback.
7. .NET 11.0.100-preview.3 INSTALLED. SK 1.74.0. `OnExternalEvent` is correct SK Process.Core API. **AiYou.Kernel csproj removed from active tree** (GitNexus test fixtures only).
8. Semantic Kernel Process.cs: `OnExternalEvent` is CORRECT for v1.21.0-alpha.
9. **Runtimes**: Python 3.14.5 (py313), Node v26.0.0, .NET 11.0.100-preview.3, Bun 1.3.14.
10. We maintain 247 active skills (54 workspace + 210 global − 17 overlap).
11. **Prompt Repetition (arXiv 2512.14982):** Applies ONLY to non-reasoning tiers to boost accuracy.
12. **GitHub Auth**: App PEM exclusive (ID 3018200). SSH primary transport. No PATs, no `gh auth login`.
13. **Credential Hygiene**: Maps API key migrated to `${GOOGLE_DESIGN_API_KEY}` env ref. Phantom `gemini-github-mcp` removed from Cline. `gemini-web-fetcher` migrated to uvx (Plane 2). Chrome CrUX key is upstream vendor code (allowlisted).
14. **Lint V26.3 Pass**: 2,836 violations fixed (142 I001, 754 T201, 1896 D400/D415, 44 F401/F841). Stale `pyproject.toml` [tool.ruff] removed (line-length 100→150 conflict).
15. **ShadowTag OS**: Architecture documented in `packages/shadowtag_os/DESIGN.md`. 6 subsystems: CoreOrchestrator, KernelChainAdapter, GateAdapter (45 keyword blocklist), JudgeAdapter, ZxRunner, SkillsBridge. 33/33 tests green. 64% coverage (core 96%, gates 90%, kernels 95%).
