# TRANSFER PACKET: SHADOWTAG OMEGA v4 (Model Identity Resolved)

> **TIMESTAMP:** 2026-02-08 11:15 PST
> **STATUS:** CRITICAL HANDOVER - DEPLOYMENT PENDING
> **AGENT:** Antigravity (Session 2892)

## 🚨 IMMEDIATE ACTION REQUIRED
1.  **RESUME DEPLOYMENT:** The build `6a857e13-6e76-4da1-bf66-7b843cadef73` was launched to deploy `gemini-3-flash-preview`.
    - **Check Status:** `gcloud builds describe 6a857e13-6e76-4da1-bf66-7b843cadef73`
    - **If Failed/Canceled:** Run `gcloud builds submit apps/judge-sentinel --tag ...` AGAIN.
2.  **VERIFY ENDPOINT:** Once deployed, `curl` `https://judge-sentinel-767252945109.us-central1.run.app/api/v1/generate-deck`.
    - **Expected:** 200 OK (or at least a Gemini Response, not a 404 Publisher Error).

## 🌐 WEBSITE (FRONTEND) ROLLUP
- **Proxy Endpoint:** `app/api/proxy/generate-deck/route.ts` implemented to bridge Frontend -> Cloud Run Backend securely.
- **Component:** `DeckViewer.tsx` implemented and integrated.
- **Status:** Code is LOCAL/COMMITTED but likely **NEEDS REDEPLOY** to `shadowtag-web` Cloud Run service to pick up the new Proxy logic.
- **Action:** `gcloud builds submit apps/shadowtag-web ...`

## 🧠 INTELLIGENCE UPDATE (The "Flash" Confusion)
We spent this session debugging `404 Publisher Model Not Found` errors.
- **TRIED:** `gemini-1.5-flash` (Generic) -> Failed (Mapped to `002`).
- **TRIED:** `gemini-1.5-flash-001` (Strict) -> Failed (404, Permission/Region issue).
- **TRIED:** `gemini-3.0-flash-001` (Guess) -> Failed (404, Invalid ID).
- **SOLVED:** Used Browser to Model Garden.
    - **CORRECT ID:** **`gemini-3-flash-preview`**
    - **BACKUP ID:** `gemini-2.0-flash-001`

**Codebase is now updated to use `gemini-3-flash-preview`.**

## 📜 NEW MANDATE: Developer Knowledge API
The User has mandated the use of the **Developer Knowledge API** for all future Google documentation queries.
- **See `GEMINI.md`** for the updated protocol.
- **Phase 13** is dedicated to implementing this.

## 📂 ARTIFACTS STATE
- `GEMINI.md`: **UPDATED** (Source of Truth).
- `task.md`: **UPDATED** (Phase 12 In Progress).
- `judge-sentinel`: **CODE FIXED** (Pending Deploy).

**"The Nervous System is wired, we just need to flip the switch."**
