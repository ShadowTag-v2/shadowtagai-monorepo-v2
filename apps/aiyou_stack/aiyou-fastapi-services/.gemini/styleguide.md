# Antigravity Coding Standards
## General
- **Tone:** Concise, professional, no fluff.
- **Language:** Python 3.13+ (Strict typing required).
- **Format:** Use 'ruff' for linting.

## Cloud Run Native
- **State:** Never store state locally. Use GCS or DB.
- **Port:** Always listen on 'PORT' env var (default 8080).
- **Logs:** Json-structured logging only (for Cloud Logging).

## Security
- **Auth:** Workload Identity Federation ONLY. No JSON keys.
