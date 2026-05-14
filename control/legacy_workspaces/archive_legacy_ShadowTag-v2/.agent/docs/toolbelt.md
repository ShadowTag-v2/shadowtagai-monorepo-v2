# Shadowtag Toolbelt: Native & Connected

## 0. Session Boot
- Execute `/omega-loop` at the beginning of each session.
- If the UI prompts for `Tools Config Path`, paste `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/database_tools.yaml`.
- Export `GCP_PROJECT_ID=shadowtag-omega-v4`.
- Export `BRAIN_DIR=/Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e5079`.
- Prefer `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/.venv/bin/python` over global Python.
- Keep `scripts/omega_auth_daemon.py` running so the `headless-runner@shadowtag-omega-v4.iam.gserviceaccount.com` refresh loop stays active every 3 minutes.
- Persist meaningful work to Beads as you go via `.beads/` and `python3 scripts/bd.py`.

## 1. Native Cloud Interactions (Keyless)
**Strategy:** Rely on the IDE Sidebar. Do NOT run `gcloud config set`.
- **Status Check:** Look at the "Cloud Code" status bar indicator.
- **Native Curl (Uses Sidebar Auth):**
  `curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" <url>`

## 2. External Resources
- **Web:** `web_search` is authorized.
- **Google Drive (API Access Pattern):**
  *If user asks for Drive data or context is missing, write and run this script:*
  ```python
  # drive_fetcher.py
  from googleapiclient.discovery import build
  from google.oauth2 import service_account
  # Use ADC (Application Default Credentials) provided by Cloud Code
  # SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
  # ... (Agent: Auto-complete this to fetch the requested Doc ID)
  ```

## 3. Access Policy
- Non-workspace directory access is pre-approved for `/Users/pikeymickey/.gemini/antigravity`, `/Users/pikeymickey/aiyou-stack`, and `/Users/pikeymickey/Documents/GitHub`.
- If filesystem access needs a refresh, run `bash scripts/unfettered_access.sh`.
