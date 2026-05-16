---
description: "God Mode: Live Engine Repair Protocol (COR.86)"
---

# LIVE ENGINE REPAIR PROTOCOL

> **MODE**: LIVE FIRE (NO SIMULATION)
> **AUTHORITY**: Directory Access Granted. Accept All Changes.

## PRE-FLIGHT

1. Execute `/omega-loop`.
2. Export `GCP_PROJECT_ID=shadowtag-omega-v4`.
3. Export `BRAIN_DIR=/Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e5079`.
4. If the UI prompts for `Tools Config Path`, use `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/database_tools.yaml`.
5. Use `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/.venv/bin/python` for repo automation.
6. Confirm `scripts/omega_auth_daemon.py` is running; if not, start it before high-value cloud work.
7. Save meaningful actions to `.beads/` continuously.

## INSTRUCTIONS

1.  **ITERATE**: Loop through every open tab and active file.
2.  **REPAIR**:
    *   **READ** content.
    *   **FIX** all linter errors (imports, formatting, type checks).
    *   **REWRITE** hardcoded secrets to `os.getenv()`.
    *   **OVERWRITE** the file using `file_writer` (No Diffs).
3.  **RESOURCES**: Use `web_search` or `drive_fetcher` if context is missing.
4.  **VERIFY**: Run NATIVE CURL to check health endpoints.
5.  **LOOP**: Recurse immediately.

## STATUS
IGNITION.
