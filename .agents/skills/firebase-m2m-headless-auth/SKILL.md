---
name: Firebase M2M Headless Auth
description: >
  Eliminates interactive `firebase login` browser OAuth for agent operations.
  Firebase CLI authenticates headlessly via GOOGLE_APPLICATION_CREDENTIALS
  pointing to a Service Account JSON key pulled from GCP Secret Manager.
version: 1.0.0
status: MANDATORY
---

# Firebase M2M Headless Auth

## Problem

Interactive `firebase login` triggers a browser OAuth flow that traps agent
terminals in PTY buffer loops. The agent cannot complete the flow autonomously.

## Solution

Service Account (SA) key-based authentication via `GOOGLE_APPLICATION_CREDENTIALS`.
Zero browser interaction required.

## Canonical Credentials

- **SA Email**: `$FIREBASE_DEPLOYER_SA` (see `scripts/load_mcp_secrets.sh`)
- **IAM Role**: `roles/firebase.admin`
- **Secret Manager Key**: `firebase-deployer-sa-key`
- **Local Path**: `.beads/firebase-sa.json` (gitignored)

## Usage

```bash
# Pull key from Secret Manager (run once per workstation)
gcloud secrets versions access latest \
  --secret=firebase-deployer-sa-key \
  --project=shadowtag-omega-v4 > .beads/firebase-sa.json

# Set env and run any Firebase CLI command headlessly
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/.beads/firebase-sa.json"
CI=true firebase deploy --only hosting --project=shadowtag-omega-v4
```

## Mandatory Rules

1. **NEVER** use `firebase login` in agent terminals
2. **ALWAYS** prefix Firebase CLI commands with `CI=true`
3. **ALWAYS** set `GOOGLE_APPLICATION_CREDENTIALS` before any Firebase CLI call
4. `.beads/firebase-sa.json` MUST be gitignored (already is)
5. SA key rotated via Secret Manager — NEVER hardcode

## Prohibited

- `firebase login` (interactive OAuth)
- `firebase login:ci` (deprecated)
- `npx firebase-tools login` (ephemeral cache, token lost)
- Storing SA key outside `.beads/` or Secret Manager
