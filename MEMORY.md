# MEMORY.md — Workspace Session Index

> Read-only quick-reference index. Max 150 chars per line. Updated by KAIROS nightly.

## Active Project
- `shadowtag-omega-v4` — GCP project, Cloud Run + Firestore + Cloud Tasks

## Products
- `kovelai` → `apps/kovelai` — Firebase Hosting (kovelai.web.app)
- `counselconduit` → `apps/counselconduit` — Cloud Run v3.2.0 LIVE, 23 modules
- `uphillsnowball` → `labs/uphillsnowball` — R&D engine, Apple Silicon local

## Key Scripts
- `scripts/kairos_daemon.py` — Background agent controller (KAIROS)
- `scripts/dream_consolidation.py` — 4-phase KI maintenance (nightly)
- `scripts/loop_steward.py` — Autonomous task continuation (5-min)
- `scripts/load_mcp_secrets.sh` — Secret Manager env injection

## Key Tools
- `tools/intelligence_router.py` — IPI quarantine → NotebookLM pipeline
- `tools/session_logger.py` — Append-only JSONL audit trail

## Key Libs
- `libs/secret_manager_helper.py` — GCP Secret Manager wrapper + cache

## Canonical Docs
- `AGENTS.md` — Agent contract (canonical)
- `GEMINI.md` — Operator invariants (v10.3)
- `BUSINESS_CONTEXT_LOCKED.md` — Pricing + architecture truth
- `RISK_REGISTER.md` — Operational risk truth
- `monorepo_manifest.yaml` — Workspace structure truth
- `antigravity-mcp-config.json` — MCP routing truth

## Daemon Fleet
- KAIROS → background, health checks every 5 min
- Dream Consolidation → nightly orient/gather/consolidate/prune
- Loop Steward → 5-min idle scaling cycles
- pnkln-evolve → recursive self-improvement
- Omni-Autolint → daily 3-5AM lint+push

## Security Posture
- Cor.30 6-pillar framework enforced
- OWASP LLM Top 10 controls active
- Betterleaks pre-commit (secrets)
- AST-grep BullMQ ban enforced
- DLP circuit breaker active

## Auth Layers
- Firebase CLI → OAuth2 refresh token
- Firebase MCP → in-memory OAuth2 session
- ADC → gcloud application default credentials
- GitHub → SSH + App PEM JWT ($SHADOWTAG_PEM)

## Test Baseline
- Python 3.14.3 → 504 collected, 480 passed, 3 skipped
- pytest.ini v8.5 controls

- [2026-05-18T08:02:54.598Z] [SESSION_EVENT] Python environment initialized and Untitled-1.py created.

- [2026-05-18T17:46:47.746Z] [OPERATOR-INVARIANTS] 14-point Omni-Sync mandate acknowledged. On every iteration moving forward, use omni_epistemic_sync.ts to freeze state across the entire OS.

- [2026-05-18T17:46:52.423Z] [CONSTRAINT] If Antigravity provides a capability (Plane 1), Cline MUST NOT instantiate a local server for the same capability. Flutter development is handled natively by dart-mcp; a separate Flutter server is explicitly prohibited.
