# Shadowtag Toolbelt: Native & Connected

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
