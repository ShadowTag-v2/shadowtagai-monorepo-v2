# Antigravity Memory Lock Pack

This pack gives Antigravity a fail-closed startup path when chat context gets thin.

## Included files

- `memory_lock.json`
- `scripts/check_memory_lock.sh`
- `scripts/startup_relock.sh`
- `scripts/audit_truth_surfaces.sh`

## What it enforces

- One canonical workspace root
- One canonical project
- One canonical model family
- One canonical MCP truth file
- Product/lab split preserved
- Forbidden stale phrases blocked

## Important deletion enforced

This pack explicitly forbids and scans for the following string:

`Service Accounts: headless-runner@shadowtag-omega-v4.iam.gserviceaccount.com is now REFRESHING at the start of every tool call. This is this service account’s only function!`

That phrase is not included in any operational script except as a forbidden-string detector.

## Install

Copy the files into the monorepo root, then run:

```bash
chmod +x scripts/check_memory_lock.sh scripts/startup_relock.sh scripts/audit_truth_surfaces.sh
scripts/startup_relock.sh
```

## Confirmatory success response

```text
MEMORY STATUS: LOCKED
NEXT ACTION: Ready for Stage 3 canonicalization and repo-drift audit.
```

## Fail-closed response

```text
MEMORY STATUS: DRIFTED
Reason: ...
Action: Stopping immediately. Requesting re-lock.
```
