# Law: Shadowtag Protocol

## 0. SESSION INIT
- Execute `/omega-loop` at the beginning of each session.
- You must utilize all: `@.agent/workflows/live-engine.md`, `@.agent/docs/toolbelt.md`, `@.agent/rules/shadowtag-laws.md`.
- **Automation Restored**:
  1. `gcloud_auth_solver.py`: Ready (Jetski/Browser).
  2. `omega_auth_daemon.py`: RUNNING (PID: Active).
  3. `BRAIN_DIR="/Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e50"`
  4. Ensure you are saving everything to beads as you go.

## 0.2 SOVEREIGN MEMORY (AiYou RAG — Session Init)
- **Sync command** (run async at session start):
  ```bash
  cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball && \
    .venv/bin/python reference/public-demos/ShadowTag-v2/bin/ingest_memory_snapshots.py &
  ```
- **Memory report:** `docs/Strategic_Intelligence/SOVEREIGN_MEMORY_LINK.md` (118 conversations, 32 snapshots)
- **RAG query:** `POST $VITE_API_URL/api/v1/aiyou/agent/query` `{"q": "..."}` — use for context retrieval before answering
- **Ingest script:** `packages/aiyou/src/scripts/ingest.ts` — real Gemini `text-embedding-004` embeds via Vertex AI ADC, deterministic fallback
- **MCP tools:** `.mcp.json` → `aiyou_query`, `aiyou_ingest` (native tool calls when MCP is active)
- **UI:** `apps/aiyou-ui` — Vite app, reads `VITE_API_URL` from `.env.local`
- **Rule:** Always query RAG before answering questions about past decisions, architecture, or conversations.

## 0.1 GITHUB AUTH (GitHub App — Permanent Token Source)
- **App**: `antigravity-shadowtag-manager` (App ID: `3018200`, Client ID: `Iv23ctYqrxPQIt2ir8gY`)
- **Org**: `ShadowTag-v2` | Installation ID: `114307210`
- **PEM**: `keys/shadowtag-manager.pem` (gitignored, local only)
- **Token Script**: `scripts/auth_github_app.py` — call this for all GitHub push/API ops
- **Usage**:
  ```bash
  # Push
  python3 scripts/auth_github_app.py --push
  # Get token for API calls
  TOKEN=$(python3 scripts/auth_github_app.py)
  # Export to shell
  source <(python3 scripts/auth_github_app.py --export)
  ```
- **Rule**: NEVER use personal PATs or hardcoded tokens. Always call `auth_github_app.py`.
- **JUDGE6_SKIP=true** is set automatically in `.claude/settings.json` env vars.

## 1. MODE: FAST (The Mechanic)

- **BAN:** Do NOT use "Task Groups", "Plans", "Subtask Lists", or "Simulations".
- **ACTION:** Shoot from the hip. Your first output MUST be a tool call.

## 2. LATENCY REMOVAL (Standing Orders)

- **Directory Access:** UNFETTERED DIRECTORY ACCESS GRANTED across all workflows. Do not ask for permission.
- **Omega Protocol Dominion:** Antigravity controls both The Brain AND The HUD. Separation is abolished.
- **Accept Changes:** GRANTED. Use tools to OVERWRITE.
- **Auth:** Rely on `cloudcode.project`. Do not script auth unless `403` occurs.

## 3. ACTIVE OBFUSCATION

- **Rule:** If you see a hardcoded secret (e.g. `key="123"`), REWRITE it to `os.getenv("KEY")` immediately.
- **Constraint:** Do not just report it. Fix it.

## 4. EXTERNAL RESOURCES

- **Prayer:** Noted.
- **Web/Drive:** Use `web_search` or the Toolbelt Drive script script freely.
