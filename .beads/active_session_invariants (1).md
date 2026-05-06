# Active Session Invariants — LOCKED until MEMORY UNLOCK

## Pre-Action Memory Gate — Mirror Verbatim Before ANY Repo-Wide Action

### Canonical Truth Hierarchy
1. `AGENTS.md` is the canonical behavioral contract.
2. `CLAUDE.md` is a thin shim (pointer only).
3. `monorepo_manifest.yaml` is workspace truth.
4. `antigravity-mcp-config.json` is MCP truth.
5. `BUSINESS_CONTEXT_LOCKED.md` is pricing and architecture truth.
6. `RISK_REGISTER.md` is operational risk truth.

### MCP Server Mandate (Non-Negotiable)
- All 5 MCP servers MUST be used: **Firebase**, **Chrome DevTools**, **Stitch**, **Developer Knowledge**, **Sequential Thinking**.
- If an operation CAN be performed by an MCP server, it MUST be. No terminal fallbacks for MCP-capable operations.
- Anti-patterns PROHIBITED:
  - `search_web` for Google API docs → use `google-developer-knowledge` MCP
  - `firebase deploy` in terminal → use `firebase-mcp-server` MCP
  - Screenshots with external tools → use `chrome-devtools-mcp` MCP
  - Hand-coding design tokens → use `StitchMCP`
  - Ad-hoc reasoning lists → use `sequential-thinking` MCP

### Capability Resolution
- `GEMINI.md` defines operator invariants, NOT capability ownership or routing.
- Capability ownership, precedence, conflict denial, and fallback behavior live ONLY in `antigravity-mcp-config.json`.

### Firebase MCP Deployment Doctrine
- Deploy = MCP **Prompt** (`firebase://guides/init/hosting`), NOT a Tool.
- Terminal CLI does NOT inherit MCP server credentials.
- Auth refresh: `npx -y firebase-tools@latest login --reauth`

### Secrets Doctrine
- Production: GCP Secret Manager ONLY (`valueFrom.secretKeyRef`).
- Local dev: `.env` (gitignored, kernel-locked `chflags uchg`).
- Google services use ADC (no API keys).
- NEVER: hardcoded keys, secrets in logs/chat/frontend/MCP inline args.

### GitHub Doctrine
- SSH (`git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git`) is MANDATORY transport.
- GitHub App PEM is the ONLY auth path (App ID 3018200).
- NEVER: `gh auth login`, PATs, deploy keys, macOS Keychain.

### Prompt Repetition Doctrine
- Apply to non-reasoning tiers ONLY (Oracle Studio, model_router, Vent Mode, Autoresearch Triad).
- Do NOT apply to reasoning/thinking models.

### Execution State Machine
- **STATE A (Pure YOLO)**: repetitive UI, standard logic, known patterns, web research, pip/npm installs, git fetch/pull.
- **STATE B (Clutch)**: git history rewrites, force-pushes, database migrations, auth/payment changes, architecture shifts >3 packages.

### Nag Protocol
- End every response with EXACTLY 22 actionable prompts until thread is fully resolved.

### Rich Hickey Vulture Doctrine
- Step 0 of any refactor = DELETION. Run `vulture` and `ruff --fix` together.
- Simple Made Easy. Unentangled > Familiar.
- Google Cloud Tasks is the EXCLUSIVE queue broker. BullMQ is banned.

### Hardened State Reference
- GEMINI.md v9.5 | AGENTS.md v9.5 | monorepo_manifest v1
- Tests: 101 passed, 5 E2E skipped
- Firestore: 2 databases | Security rules: zero-trust
- Cloud Functions: captureLead v2
- Hosting: 3 targets (kovelai, shadowtagai, default-site)
- CounselConduit: v3.1.0 on Cloud Run (33 API modules)
- Lighthouse: P93+/A93+/BP100/SEO100
- SOVEREIGN_GOLD_MASTER tag: active

## Session Lock
- **Status**: LOCKED
- **Unlock**: User must say "MEMORY UNLOCK"
- **Created**: 2026-04-18T23:40:01-07:00
- **Session**: 60bdfcfd-1afb-43b2-bf64-2065030ed3ec
