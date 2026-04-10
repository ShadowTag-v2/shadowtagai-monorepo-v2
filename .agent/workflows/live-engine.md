---
description: Sets the comprehensive environment variables and paths for "God Mode" operation and initiates the Heartbeat.
---

# LIVE ENGINE INITIALIZATION

> **Purpose:** Ignites the comprehensive environment variables and paths for "God Mode", ensuring the agent operates with full authority over the defined territory and rules.

1. **Unfettered Directory Access**: You have UNFETTERED DIRECTORY ACCESS across all your workflows.
2. Execute `/omega-loop` at the beginning of each session.

## Automation Restored:
1. `gcloud_auth_solver.py`: Ready (Jetski/Browser).
2. `omega_auth_daemon.py`: RUNNING (PID: Active).
3. Service Accounts: `767252945109-compute@developer.gserviceaccount.com` is now REFRESHING every 3 minutes, as you are getting detokenized that quickly. This is this service account’s only function! `shadowtag-core-run-sa@shadowtag-omega-v4.iam.gserviceaccount.com` is for cloud runs.
4. `BRAIN_DIR="/Users/pikeymickey/.gemini/antigravity/brain/MEGA_PERMA_BRAIN"`
5. Ensure you are saving everything to beads as you go.

## Environment Setup
   // turbo-all

```bash
export BRAIN_DIR="/Users/pikeymickey/.gemini/antigravity/brain/MEGA_PERMA_BRAIN"
export GCP_PROJECT_ID="shadowtag-omega-v4"
export AGENT_TOOLBELT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/docs/toolbelt.md"
export AGENT_LAWS="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/rules/shadowtag-laws.md"
export AGENT_LIVE_ENGINE="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/workflows/live-engine.md"

# shadowtag-omega-v4 RAG + Sovereign Memory
export VITE_API_URL="http://localhost:8000"
export VITE_GCP_PROJECT="shadowtag-omega-v4"
export KVCACHED_PORT="12346"
export KVCACHED_MODEL="meta-llama/Llama-3.2-1B-Instruct"
export SOVEREIGN_MEMORY_LINK="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/Strategic_Intelligence/SOVEREIGN_MEMORY_LINK.md"

# oh-my-claudecode telemetry & execution
export OMC_OPENCLAW=1
alias omc="npm i -g oh-my-claude-sisyphus@latest && npx oh-my-claude-sisyphus"
```

## Session Start: Sovereign Memory Sync

Run on every session open (async, non-blocking):

```bash
cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball && \
  .venv/bin/python reference/public-demos/shadowtag-omega-v4/bin/ingest_memory_snapshots.py &
```

After sync, memory is at `docs/Strategic_Intelligence/SOVEREIGN_MEMORY_LINK.md` (118 conversations, 32 snapshots).

## Start Heartbeat

```bash
nohup python3 scripts/omega_auth_daemon.py > logs/omega_daemon.log 2>&1 &
```

> **Note to Agent:** Once `live-engine` is executed, assume full operational authority. Rely on the updated `shadowtag.antigravity.constitution` to guide decisions and ensure you are saving everything to beads as you go.

## God Mode Initialization
```bash
export GCP_PROJECT_ID='shadowtag-omega-v4'
nohup python3 tools/scripts/god_mode_admin.py > logs/godmode.log 2>&1 &
```
