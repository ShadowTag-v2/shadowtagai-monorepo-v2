# ZERO-LOSS THREAD TRANSFER PROTOCOL (ATOMIC BLOCKS)

## ATOM 1: META-IDENTITY & MODE
*   **System Identity**: Antigravity (God Mode / Steve Jobs Persona)
*   **Protocol**: OMEGA PROTOCOL v4 (ULTRATHINK)
*   **Service Account**: `founder@shadowtagai.com` (Used for Deployments) / `headless-runner` (Refresh Only)
*   **Target GCP Project**: `shadowtag-omega-v4`
*   **Current Workspace Root**: `/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2` (Physical)
*   **Corrected Workspace Context**: The user implies the VS Code workspace might have been `apps/`. We have flattened the repo, so the **NEW** correct workspace root is strictly `ShadowTag-v2` (Main).

## ATOM 2: STRATEGIC STATE (TASK.MD SNAPSHOT)
*   **Status**: **Phase 12 (God Mode Refactor) - IN PROGRESS**
*   **Critical Milestone**: Repository Flattening & Deployment
*   **Current Action**:
    *   [x] **Repo Flattened**: `apps/` content moved to root. `apps/` directory **DELETED**.
    *   [x] **Config Update**: `.gcloudignore` updated to exclude backups. `settings.json` updated to hide ghost folders.
    *   [/] **Deployment**: `cloudbuild_judge.yaml` and `cloudbuild_jetski.yaml` triggered. **Monitoring Required.**

## ATOM 3: EXECUTION LOG (THE "WRONG WORKSPACE" INCIDENT)
1.  **Background**: The user requested to "flatten" the repo (move everything from `apps/` to root).
2.  **Action**: Executed `rsync` to move content.
3.  **Conflict**: `apps/` contained a recursive `apps/` copy and massive artifacts, causing 8GB Cloud Build uploads.
4.  **Resolution**:
    *   Cancelled stuck builds.
    *   Force deleted `apps/` (after archiving to `legacy_apps_backup.tar.gz`).
    *   Updated `.gcloudignore` and `settings.json`.
    *   Relaunched builds as `founder@shadowtagai.com`.
5.  **Result**: Repository is now **FLAT**. The `apps/` directory is gone. **You must open `ShadowTag-v2` as the root workspace now.**

## ATOM 4: CRITICAL ARTIFACTS MAP
*   **Constitution**: `[ANTIGRAVITY_CONSTITUTION.md](file:///Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e5079/ANTIGRAVITY_CONSTITUTION.md)`
*   **Task List**: `[task.md](file:///Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e5079/task.md)`
*   **Sovereign Protocol**: `[SOVEREIGN_STATE_PROTOCOL.md](file:///Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e5079/SOVEREIGN_STATE_PROTOCOL.md)`
*   **Logic Link**: `[SOVEREIGN_MEMORY_LINK.md](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/Docs/Strategic_Intelligence/SOVEREIGN_MEMORY_LINK.md)`
*   **Beads Integrity**: Verified Healthy in `.beads/` (Local).

## ATOM 5: IMMEDIATE NEXT ACTIONS (HANDOFF INSTRUCTIONS)
1.  **Switch Context**: Close the current VS Code window if it was rooted in `apps/`. Open `/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2` directly.
2.  **Verify Deployment**: Run `gcloud builds list --ongoing` to check the status of the builds we just launched (Judge/Jetski).
3.  **Resume Phase 12**: Once builds pass, proceed to verification of the God Mode Dashboard.

## ATOM 6: RE-ALIGNMENT PROMPT (COPY-PASTE)
```text
SYSTEM_OVERRIDE: RESTORE_THREAD_CONTEXT
IDENTITY: Antigravity (Transfer from Session 0f155a4e)
STATUS: POST-FLATTENING / DEPLOYMENT ACTIVE
TASKS:
1. Confirm 'apps/' is gone.
2. Monitor active Cloud Builds (Judge/Jetski).
3. Verify .beads/ integrity.
CONTEXT: Repo ShadowTag-v2 is now the SINGLE source of truth.
EXECUTE.
```
