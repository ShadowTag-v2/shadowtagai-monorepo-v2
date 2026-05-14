# Shadowtag Toolbelt: Native & Connected

## 0. AGENT PROTOCOL: SHELL ACCESS & CAPABILITIES
- **Directive:** You have **UNFETTERED DIRECTORY ACCESS** across all workflows and the entire repo.
- **Session Init:** Execute `/omega-loop` at the beginning of each session, as well as: `@.agent/workflows/live-engine.md`, `@.agent/docs/toolbelt.md`, `@.agent/rules/shadowtag-laws.md`.

## Automation Restored:
1. `gcloud_auth_solver.py`: Ready (Jetski/Browser).
2. `omega_auth_daemon.py`: RUNNING (PID: Active).
3. `BRAIN_DIR="/Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e50"`
5. Ensure you are saving everything to beads as you go.

## 1. Native Cloud Interactions (Keyless)

**Strategy:** Rely on the IDE Sidebar. Do NOT run `gcloud config set`.

- **Status Check:** Look at the "Cloud Code" status bar indicator.
- **Native Curl (Uses Sidebar Auth):**
  `curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" <url>`

## 2. AiYou RAG — Sovereign Knowledge Base

**API base:** `$VITE_API_URL` (default `http://localhost:8000`)
**MCP config:** `.mcp.json` at repo root (tools: `aiyou_query`, `aiyou_ingest`)

### Query (semantic RAG)
```bash
curl -s -X POST "$VITE_API_URL/api/v1/aiyou/agent/query" \
  -H "Content-Type: application/json" \
  -d '{"q": "<your question>"}' | jq .
```

### Ingest a document chunk
```bash
# Run the full ingest pipeline (scans 5 source dirs, Gemini text-embedding-004 + fallback):
cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
npx ts-node packages/aiyou/src/scripts/ingest.ts [optional-extra-dir]
```

### Memory report
```
docs/Strategic_Intelligence/SOVEREIGN_MEMORY_LINK.md  ← 118 conversations, 32 snapshots
```

### Embedding source
- **Primary:** Gemini `text-embedding-004` via Vertex AI ADC (`gcloud auth print-access-token`)
- **Fallback:** Deterministic hash-seeded 768-dim vector (no API required, zero-drift)

## 3. External Resources

- **Web:** `web_search` is authorized.
- **Google Drive (API Access Pattern):**
  _If user asks for Drive data or context is missing, write and run this script:_
  ```python
  # drive_fetcher.py
  from googleapiclient.discovery import build
  from google.oauth2 import service_account
  # Use ADC (Application Default Credentials) provided by Cloud Code
  # SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
  # ... (Agent: Auto-complete this to fetch the requested Doc ID)
  ```
